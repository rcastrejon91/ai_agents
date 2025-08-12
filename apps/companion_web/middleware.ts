import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

function makeJur(req: NextRequest) {
  const c = (req.headers.get("x-vercel-ip-country") || "").toUpperCase(); // e.g., US
  const r = (req.headers.get("x-vercel-ip-country-region") || "").toUpperCase(); // e.g., IL
  if (c && r) return `${c}-${r}`;        // US-IL
  if (c) return `${c}-FED`;              // US-FED (country only)
  return "US-FED";
}

export function middleware(req: NextRequest) {
  // Don’t run on static assets
  const { pathname } = req.nextUrl;
  if (pathname.startsWith("/_next") || pathname.startsWith("/favicon")) {
    return NextResponse.next();
  }
  const jurCookie = req.cookies.get("jurisdiction")?.value;
  const jur = jurCookie || makeJur(req);
  const res = NextResponse.next();
  if (!jurCookie) res.cookies.set("jurisdiction", jur, { path: "/", maxAge: 60*60*24*7 });
  return res;
}
