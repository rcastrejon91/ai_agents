import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  if (req.method !== "POST")
    return res.status(405).json({ error: "Method not allowed" });

  const { message, mode = "chill" } = (req.body as any) || {};
  if (!message || typeof message !== "string")
    return res.status(400).json({ error: "message required" });

  if (!process.env.OPENAI_API_KEY) {
    return res.status(200).json({ reply: `(demo:${mode}) ${message}` });
  }

  try {
    const r = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content: `You are LYRA for AITaskFlo, a ${mode} but helpful assistant.`,
          },
          { role: "user", content: message },
        ],
        temperature: 0.7,
      }),
    }).then((r) => r.json());

    const reply = r?.choices?.[0]?.message?.content ?? "...";
    return res.status(200).json({ reply });
  } catch (e: any) {
    return res.status(500).json({ error: e?.message || "server error" });
  }
}
