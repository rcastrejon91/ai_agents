import type { NextApiRequest, NextApiResponse } from "next";
import { createClient } from "@supabase/supabase-js";

const supa =
  process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY
    ? createClient(
        process.env.SUPABASE_URL,
        process.env.SUPABASE_SERVICE_ROLE_KEY
      )
    : null;

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const auth = req.headers.authorization || "";
  if (!auth || auth !== `Bearer ${process.env.GUARDIAN_INGEST_TOKEN}`) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  if (!supa) return res.status(200).json({ items: [] });

  const { data, error } = await supa
    .from("security_events")
    .select("*")
    .order("ts", { ascending: false })
    .limit(100);

  if (error) return res.status(500).json({ error: error.message });
  res.status(200).json({ items: data });
}
