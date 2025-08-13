import type { NextApiRequest, NextApiResponse } from "next";
import { sb } from "../curate/_supabase";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (process.env.NODE_ENV !== "test" && req.headers.authorization !== `Bearer ${process.env.ADMIN_TOKEN}`) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  await sb.from("kg_edges").delete().neq("id", "00000000-0000-0000-0000-000000000000");
  await sb.from("kg_nodes").delete().neq("id", "00000000-0000-0000-0000-000000000000");
  res.status(200).json({ ok: true });
}
