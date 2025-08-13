import type { NextApiRequest, NextApiResponse } from "next";

// Free-first discovery: OpenAlex + ClinicalTrials.gov, summarized by OpenAI if key exists.
async function fetchOpenAlex(topic:string) {
  const url = `https://api.openalex.org/works?search=${encodeURIComponent(topic)}&per_page=5`;
  const r = await fetch(url); const j = await r.json();
  const hits = (j?.results||[]).map((w:any)=>({
    title: w.title, year: w.publication_year, url: w.id, venue: w?.host_venue?.display_name
  }));
  return hits;
}

async function fetchClinicalTrials(topic:string) {
  const url = `https://clinicaltrials.gov/api/query/study_fields?expr=${encodeURIComponent(topic)}&fields=BriefTitle,NCTId,Condition,OverallStatus&min_rnk=1&max_rnk=5&fmt=json`;
  const r = await fetch(url); const j = await r.json();
  const studies = (j?.StudyFieldsResponse?.StudyFields||[]).map((s:any)=>({
    nctid: s.NCTId?.[0], title: s.BriefTitle?.[0], status: s.OverallStatus?.[0]
  }));
  return studies;
}

export default async function handler(req:NextApiRequest, res:NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({ error:"Method not allowed" });
  const { topic = "" } = req.body || {};
  if (!topic) return res.status(400).json({ error:"topic required" });

  const [papers, trials] = await Promise.all([
    fetchOpenAlex(topic).catch(()=>[]),
    fetchClinicalTrials(topic).catch(()=>[]),
  ]);

  let summary = `Found ${papers.length} recent papers and ${trials.length} trials for “${topic}”.`;
  const key = process.env.OPENAI_API_KEY;
  if (key && papers.length + trials.length > 0) {
    try {
      const r = await fetch("https://api.openai.com/v1/chat/completions", {
        method:"POST",
        headers:{ "Content-Type":"application/json", "Authorization":`Bearer ${key}` },
        body: JSON.stringify({
          model:"gpt-4o-mini",
          messages:[
            { role:"system", content:"Summarize for clinicians in 5 bullets. Cite paper titles." },
            { role:"user", content: JSON.stringify({ papers, trials }) }
          ],
          temperature: 0.2
        })
      });
      const j = await r.json();
      summary = j?.choices?.[0]?.message?.content || summary;
    } catch { /* keep fallback */ }
  }

  return res.status(200).json({
    meta: { paper_count: papers.length, trial_count: trials.length },
    summary,
    papers, trials,
    disclaimer: "Educational summary. Not medical advice."
  });
}
