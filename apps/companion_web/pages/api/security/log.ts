import type { NextApiRequest, NextApiResponse } from "next";
import { createClient } from "@supabase/supabase-js";
import { alertWebhook } from "../../../lib/guardian";

const supa = process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY
  ? createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY)
  : null;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const token = req.headers["x-guardian-token"];
  if (!token || token !== process.env.GUARDIAN_INGEST_TOKEN) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  const body = (req.body ?? {}) as any;
  const record = {
    event: body.event || "unknown",
    ip: body.ip || (req.headers["x-forwarded-for"] as string) || req.socket.remoteAddress || null,
    path: body.path || null,
    method: body.method || req.method,
    query: body.query || null,
    user_agent: body.user_agent || (req.headers["user-agent"] as string) || null,
    referrer: body.referrer || (req.headers["referer"] as string) || null,
    country: body.country || null,
    city: body.city || null,
    details: body.details || {},
  };

  if (["waf_block", "rate_limit_block", "honeytoken_triggered"].includes(record.event)) {
    await alertWebhook(record.event, record);
  }

  if (!supa) return res.status(200).json({ ok: true, stored: false });

  try {
    const { error } = await supa.from("security_events").insert([record]);
    if (error) throw error;
    return res.status(200).json({ ok: true, stored: true });
  } catch (e: any) {
    console.error("[guardian/log] insert failed", e?.message || e);
    return res.status(200).json({ ok: false, stored: false });
  }
}
