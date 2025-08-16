export const runtime = "nodejs";
import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const DATA_DIR = process.env.DATA_PATH || "/tmp/data";
const EMAIL_FROM = process.env.EMAIL_FROM!;
const EMAIL_TO = process.env.EMAIL_TO!;
const MAIL_ENDPOINT = process.env.MAIL_ENDPOINT || "";
const MAIL_API_KEY = process.env.MAIL_API_KEY || "";

function r<T>(f: string, fb: T): T {
  try {
    return JSON.parse(fs.readFileSync(path.join(DATA_DIR, f), "utf8"));
  } catch (err) {
    console.error("Failed to read file", f, err);
    return fb;
  }
}

async function send(subject: string, text: string) {
  if (!MAIL_ENDPOINT) return;
  try {
    await fetch(MAIL_ENDPOINT, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-mail-key": MAIL_API_KEY,
      },
      body: JSON.stringify({ from: EMAIL_FROM, to: EMAIL_TO, subject, text }),
    });
  } catch (err) {
    console.error("Failed to send digest mail", err);
  }
}

export async function POST() {
  const proc = r<any>("learn_knowledge.json", { entries: [] });
  const last = proc.entries.slice(-8).reverse();
  if (!last.length)
    return NextResponse.json({ ok: true, skipped: "no entries" });

  const lines = last
    .map((e: any, i: number) => `${i + 1}. ${e.url}\n---\n${e.summary}\n`)
    .join("\n");

  const body = `Lyra — What I learned today\n\n${lines}\n\n— end —`;
  await send("Lyra Daily Learning Digest", body);
  return NextResponse.json({ ok: true, sent: last.length });
}
