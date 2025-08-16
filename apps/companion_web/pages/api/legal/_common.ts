import type { NextApiRequest, NextApiResponse } from "next";

export function roleFrom(req: NextApiRequest): string {
  return (req.headers["x-user-role"] as string) || "guest";
}

export async function tavilySearch(query: string) {
  const r = await fetch("https://api.tavily.com/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.TAVILY_API_KEY}`,
    },
    body: JSON.stringify({ query, include_answer: true, max_results: 6 }),
  }).then((r) => r.json());
  return {
    answer: r?.answer || "",
    results: (r?.results || []).map((x: any) => ({
      title: x.title,
      url: x.url,
      snippet: x.snippet,
    })),
  };
}

export async function openaiSummarize(prompt: string) {
  const r = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.2,
    }),
  }).then((r) => r.json());
  return r?.choices?.[0]?.message?.content || "";
}

export function limitGate(req: NextApiRequest, res: NextApiResponse) {
  const max = parseInt(process.env.LEGAL_DAILY_LIMIT || "200", 10);
  const cookieName = "legal_daily";
  const now = Date.now();
  const cookie = req.cookies?.[cookieName] || "";
  const [countStr, resetStr] = cookie.split("|");
  let count = parseInt(countStr) || 0;
  let reset = resetStr ? new Date(resetStr).getTime() : 0;
  if (!resetStr || reset <= now) {
    count = 0;
    const d = new Date();
    d.setUTCHours(24, 0, 0, 0);
    reset = d.getTime();
  }
  const ok = count < max;
  if (ok) count += 1;
  const setCookie = `${cookieName}=${count}|${new Date(reset).toISOString()}; Path=/; HttpOnly; SameSite=Lax;`;
  const remaining = ok ? max - count : 0;
  return { ok, setCookie, remaining, resetISO: new Date(reset).toISOString() };
}
