import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

let CURRENT = {
  admin: false,
  personality: "chill" as "chill"|"sassy"|"sage"|"gremlin"|"guardian"|"gamer"
};

function ok(data:any){ return NextResponse.json({ ok:true, ...data }); }
function bad(msg:string){ return NextResponse.json({ ok:false, error: msg }, { status: 400 }); }

function logAdminEvent(evt: Record<string, any>) {
  try {
    const dir = path.join(process.cwd(), "data");
    if (!fs.existsSync(dir)) fs.mkdirSync(dir);
    fs.appendFileSync(path.join(dir, "admin_mode.log"), JSON.stringify({ ts: Date.now(), ...evt })+"\n", "utf-8");
  } catch (err) {
    console.error('Failed to log admin event', err);
  }
}

export async function GET(){ return ok(CURRENT); }

export async function POST(req: NextRequest) {
  let body: any = {};
  try {
    body = await req.json();
  } catch (err) {
    console.error('Failed to parse admin mode body', err);
    body = {};
  }
  const { passphrase, pin, admin, personality } = body || {};
  const envPass=(process.env.ADMIN_PASSPHRASE||"").trim().toLowerCase();
  const envPin =(process.env.ADMIN_PIN||"").trim();
  const used = passphrase ? "passphrase" : (pin ? "pin" : "unknown");
  const authed = (passphrase && passphrase.trim().toLowerCase()===envPass) || (pin && String(pin)===String(envPin));
  if (!authed){ logAdminEvent({ type:"auth_failed", used }); return bad("unauthorized"); }

  const before = { ...CURRENT };
  if (typeof admin==="boolean") CURRENT.admin=admin;
  if (personality) CURRENT.personality=personality;

  logAdminEvent({ type:"admin_mode_update", used, before, after: CURRENT });
  return ok(CURRENT);
}
