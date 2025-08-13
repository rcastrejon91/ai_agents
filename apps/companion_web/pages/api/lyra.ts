// Debug-friendly Lyra API route
import type { NextApiRequest, NextApiResponse } from "next";

type ChatChoice = { message?: { content?: string } };
type OpenAIChatRes = { choices?: ChatChoice[] };

const MODEL_ORDER = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"] as const;
const OPENAI_URL = "https://api.openai.com/v1/chat/completions";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const rid = Math.random().toString(36).slice(2, 8); // request id for logs
  try {
    if (req.method !== "POST") {
      return res.status(405).json({ error: "Method not allowed" });
    }

    // --- Env + input sanity ---------------------------------------------------
    const key = process.env.OPENAI_API_KEY;
    if (!key) {
      console.error(`[lyra:${rid}] Missing OPENAI_API_KEY`);
      return res.status(500).json({ error: "Server not configured." });
    }

    const { message = "" } = (req.body ?? {}) as { message?: string };
    const userMsg = (typeof message === "string" && message.trim()) || "Hello";
    const systemPrompt =
      "You are Lyra, a concise, friendly assistant. Keep answers short and helpful.";

    // --- Try models in order until one succeeds -------------------------------
    let lastErrText = "";
    for (const model of MODEL_ORDER) {
      try {
        const payload = {
          model,
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userMsg },
          ],
        };

        const r = await fetch(OPENAI_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${key}`,
          },
          body: JSON.stringify(payload),
        });

        // Log full upstream body for failures so we can SEE the reason in Vercel logs
        if (!r.ok) {
          const errText = await r.text().catch(() => "");
          lastErrText = `status=${r.status} body=${errText}`;
          console.error(`[lyra:${rid}] upstream error model=${model} -> ${lastErrText}`);

          // If the model is unknown/forbidden for this key, try next model
          if (r.status === 404 || r.status === 400 || r.status === 403) continue;

          // Non-transient error: stop trying others, return message to client
          return res.status(502).json({ error: "Upstream error." });
        }

        // Parse success
        const data = (await r.json()) as OpenAIChatRes;
        const reply =
          data?.choices?.[0]?.message?.content?.trim() ||
          "I'm not sure what to say, but I'm here!";

        return res.status(200).json({ reply, model });
      } catch (e: any) {
        // Network/parse exception: try next model
        const msg = e?.stack || e?.message || String(e);
        console.error(`[lyra:${rid}] exception model=${model} ->`, msg);
        lastErrText = msg;
        continue;
      }
    }

    // If we fell through every model:
    console.error(`[lyra:${rid}] all models failed -> ${lastErrText}`);
    return res.status(502).json({ error: "Upstream error." });
  } catch (e: any) {
    console.error(`[lyra:${rid}] fatal`, e?.stack || e?.message || e);
    return res.status(500).json({ error: "Server error." });
  }
}
