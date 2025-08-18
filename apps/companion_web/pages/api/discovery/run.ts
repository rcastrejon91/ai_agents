import type { NextApiRequest, NextApiResponse } from "next";

async function fetchOpenAlex(topic: string) {
  const url = `https://api.openalex.org/works?search=${encodeURIComponent(topic)}&per_page=5`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      console.error("OpenAlex API failed", { status: response.status });
      return [];
    }

    const data = await response.json();
    const hits = (data?.results || []).map((w: any) => ({
      title: w.title,
      year: w.publication_year,
      url: w.id,
      venue: w?.host_venue?.display_name,
    }));
    return hits;
  } catch (error) {
    console.error("OpenAlex fetch error:", error);
    return [];
  }
}

async function fetchClinicalTrials(topic: string) {
  const url = `https://clinicaltrials.gov/api/query/study_fields?expr=${encodeURIComponent(topic)}&fields=BriefTitle,NCTId,Condition,OverallStatus&min_rnk=1&max_rnk=5&fmt=json`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      console.error("ClinicalTrials API failed", { status: response.status });
      return [];
    }

    const data = await response.json();
    const studies = (data?.StudyFieldsResponse?.StudyFields || []).map((s: any) => ({
      nctid: s.NCTId?.[0],
      title: s.BriefTitle?.[0],
      status: s.OverallStatus?.[0],
    }));
    return studies;
  } catch (error) {
    console.error("ClinicalTrials fetch error:", error);
    return [];
  }
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  if (req.method !== "POST")
    return res.status(405).json({ error: "Method not allowed" });
  const { topic = "" } = req.body || {};
  if (!topic) return res.status(400).json({ error: "topic required" });

  let papers: any[] = [];
  let trials: any[] = [];
  await Promise.all([
    (async () => {
      try {
        papers = await fetchOpenAlex(topic);
      } catch (err) {
        console.error("OpenAlex fetch failed", err);
        papers = [];
      }
    })(),
    (async () => {
      try {
        trials = await fetchClinicalTrials(topic);
      } catch (err) {
        console.error("ClinicalTrials fetch failed", err);
        trials = [];
      }
    })(),
  ]);

  let summary = `Found ${papers.length} recent papers and ${trials.length} trials for “${topic}”.`;
  const key = process.env.OPENAI_API_KEY;
  if (key && papers.length + trials.length > 0) {
    try {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${key}`,
        },
        body: JSON.stringify({
          model: "gpt-4o-mini",
          messages: [
            {
              role: "system",
              content:
                "Summarize for clinicians in 5 bullets. Cite paper titles.",
            },
            { role: "user", content: JSON.stringify({ papers, trials }) },
          ],
          temperature: 0.2,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        summary = data?.choices?.[0]?.message?.content || summary;
      } else {
        console.error("OpenAI summarization failed", { status: response.status });
      }
    } catch (err) {
      console.error("Error calling OpenAI for summarization", err);
      /* keep fallback */
    }
  }

  return res.status(200).json({
    meta: { paper_count: papers.length, trial_count: trials.length },
    summary,
    papers,
    trials,
    disclaimer: "Educational summary. Not medical advice.",
  });
}
