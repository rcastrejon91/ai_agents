import type { NextApiRequest, NextApiResponse } from "next";
import { sb } from "../curate/_supabase";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (process.env.NODE_ENV !== "test" && req.headers.authorization !== `Bearer ${process.env.ADMIN_TOKEN}`) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  const { data: n1 } = await sb
    .from("kg_nodes")
    .insert({ kind: "Condition", name: "Asthma" })
    .select()
    .single();
  const { data: n2 } = await sb
    .from("kg_nodes")
    .insert({ kind: "Drug", name: "Albuterol" })
    .select()
    .single();
  const { data: n3 } = await sb
    .from("kg_nodes")
    .insert({ kind: "Paper", name: "Test RCT", source_url: "https://example.org/pmid-test" })
    .select()
    .single();
  await sb.from("kg_edges").insert({
    src_id: n2!.id,
    dst_id: n1!.id,
    rel: "treats",
    confidence: 0.95,
    evidence_id: n3!.id,
    status: "approved",
  });
  res.status(200).json({ ok: true });
}
