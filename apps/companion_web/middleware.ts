import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { looksMalicious, rateLimit, edgeLog } from "./lib/guardian";

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};

export async function middleware(req: NextRequest) {
  const url = new URL(req.url);
  const ip = (req.headers.get("x-real-ip") ||
    req.headers.get("x-forwarded-for") ||
    (req as any).ip ||
    "unknown") as string;

  if (!rateLimit(ip, 90)) {
    await edgeLog({
      event: "rate_limit_block",
      ip,
      path: url.pathname,
      method: req.method,
    });
    return NextResponse.json({ error: "Too many requests" }, { status: 429 });
  }

  const hay = `${url.pathname} ${url.search || ""}`;
  if (looksMalicious(hay)) {
    await edgeLog({
      event: "waf_block",
      ip,
      path: url.pathname,
      method: req.method,
      query: url.search || "",
      user_agent: req.headers.get("user-agent"),
      referrer: req.headers.get("referer"),
    });
    return NextResponse.json({ error: "Blocked by Guardian" }, { status: 403 });
  }

  const res = NextResponse.next();
  res.headers.set("X-Frame-Options", "DENY");
  res.headers.set("X-Content-Type-Options", "nosniff");
  res.headers.set("Referrer-Policy", "no-referrer");
  res.headers.set("Permissions-Policy", "geolocation=(), microphone=()");
  res.headers.set(
    "Content-Security-Policy",
    [
      "default-src 'self'",
      "img-src 'self' data: https:",
      "script-src 'self' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline'",
      "connect-src 'self' https:",
      "frame-ancestors 'none'",
    ].join("; "),
  );
  return res;
}
