import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
type Decision = "approve" | "reject" | "modify";

function writeJSON(p: string, data: any) {
  const d = path.dirname(p);
  if (!fs.existsSync(d)) fs.mkdirSync(d);
  fs.writeFileSync(p, JSON.stringify(data, null, 2), "utf-8");
}
function readJSON<T>(p: string, fb: T): T {
  try {
    return JSON.parse(fs.readFileSync(p, "utf-8"));
  } catch {
    return fb;
  }
}

export async function POST(req: NextRequest) {
  const { id, title, decision, notes } = await req.json();
  if (!id || !decision)
    return NextResponse.json(
      { ok: false, error: "missing id/decision" },
      { status: 400 },
    );
  const file = path.join(process.cwd(), "data", "pitches.json");
  const log = path.join(process.cwd(), "data", "pitches.log");
  const all = readJSON<{ history: any[] }>(file, { history: [] });
  const entry = {
    ts: Date.now(),
    id,
    title: title || "(untitled)",
    decision: decision as Decision,
    notes: notes || "",
  };
  all.history.push(entry);
  writeJSON(file, all);
  try {
    fs.appendFileSync(log, JSON.stringify(entry) + "\n", "utf-8");
  } catch {}
  return NextResponse.json({ ok: true });
}
