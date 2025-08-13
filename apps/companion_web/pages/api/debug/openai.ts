import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(_req: NextApiRequest, res: NextApiResponse) {
  const key = process.env.OPENAI_API_KEY;
  if (!key) return res.status(500).json({ ok: false, reason: "no OPENAI_API_KEY" });

  const r = await fetch("https://api.openai.com/v1/models", {
    headers: { Authorization: `Bearer ${key}` },
  }).catch((e) => ({ ok: false, status: 599, text: async () => String(e) } as any));

  const text = await (r as any).text?.().catch(() => "(no body)");
  return res.status(r.ok ? 200 : (r.status || 502)).json({
    ok: r.ok,
    status: r.status || 0,
    body_sample: String(text).slice(0, 400),
  });
}
