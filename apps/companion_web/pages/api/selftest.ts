import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  _req: NextApiRequest,
  res: NextApiResponse
) {
  const key = process.env.OPENAI_API_KEY;
  if (!key)
    return res
      .status(500)
      .json({ ok: false, step: "env", msg: "No OPENAI_API_KEY" });
  const r = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${key}`,
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: "ping" }],
    }),
  });
  const text = await r.text();
  return res
    .status(r.ok ? 200 : 502)
    .json({ ok: r.ok, status: r.status, body: text.slice(0, 500) });
}
