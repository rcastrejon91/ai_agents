import type { NextApiRequest, NextApiResponse } from "next";
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const q = (req.query.q as string) || "speech+pronunciation";
  const url = `https://export.arxiv.org/api/query?search_query=all:${encodeURIComponent(q)}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending`;
  const r = await fetch(url);
  const xml = await r.text();
  const items: any[] = [];
  const rx =
    /<entry>[\s\S]*?<title>([\s\S]*?)<\/title>[\s\S]*?<id>([\s\S]*?)<\/id>[\s\S]*?<summary>([\s\S]*?)<\/summary>/g;
  let m: RegExpExecArray | null;
  while ((m = rx.exec(xml))) {
    items.push({ title: m[1].trim(), url: m[2].trim(), summary: m[3].trim() });
  }
  res.status(200).json({ items });
}
