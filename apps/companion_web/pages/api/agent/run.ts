import type { NextApiRequest, NextApiResponse } from "next";

type Step = {
  id: string;
  tool: string;
  args: Record<string, string>;
  note?: string;
  result?: any;
};
type RunReport = {
  plan: Step[];
  outputs: {
    id: string;
    ok: boolean;
    title?: string;
    text?: string;
    cite?: string;
  }[];
  summary: string;
};

function heuristicPlan(q: string): Step[] {
  const s: Step[] = [];
  const add = (tool: string, args: any, note = "") =>
    s.push({ id: String(s.length + 1), tool, args, note });
  const lower = q.toLowerCase();

  // Simple rules if no LLM: use keywords to choose tools
  if (/\b(weather|temp)\b/.test(lower)) {
    // try geocode first if a place is in text; naive extraction: last 4 words
    const guess = q.split(" ").slice(-4).join(" ");
    add("geocode", { q: guess }, "Guess location from question tail");
    add(
      "weather",
      { lat: "{{plan.1.data.lat}}", lon: "{{plan.1.data.lon}}" },
      "Use geocoded coords",
    ); // templated fill
  }
  if (/\b(wiki|what is|who is|explain|latest)\b/.test(lower)) {
    add("wiki", { q }, "General knowledge");
  }
  if (/\bnews|tech\b/.test(lower)) add("hn", {}, "Tech news snapshot");
  return s.length
    ? s
    : [{ id: "1", tool: "wiki", args: { q }, note: "Default knowledge" }];
}

async function llmPlan(q: string, key: string) {
  const prompt = `
Create 1-4 JSON steps to answer the user by calling tools.
Tools: wiki{q}, geocode{q}, weather{lat,lon}, hn{}, books{q}, dict{w}, rss{url}.
Return ONLY JSON array. Use geocode->weather if user mentions a place.

User: ${q}`;
  const r = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${key}`,
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      temperature: 0.1,
      messages: [{ role: "user", content: prompt }],
    }),
  });
  if (!r.ok) throw new Error("llm plan failed");
  const j = await r.json();
  const txt = j?.choices?.[0]?.message?.content || "[]";
  try {
    return JSON.parse(txt) as Step[];
  } catch (err) {
    console.error("Failed to parse LLM plan", err);
    return heuristicPlan(q);
  }
}

function fillTemplates(args: Record<string, string>, ctx: Record<string, any>) {
  const out: Record<string, string> = {};
  for (const k of Object.keys(args)) {
    out[k] = args[k].replace(/\{\{([^}]+)\}\}/g, (_, path) => {
      const parts = path.split(".");
      let v: any = ctx;
      for (const p of parts) v = v?.[p];
      return v ?? "";
    });
  }
  return out;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<RunReport | any>,
) {
  try {
    if (req.method !== "POST") return res.status(405).end();
    const q = (req.body?.query || "").toString().trim();
    if (!q) return res.status(400).json({ error: "missing query" });

    const plan: Step[] = process.env.OPENAI_API_KEY
      ? await llmPlan(q, process.env.OPENAI_API_KEY)
      : heuristicPlan(q);

    // Execute steps client-side; this API just returns the plan.
    // (Safer, avoids server SSRF. The client will call our /api/free/* routes.)
    return res
      .status(200)
      .json({
        plan,
        outputs: [],
        summary: "Client should execute steps and report back.",
      });
  } catch (e: any) {
    console.error("Agent run failed", e);
    return res.status(500).json({ error: e?.message || "agent_error" });
  }
}
