// apps/companion_web/pages/api/med/graph/query.ts
import type { NextApiRequest, NextApiResponse } from "next";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { question } = (req.body ?? {}) as { question?: string };
  if (!question) return res.status(400).json({ error: "Missing question" });

  // 1) Get anchor nodes
  let anchors: any[] = [];
  try {
    const { data, error } = await supabase.rpc("kg_anchor_nodes", {
      p_query: question,
      p_k: 5,
    });
    if (error) throw error;
    anchors = data ?? [];
  } catch (err) {
    console.error('kg_anchor_nodes RPC failed', err);
    anchors = [];
  }

  const anchorIds = (anchors ?? []).map((a: any) => a.id);

  // 2) Get edges touching those anchors
  let edges: any[] = [];
  try {
    const { data, error } = await supabase
      .from("kg_edges_view")
      .select("*")
      .or(`src_id.in.(${anchorIds.join(",")}),dst_id.in.(${anchorIds.join(",")})`)
      .eq("status", "approved")
      .limit(200);
    if (error) throw error;
    edges = data ?? [];
  } catch (err) {
    console.error('kg_edges_view fetch failed', err);
    edges = [];
  }

  // 3) Format as brief lines Lyra can cite
  const lines: string[] = [];
  for (const e of edges as any[]) {
    const evSrc = e?.evidence?.source_url;
    const ev = evSrc ? `[evidence: ${evSrc}]` : "";
    lines.push(`${e.src.kind}:${e.src.name} --${e.rel}--> ${e.dst.kind}:${e.dst.name}${ev}`);
  }

  if (!lines.length) {
    return res.status(200).json({ abstain: true, reasons: ["No graph context found."] });
  }

  return res.status(200).json({
    graph_context: lines.slice(0, 50),
    anchors: anchors.slice(0, 20),
  });
}
