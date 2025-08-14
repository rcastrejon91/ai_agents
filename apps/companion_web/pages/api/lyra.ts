import type { NextApiRequest, NextApiResponse } from "next";
import { scrubSecrets } from "../../lib/guardian";

const LYRA_MODEL = "gpt-4o-mini";

// Minimal Lyra API route that validates env wiring and proxies to OpenAI.
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const { message = "" } = (req.body ?? {}) as { message?: string };

    // naive tool inference: pick tools based on message keywords
    const tools: string[] = [];
    if (/\btrial|study|paper|pubmed|openalex|arxiv\b/i.test(message)) tools.push("Discovery");
    if (/\bcbc|cmp|hemoglobin|glucose|platelet|wbc\b/i.test(message)) tools.push("Labs");
    if (/\bdispatch|deliver|runner|iv|rad|or-|code blue|ops\b/i.test(message)) tools.push("Ops");
    if (tools.length === 0) tools.push("Chat");

    const key = process.env.OPENAI_API_KEY;
    if (!key) {
      console.error("[lyra] missing OPENAI_API_KEY");
      const reply = `(demo) Using ${tools.join(" + ")} → ${message}`;
      return res.status(200).json({ reply, model: "demo", tools });
    }

    // Health ping: allows ?ping=1 check without burning tokens
    if (req.query.ping) {
      return res.status(200).json({ reply: "pong", model: "demo", tools });
    }

    // Call OpenAI
    const openaiRes = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${key}`,
      },
      body: JSON.stringify({
        model: LYRA_MODEL,
        messages: [
          { role: "system", content: "You are Lyra, a concise, friendly assistant." },
          { role: "user", content: message },
        ],
      }),
    });

    if (!openaiRes.ok) {
      let errText = "";
      try {
        errText = await openaiRes.text();
      } catch (err) {
        console.error('[lyra] failed to read error body', err);
        errText = "";
      }
      console.error("[lyra] upstream error", openaiRes.status, errText);
      return res.status(502).json({ error: "Upstream error." });
    }

    const data = (await openaiRes.json()) as any;
    const reply: string | undefined = data?.choices?.[0]?.message?.content?.trim();
    const safeReply = scrubSecrets(reply ?? "I'm not sure what to say, but I'm here!");
    return res.status(200).json({ reply: safeReply, model: LYRA_MODEL, tools });
  } catch (e: any) {
    console.error("[lyra] exception", e?.stack || e?.message || e);
    return res.status(500).json({ error: "Server error." });
  }
}

