import type { NextApiRequest, NextApiResponse } from "next";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE!
);

type NodeIn = {
  kind: string;
  name: string;
  canonical_id?: string;
  source_url?: string;
  embedding?: number[];
};
type EdgeIn = {
  src_key: string;
  dst_key: string;
  rel: string;
  evidence_key?: string;
  confidence: number;
  justification?: string;
  snippet?: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST")
    return res.status(405).json({ error: "Method not allowed" });
  const { nodes = [], edges = [] } = (req.body ?? {}) as {
    nodes: NodeIn[];
    edges: EdgeIn[];
  };

  const keyToId: Record<string, string> = {};
  for (let i = 0; i < nodes.length; i++) {
    const n = nodes[i];
    const { data, error } = await supabase.rpc("kg_upsert_node", {
      p_kind: n.kind,
      p_name: n.name,
      p_canonical_id: n.canonical_id ?? null,
      p_source_url: n.source_url ?? null,
      p_embedding: n.embedding ?? null,
    });
    if (error) return res.status(500).json({ error: error.message });
    keyToId[`n${i}`] = (data as any).id;
  }

  for (const e of edges) {
    const { data, error } = await supabase
      .from("kg_edges")
      .insert({
        src_id: keyToId[e.src_key],
        dst_id: keyToId[e.dst_key],
        rel: e.rel,
        evidence_id: e.evidence_key ? keyToId[e.evidence_key] : null,
        confidence: e.confidence,
      })
      .select("id")
      .single();
    if (error) return res.status(500).json({ error: error.message });

    await supabase.from("kg_assertions").insert({
      edge_id: (data as any).id,
      author: "pipeline:ingest",
      method: "RAG+LLM-extract",
      justification: e.justification ?? null,
      raw_snippet: e.snippet ?? null,
    });
  }

  return res.status(200).json({
    ok: true,
    nodes: Object.values(keyToId).length,
    edges: edges.length,
  });
}
