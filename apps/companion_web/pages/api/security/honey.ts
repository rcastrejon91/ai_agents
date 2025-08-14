import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const token = process.env.GUARDIAN_INGEST_TOKEN!;
    const base = process.env.NEXT_PUBLIC_BASE_URL || "";
    await fetch(`${base}/api/security/log`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-guardian-token": token },
      body: JSON.stringify({
        event: "honeytoken_triggered",
        details: { q: req.query, ua: req.headers["user-agent"] },
      }),
    });
  } catch {}
  return res.status(204).end();
}
