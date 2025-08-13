import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { message = "" } = req.body || {};
    if (!process.env.OPENAI_API_KEY) {
      console.error("[lyra] missing OPENAI_API_KEY");
      return res
        .status(200)
        .json({ reply: "The server is missing credentials, please try later." });
    }

    const openaiRes = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [{ role: "user", content: message }],
      }),
    });

    if (!openaiRes.ok) {
      const errText = await openaiRes.text().catch(() => "");
      console.error("[lyra] upstream", openaiRes.status, errText);
      return res
        .status(200)
        .json({ reply: "Sorry, I'm having trouble responding right now." });
    }

    const data = await openaiRes.json();
    const reply = data?.choices?.[0]?.message?.content?.trim();
    return res
      .status(200)
      .json({ reply: reply ?? "I'm not sure what to say, but I'm here!" });
  } catch (e: any) {
    console.error("[lyra] exception", e?.stack || e?.message || e);
    return res
      .status(200)
      .json({ reply: "Sorry, I'm having trouble responding right now." });
  }
}

