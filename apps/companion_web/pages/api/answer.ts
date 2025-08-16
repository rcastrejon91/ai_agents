import type { NextApiRequest, NextApiResponse } from "next";

// simple fetch with timeout
async function getJSON(url: string, headers: any = {}) {
  const ctrl = new AbortController();
  const to = setTimeout(() => ctrl.abort(), 8000);
  try {
    const r = await fetch(url, { headers, signal: ctrl.signal });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return await r.json();
  } finally {
    clearTimeout(to);
  }
}

async function wiki(q: string) {
  const s = await getJSON(
    `https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srsearch=${encodeURIComponent(q)}`,
  );
  const top = s?.query?.search?.[0];
  if (!top?.title) return null;
  const sum = await getJSON(
    `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(top.title)}`,
  );
  return {
    title: sum?.title || top.title,
    url:
      sum?.content_urls?.desktop?.page ||
      `https://en.wikipedia.org/wiki/${encodeURIComponent(top.title)}`,
    snippet: sum?.extract || "",
  };
}

async function hn(q: string) {
  // quick & dirty: take top stories and filter by query in title
  const ids: number[] = await getJSON(
    "https://hacker-news.firebaseio.com/v0/topstories.json",
  );
  const items = await Promise.all(
    ids
      .slice(0, 50)
      .map(
        async (id) =>
          await getJSON(
            `https://hacker-news.firebaseio.com/v0/item/${id}.json`,
          ),
      ),
  );
  return items
    .filter((i: any) => i?.title?.toLowerCase().includes(q.toLowerCase()))
    .slice(0, 3)
    .map((i: any) => ({
      title: i.title,
      url: i.url || `https://news.ycombinator.com/item?id=${i.id}`,
    }));
}

async function rssTech() {
  const r = await fetch("https://hnrss.org/frontpage"); // xml
  const xml = await r.text();
  const items: { title: string; url: string }[] = [];
  const regex =
    /<item>[\s\S]*?<title>(.*?)<\/title>[\s\S]*?<link>(.*?)<\/link>/g;
  let match: RegExpExecArray | null;
  while ((match = regex.exec(xml)) && items.length < 5) {
    items.push({ title: match[1], url: match[2] });
  }
  return items;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  try {
    if (req.method !== "POST") return res.status(405).end();
    const { question = "" } = (req.body || {}) as { question?: string };
    const q = String(question).trim();
    if (!q) return res.status(400).json({ error: "missing question" });

    // gather free sources
    let w: any = null;
    let h: any[] = [];
    let r: any[] = [];
    await Promise.all([
      (async () => {
        try {
          w = await wiki(q);
        } catch (err) {
          console.error("wiki fetch failed", err);
          w = null;
        }
      })(),
      (async () => {
        try {
          h = await hn(q);
        } catch (err) {
          console.error("hn fetch failed", err);
          h = [];
        }
      })(),
      (async () => {
        try {
          r = await rssTech();
        } catch (err) {
          console.error("rssTech fetch failed", err);
          r = [];
        }
      })(),
    ]);
    const sources = [...(w ? [w] : []), ...h, ...r.slice(0, 2)].slice(0, 6);

    // build context for the model
    const context = sources
      .map((s: any, i: number) => `[${i + 1}] ${s.title}\n${s.url}`)
      .join("\n\n");

    // ask OpenAI to answer WITH citations indexes
    let answerText = "Demo mode: no OPENAI_API_KEY set.";
    if (process.env.OPENAI_API_KEY) {
      const prompt = [
        `You are Lyra, a careful assistant. Answer the user's question using ONLY the context links.`,
        `Cite like [1], [2] where relevant. If unknown, say you don't know.`,
        `Question: ${q}`,
        `Context:\n${context}`,
      ].join("\n\n");

      const r = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          model: "gpt-4o-mini",
          temperature: 0.2,
          messages: [{ role: "user", content: prompt }],
        }),
      });
      if (!r.ok) {
        let t = "";
        try {
          t = await r.text();
        } catch (err) {
          console.error("Failed to read OpenAI error", err);
          t = "";
        }
        return res
          .status(502)
          .json({ error: "upstream", detail: t.slice(0, 400) });
      }
      const j = await r.json();
      answerText = j?.choices?.[0]?.message?.content?.trim() || "No answer.";
    }

    res.status(200).json({ answer: answerText, sources });
  } catch (e: any) {
    console.error("answer route failed", e);
    res.status(500).json({ error: e?.message || "server_error" });
  }
}
