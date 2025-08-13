import type { NextApiRequest, NextApiResponse } from "next";

// Minimal Lyra API route that validates env wiring and proxies to OpenAI.
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { message = "" } = (req.body ?? {}) as { message?: string };

    // Sanity: env must exist
    const key = process.env.OPENAI_API_KEY;
    if (!key) {
      console.error("[lyra] missing OPENAI_API_KEY");
      return res.status(500).json({ error: "Server not configured." });
    }

    // Health ping: allows ?ping=1 check without burning tokens
    if (req.query.ping) {
      return res.status(200).json({ reply: "pong" });
    }

    // Call OpenAI
    const openaiRes = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${key}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: "You are Lyra, a concise, friendly assistant." },
          { role: "user", content: message },
        ],
      }),
    });

    if (!openaiRes.ok) {
      const errText = await openaiRes.text().catch(() => "");
      console.error("[lyra] upstream error", openaiRes.status, errText);
      return res.status(502).json({ error: "Upstream error." });
    }

    const data = (await openaiRes.json()) as any;
    const reply: string | undefined = data?.choices?.[0]?.message?.content?.trim();
    return res.status(200).json({ reply: reply ?? "I'm not sure what to say, but I'm here!" });
  } catch (e: any) {
    console.error("[lyra] exception", e?.stack || e?.message || e);
    return res.status(500).json({ error: "Server error." });
  }
}
