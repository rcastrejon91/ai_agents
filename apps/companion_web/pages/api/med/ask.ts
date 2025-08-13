import type { NextApiRequest, NextApiResponse } from "next";

type Doc = { id: string; title: string; url: string; snippet: string };
type MedAnswer = {
  answer?: string;
  citations?: { id: string; title: string; url: string }[];
  confidence?: number;
  abstain?: boolean;
  reasons?: string[];
};

const MIN_CONF = 0.72;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });
  const { question } = (req.body ?? {}) as { question?: string };
  if (!question) return res.status(400).json({ error: "Missing question" });

  // 1) Retrieve vetted evidence
  const docs: Doc[] = [
    ...(await searchPubMed(question)),
    ...(await searchClinicalTrials(question)),
    ...(await searchFDALabels(question)),
  ].slice(0, 8);

  if (!docs.length) {
    return res.status(200).json(<MedAnswer>{
      abstain: true,
      reasons: ["No high-quality evidence found for this query."],
    });
  }

  // 2) Ask the model to synthesize WITH citations only to provided docs
  const sys = [
    "You are Medical-Lyra. Use ONLY the provided evidence.",
    "Cite by index like [1], [2] that map to provided docs.",
    "If evidence is insufficient or conflicting, set abstain=true.",
    "NEVER guess. No creative speculation. No differential diagnoses beyond evidence.",
    "Return JSON with keys: answer, citations, confidence, abstain, reasons."
  ].join(" ");

  const context = docs
    .map((d, i) => `[${i + 1}] ${d.title}\n${d.snippet}\nURL: ${d.url}`)
    .join("\n\n");

  const resp = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: sys },
        { role: "user", content: `Question: ${question}\n\nEvidence:\n${context}\n\nReturn strict JSON.` },
      ],
      temperature: 0.0,
    }),
  });

  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    console.error("[med/ask] upstream", resp.status, text);
    return res.status(502).json({ error: "Upstream error." });
  }

  let parsed: MedAnswer | null = null;
  try {
    const j = await resp.json();
    parsed = JSON.parse(j.choices?.[0]?.message?.content || "{}");
  } catch (e) {
    console.error("[med/ask] parse", e);
  }

  // 3) Enforce abstention rule
  if (!parsed || parsed.abstain || (parsed.confidence ?? 0) < MIN_CONF) {
    return res.status(200).json(<MedAnswer>{
      abstain: true,
      reasons: parsed?.reasons ?? ["Low confidence."],
      citations: (parsed?.citations ?? []).slice(0, 4),
    });
  }

  // 4) Return answer with linked citations
  const citations = (parsed.citations ?? []).map((c, i) => ({
    idx: i + 1,
    title: c.title,
    url: c.url,
  }));

  return res.status(200).json({
    answer: parsed.answer,
    confidence: Math.min(1, Math.max(0, parsed.confidence ?? 0)),
    citations,
  });
}

/** -------- Retrieval helpers (free, no key needed) ---------- **/
async function searchPubMed(q: string): Promise<Doc[]> {
  // E-utilities: esearch + esummary
  const ids = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=5&retmode=json&term=${encodeURIComponent(q)}`
  )
    .then((r) => r.json())
    .then((j) => j.esearchresult?.idlist ?? [])
    .catch(() => []);
  const idStr = ids.join(",");
  if (!idStr) return [];
  const sum = await fetch(
    `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=${idStr}`
  )
    .then((r) => r.json())
    .catch(() => ({}));
  const result: Doc[] = [];
  for (const id of ids) {
    const it = sum.result?.[id];
    if (!it) continue;
    result.push({
      id,
      title: it.title,
      url: `https://pubmed.ncbi.nlm.nih.gov/${id}/`,
      snippet: `${it.title}. ${it.source ?? ""} ${it.pubdate ?? ""}`,
    });
  }
  return result;
}

async function searchClinicalTrials(q: string): Promise<Doc[]> {
  const url = `https://clinicaltrials.gov/api/query/study_fields?expr=${encodeURIComponent(q)}&fields=BriefTitle,NCTId,Condition,BriefSummary&min_rnk=1&max_rnk=5&fmt=json`;
  const j = await fetch(url)
    .then((r) => r.json())
    .catch(() => null);
  const rows = j?.StudyFieldsResponse?.StudyFields ?? [];
  return rows.map((r: any) => ({
    id: r.NCTId?.[0] ?? "",
    title: r.BriefTitle?.[0] ?? "Clinical trial",
    url: `https://clinicaltrials.gov/study/${r.NCTId?.[0] ?? ""}`,
    snippet: r.BriefSummary?.[0] ?? "",
  }));
}

async function searchFDALabels(q: string): Promise<Doc[]> {
  // OpenFDA drug labels
  const url = `https://api.fda.gov/drug/label.json?search=${encodeURIComponent(q)}&limit=3`;
  const j = await fetch(url)
    .then((r) => r.json())
    .catch(() => null);
  const results = j?.results ?? [];
  return results.map((r: any, i: number) => ({
    id: r.id ?? String(i),
    title: r.openfda?.brand_name?.[0] ?? "Drug label",
    url: `https://api.fda.gov/drug/label.json?search=id:${r.id}`,
    snippet: (r.indications_and_usage ?? r.description ?? [""])[0],
  }));
}
