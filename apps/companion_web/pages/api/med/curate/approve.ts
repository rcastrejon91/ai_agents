import type { NextApiRequest, NextApiResponse } from "next";
import { sb, guard } from "./_supabase";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });
  if (!guard(req, res)) return;
  const { id } = req.body ?? {};
  if (!id) return res.status(400).json({ error: "Missing id" });

  const { error } = await sb.from("kg_edges").update({ status: "approved" }).eq("id", id);
  if (error) return res.status(500).json({ error: error.message });
  res.status(200).json({ ok: true });
}
