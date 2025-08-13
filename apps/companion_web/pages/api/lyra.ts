// pages/api/lyra.ts
import type { NextApiRequest, NextApiResponse } from "next";

const OPENAI_URL = "https://api.openai.com/v1/chat/completions";
const MODEL_ORDER = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"] as const;

type ChatChoice = { message?: { content?: string } };
type OpenAIChatRes = { choices?: ChatChoice[] };

function pickMessage(body: any): string {
  const msg = typeof body?.message === "string" ? body.message : "";
  return (msg || "").trim() || "Hello!";
}

async function callOpenAI(
  key: string,
  model: string,
  message: string,
  rid: string
): Promise<string> {
  // 15s guard so the request doesn’t hang forever
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), 15_000);

  try {
    const res = await fetch(OPENAI_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${key}`,
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: "You are Lyra, a concise, friendly assistant." },
          { role: "user", content: message },
        ],
      }),
      signal: controller.signal,
    });

    if (!res.ok) {
      // Let caller decide how to handle upstream failures
      const text = await res.text().catch(() => "");
      throw new Error(`upstream:${res.status} ${text}`);
    }

    const data = (await res.json()) as OpenAIChatRes;
    const reply = data?.choices?.[0]?.message?.content?.trim();
    if (!reply) throw new Error("empty_reply");
    return reply;
  } finally {
    clearTimeout(t);
  }
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Method guard
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  // Env guard
  const key = process.env.OPENAI_API_KEY;
  if (!key) {
    console.error("[lyra] missing OPENAI_API_KEY");
    return res.status(500).json({ error: "Server not configured." });
  }

  const rid = Math.random().toString(36).slice(2, 8);
  const userMsg = pickMessage(req.body);

  // Try each model; return first success
  let lastErr: unknown = null;
  for (const model of MODEL_ORDER) {
    try {
      const reply = await callOpenAI(key, model, userMsg, rid);
      return res.status(200).json({ reply });
    } catch (e) {
      lastErr = e;
      // If the error came from OpenAI, treat as upstream and try next model
      const msg = (e as Error)?.message || String(e);
      console.error(`[lyra:${rid}] model ${model} failed ->`, msg);
      continue;
    }
  }

  // All models failed → upstream error
  console.error(`[lyra:${rid}] all models failed ->`, lastErr);
  return res.status(502).json({ error: "Upstream error." });
}

