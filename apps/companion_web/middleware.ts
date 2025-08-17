import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { looksMalicious, rateLimit, edgeLog } from "./lib/guardian";
import { getConfig } from "./config/environments";
import { SecurityHeaders } from "./config/security";

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};

export async function middleware(req: NextRequest) {
  const url = new URL(req.url);
  const ip = (req.headers.get("x-real-ip") ||
    req.headers.get("x-forwarded-for") ||
    (req as any).ip ||
    "unknown") as string;

  // Enhanced rate limiting 
  const rateLimitMax = 90; // Could be made configurable
  if (!rateLimit(ip, rateLimitMax)) {
    await edgeLog({
      event: "rate_limit_block",
      ip,
      path: url.pathname,
      method: req.method
    });
    return NextResponse.json({ error: "Too many requests" }, { status: 429 });
  }

  // Enhanced malicious request detection
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

  // CORS validation for API routes
  if (url.pathname.startsWith('/api/')) {
    const origin = req.headers.get('origin');
    const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'];
    
    if (origin && allowedOrigins.length > 0 && !allowedOrigins.includes(origin)) {
      await edgeLog({
        event: "cors_block",
        ip,
        path: url.pathname,
        details: { origin, allowedOrigins }
      });
      return NextResponse.json({ error: "CORS policy violation" }, { status: 403 });
    }
  }

  // Apply enhanced security headers
  const res = NextResponse.next();
  
  // Set all security headers from configuration
  Object.entries(SecurityHeaders).forEach(([header, value]) => {
    res.headers.set(header, value);
  });

  // Add CORS headers for allowed origins
  const origin = req.headers.get('origin');
  const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'];
  if (origin && allowedOrigins.includes(origin)) {
    res.headers.set('Access-Control-Allow-Origin', origin);
    res.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Admin-Key');
    res.headers.set('Access-Control-Allow-Credentials', 'true');
  }

  return res;
}
