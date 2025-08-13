import type { NextApiRequest, NextApiResponse } from "next";
import { sb, guard } from "./_supabase";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });
  if (!guard(req, res)) return;

  const { data, error } = await sb.from("kg_edges_pending").select("*").limit(200);
  if (error) return res.status(500).json({ error: error.message });
  res.status(200).json({ items: data });
}
