export const runtime = "nodejs";
import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const DATA_DIR = process.env.DATA_PATH || "/tmp/data";
function ensure() {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
}
function readJSON<T>(f: string, fb: T): T {
  try {
    return JSON.parse(fs.readFileSync(path.join(DATA_DIR, f), "utf8"));
  } catch (err) {
    console.error("Failed to read JSON file", f, err);
    return fb;
  }
}
function writeJSON(f: string, d: any) {
  ensure();
  fs.writeFileSync(path.join(DATA_DIR, f), JSON.stringify(d, null, 2), "utf8");
}

async function fetchText(url: string) {
  const res = await fetch(url, {
    headers: { "user-agent": "LyraBot/1.0 (+https://example.com)" },
  });
  if (!res.ok) throw new Error(`fetch ${url} ${res.status}`);
  return await res.text();
}

async function robotsAllows(url: string) {
  try {
    const u = new URL(url);
    const robots = `${u.origin}/robots.txt`;
    let txt = "";
    try {
      txt = await fetchText(robots);
    } catch (err) {
      console.error("Failed to fetch robots.txt", err);
      txt = "";
    }
    if (!txt) return true;
    const dis = txt
      .split("\n")
      .filter((l) => l.toLowerCase().startsWith("disallow:"))
      .map((l) => l.split(":")[1].trim());
    return !dis.some((rule) => u.pathname.startsWith(rule));
  } catch (err) {
    console.error("robots.txt check failed", err);
    return true;
  }
}

export async function POST(req: NextRequest) {
  const { RSS_FEEDS } = await import("../_sources");
  const MAX = Number(process.env.LEARN_MAX_ITEMS || 25);
  const bucket = readJSON<any>("learn_raw.json", { items: [] });

  for (const feed of RSS_FEEDS) {
    try {
      const xml = await fetchText(feed);
      const links = (xml.match(/<link>(.*?)<\/link>/g) || [])
        .map((m: string) => m.replace(/<\/?link>/g, ""))
        .slice(0, 20);
      for (const link of links) {
        if (!link || !allowed(link)) continue;
        if (bucket.items.find((x: any) => x.url === link)) continue;
        bucket.items.push({ url: link, source: "rss", ts: Date.now() });
      }
    } catch (err) {
      console.error("RSS fetch failed", feed, err);
    }
  }

  try {
    const w = await fetch(
      "https://en.wikipedia.org/api/rest_v1/feed/featured/2025/01/01",
    ).then((r) => r.json());
    w?.tfa?.content_urls?.desktop?.page &&
      bucket.items.push({
        url: w.tfa.content_urls.desktop.page,
        source: "wikipedia",
        ts: Date.now(),
      });
  } catch (err) {
    console.error("Wikipedia featured feed fetch failed", err);
  }

  try {
    const q = 'assistive robotics hospital navigation safety "best practices"';
    const res = await fetch("https://api.tavily.com/search", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-apis-key": process.env.TAVILY_API_KEY!,
      },
      body: JSON.stringify({
        query: q,
        include_domains: (process.env.LEARN_ALLOWED_DOMAINS || "").split(","),
      }),
    }).then((r) => r.json());
    for (const hit of res?.results || []) {
      if (!allowed(hit.url)) continue;
      if (!bucket.items.find((x: any) => x.url === hit.url)) {
        bucket.items.push({ url: hit.url, source: "tavily", ts: Date.now() });
      }
    }
  } catch (err) {
    console.error("Tavily search failed", err);
  }

  bucket.items = bucket.items.slice(-MAX);
  writeJSON("learn_raw.json", bucket);
  return NextResponse.json({ ok: true, count: bucket.items.length });
}

function allowed(url: string) {
  const { allowedDomain } = require("../_sources");
  return allowedDomain(url);
}
