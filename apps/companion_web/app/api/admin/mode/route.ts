import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import {
  sanitizeInput,
  logSecurityEvent,
} from "../../../../lib/security";
import { logger } from "../../../../lib/logger";

let CURRENT = {
  admin: false,
  personality: "chill" as
    | "chill"
    | "sassy"
    | "sage"
    | "gremlin"
    | "guardian"
    | "gamer",
};

// Rate limiting store
const rateLimitStore: { [key: string]: { count: number; resetTime: number } } =
  {};

function checkRateLimit(
  identifier: string,
  max: number = 5,
  windowMs: number = 300000,
): boolean {
  const now = Date.now();

  // Clean old entries
  Object.keys(rateLimitStore).forEach((key) => {
    if (rateLimitStore[key].resetTime < now) {
      delete rateLimitStore[key];
    }
  });

  if (!rateLimitStore[identifier]) {
    rateLimitStore[identifier] = { count: 1, resetTime: now + windowMs };
    return true;
  }

  if (rateLimitStore[identifier].count >= max) {
    return false;
  }

  rateLimitStore[identifier].count++;
  return true;
}

function ok(data: any) {
  return NextResponse.json({ ok: true, ...data });
}

function bad(msg: string, status: number = 400) {
  return NextResponse.json({ ok: false, error: msg }, { status });
}

function logAdminEvent(evt: Record<string, any>) {
  try {
    const dir = path.join(process.cwd(), "data");
    if (!fs.existsSync(dir)) fs.mkdirSync(dir);
    fs.appendFileSync(
      path.join(dir, "admin_mode.log"),
      JSON.stringify({
        ts: Date.now(),
        timestamp: new Date().toISOString(),
        ...evt,
      }) + "\n",
      "utf-8",
    );
  } catch (err) {
    logger.error("Failed to log admin event", { error: err });
  }
}

export async function GET(req: NextRequest) {
  // Set security headers and return response
  const response = ok(CURRENT);
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-XSS-Protection", "1; mode=block");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
  );
  return response;
}

export async function POST(req: NextRequest) {
  try {
    // Rate limiting
    const ip = req.ip || req.headers.get("x-forwarded-for") || "unknown";
    if (!checkRateLimit(ip, 5, 300000)) {
      // 5 attempts per 5 minutes
      logSecurityEvent("admin_rate_limit", { ip }, "WARNING");
      const response = bad("Too many attempts. Please try again later.", 429);
      // Set security headers
      response.headers.set("X-Content-Type-Options", "nosniff");
      response.headers.set("X-Frame-Options", "DENY");
      response.headers.set("X-XSS-Protection", "1; mode=block");
      response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
      response.headers.set(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
      );
      return response;
    }

    let body: any = {};
    try {
      const text = await req.text();
      if (text.length > 1000) {
        // Limit body size
        logSecurityEvent(
          "admin_body_too_large",
          { ip, size: text.length },
          "WARNING",
        );
        return bad("Request body too large");
      }
      body = JSON.parse(text);
    } catch (err) {
      logger.error("Failed to parse admin mode body", { error: err, ip });
      return bad("Invalid JSON");
    }

    // Sanitize inputs
    const passphrase = sanitizeInput(body?.passphrase, 100);
    const pin = sanitizeInput(body?.pin, 20);
    const admin = typeof body?.admin === "boolean" ? body.admin : undefined;
    const personality = sanitizeInput(body?.personality, 20);

    // Validate personality if provided
    const validPersonalities = [
      "chill",
      "sassy",
      "sage",
      "gremlin",
      "guardian",
      "gamer",
    ];
    if (personality && !validPersonalities.includes(personality)) {
      logSecurityEvent(
        "admin_invalid_personality",
        { ip, personality },
        "WARNING",
      );
      return bad("Invalid personality");
    }

    const envPass = (process.env.ADMIN_PASSPHRASE || "").trim().toLowerCase();
    const envPin = (process.env.ADMIN_PIN || "").trim();

    if (!envPass && !envPin) {
      logger.error("No admin credentials configured");
      return bad("Admin access not configured", 503);
    }

    const used = passphrase ? "passphrase" : pin ? "pin" : "unknown";
    const authed =
      (passphrase && envPass && passphrase.toLowerCase() === envPass) ||
      (pin && envPin && String(pin) === String(envPin));

    if (!authed) {
      logAdminEvent({ type: "auth_failed", used, ip });
      logSecurityEvent("admin_auth_failed", { ip, used }, "CRITICAL");
      return bad("Unauthorized", 401);
    }

    const before = { ...CURRENT };
    if (admin !== undefined) CURRENT.admin = admin;
    if (personality) CURRENT.personality = personality as any;

    logAdminEvent({
      type: "admin_mode_update",
      used,
      before,
      after: CURRENT,
      ip,
    });

    logger.info("Admin mode updated", {
      used,
      changes: { admin, personality },
      ip,
    });

    const response = ok(CURRENT);
    // Set security headers
    response.headers.set("X-Content-Type-Options", "nosniff");
    response.headers.set("X-Frame-Options", "DENY");
    response.headers.set("X-XSS-Protection", "1; mode=block");
    response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
    response.headers.set(
      "Content-Security-Policy",
      "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    );
    return response;
  } catch (error) {
    logger.error("Admin mode POST error", { error });
    const response = bad("Internal server error", 500);
    // Set security headers
    response.headers.set("X-Content-Type-Options", "nosniff");
    response.headers.set("X-Frame-Options", "DENY");
    response.headers.set("X-XSS-Protection", "1; mode=block");
    response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
    response.headers.set(
      "Content-Security-Policy",
      "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    );
    return response;
  }
}
