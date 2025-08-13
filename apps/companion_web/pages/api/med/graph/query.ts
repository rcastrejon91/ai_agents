import type { NextApiRequest, NextApiResponse } from "next";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE!
);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });
  const { question } = (req.body ?? {}) as { question?: string };
  if (!question) return res.status(400).json({ error: "Missing question" });

  const { data: anchors } = await supabase.rpc("kg_anchor_nodes", { p_query: question, p_k: 5 }).catch(() => ({ data: [] as any[] }));
  const anchorIds = (anchors ?? []).map((a: any) => a.id);

  const { data: edges } = await supabase
    .from("kg_edges")
    .select(
      "id, rel, confidence, src:kg_nodes!kg_edges_src_id_fkey(id,kind,name), dst:kg_nodes!kg_edges_dst_id_fkey(id,kind,name), evidence:kg_nodes!kg_edges_evidence_id_fkey(id,kind,name,source_url)"
    )
    .or(`src_id.in.(${anchorIds.join(",")}),dst_id.in.(${anchorIds.join(",")})`)
    .eq("status", "approved")
    .limit(200);

  const lines: string[] = [];
  for (const e of edges ?? []) {
    const ev = e.evidence?.source_url ? ` [evidence: ${e.evidence.source_url}]` : "";
    lines.push(`${e.src.kind}:${e.src.name} --${e.rel}(${e.confidence.toFixed(2)})--> ${e.dst.kind}:${e.dst.name}${ev}`);
  }
  if (!lines.length) return res.status(200).json({ abstain: true, reasons: ["No graph context found."] });

  const sys = "Answer strictly from the provided graph facts. If insufficient, say you cannot conclude.";
  const prompt = `Question: ${question}\n\nGraph facts:\n${lines.join("\n")}\n\nReturn concise answer with bullet points and include the specific edges you relied on.`;

  const r = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
    body: JSON.stringify({ model: "gpt-4o-mini", temperature: 0, messages: [{ role: "system", content: sys }, { role: "user", content: prompt }] }),
  });

  if (!r.ok) return res.status(502).json({ error: "Upstream error." });
  const j = await r.json();
  const answer = j.choices?.[0]?.message?.content?.trim();
  if (!answer) return res.status(200).json({ abstain: true, reasons: ["No answer generated."] });

  return res.status(200).json({ answer, edges: (edges ?? []).length });
}
