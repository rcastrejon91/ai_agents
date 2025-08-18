/**
 * Authentication and security utilities for Next.js API routes
 */

import { NextApiRequest, NextApiResponse } from "next";
import { NextResponse } from "next/server";
import { getSession } from "next-auth/react";

export interface SecurityConfig {
  requireAuth?: boolean;
  rateLimit?: {
    max: number;
    windowMs: number;
  };
  allowedMethods?: string[];
  maxBodySize?: number;
}

export interface RateLimitStore {
  [key: string]: {
    requests: number;
    resetTime: number;
  };
}

// Simple in-memory rate limit store (use Redis in production)
const rateLimitStore: RateLimitStore = {};

/**
 * Rate limiting middleware for API routes
 */
export function rateLimit(config: { max: number; windowMs: number }) {
  return (req: NextApiRequest, res: NextApiResponse): boolean => {
    const key = getClientIdentifier(req);
    const now = Date.now();
    const windowStart = now - config.windowMs;

    // Clean up old entries
    Object.keys(rateLimitStore).forEach((k) => {
      if (rateLimitStore[k].resetTime < windowStart) {
        delete rateLimitStore[k];
      }
    });

    if (!rateLimitStore[key]) {
      rateLimitStore[key] = {
        requests: 1,
        resetTime: now + config.windowMs,
      };
      return true;
    }

    if (rateLimitStore[key].resetTime < now) {
      // Reset window
      rateLimitStore[key] = {
        requests: 1,
        resetTime: now + config.windowMs,
      };
      return true;
    }

    if (rateLimitStore[key].requests >= config.max) {
      return false;
    }

    rateLimitStore[key].requests++;
    return true;
  };
}

/**
 * Get client identifier for rate limiting
 */
function getClientIdentifier(req: NextApiRequest): string {
  // Use IP address and user agent for identification
  const forwarded = req.headers["x-forwarded-for"];
  const ip = forwarded
    ? Array.isArray(forwarded)
      ? forwarded[0]
      : forwarded.split(",")[0]
    : req.socket.remoteAddress;
  const userAgent = req.headers["user-agent"] || "";
  return `${ip}:${userAgent.slice(0, 50)}`;
}

/**
 * Input sanitization utilities
 */
export function sanitizeInput(
  input: unknown,
  maxLength: number = 1000,
): string {
  if (typeof input !== "string") {
    return "";
  }

  // Limit length
  let sanitized = input.slice(0, maxLength);

  // Remove potentially dangerous HTML/script content
  sanitized = sanitized
    .replace(/<script[^>]*>.*?<\/script>/gi, "")
    .replace(/<iframe[^>]*>.*?<\/iframe>/gi, "")
    .replace(/javascript:/gi, "")
    .replace(/vbscript:/gi, "")
    .replace(/on\w+\s*=/gi, "");

  // Basic HTML escape
  sanitized = sanitized
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");

  return sanitized.trim();
}

/**
 * Validate email format
 */
export function validateEmail(email: string): boolean {
  if (!email || typeof email !== "string") {
    return false;
  }

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email) && email.length <= 254;
}

/**
 * Security headers middleware
 */
export function setSecurityHeaders(res: NextApiResponse): void;
export function setSecurityHeaders(res: NextResponse): NextResponse;
export function setSecurityHeaders(res: NextApiResponse | NextResponse): void | NextResponse {
  const headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
  };

  if (res instanceof NextResponse) {
    // App Router NextResponse
    Object.entries(headers).forEach(([key, value]) => {
      res.headers.set(key, value);
    });
    return res;
  } else {
    // Pages API NextApiResponse
    Object.entries(headers).forEach(([key, value]) => {
      res.setHeader(key, value);
    });
  }
}

/**
 * Logger for security events
 */
export function logSecurityEvent(
  type: string,
  details: Record<string, any>,
  level: "INFO" | "WARNING" | "ERROR" | "CRITICAL" = "WARNING",
): void {
  const logEntry = {
    timestamp: new Date().toISOString(),
    type,
    level,
    details,
  };

  console.log(`[SECURITY-${level}]`, JSON.stringify(logEntry));
}

/**
 * Middleware wrapper for securing API routes
 */
export function withSecurity(
  handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void> | void,
  config: SecurityConfig = {},
) {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    try {
      // Set security headers
      setSecurityHeaders(res);

      // Check allowed methods
      if (
        config.allowedMethods &&
        !config.allowedMethods.includes(req.method || "")
      ) {
        logSecurityEvent("method_not_allowed", {
          method: req.method,
          url: req.url,
        });
        return res.status(405).json({ error: "Method not allowed" });
      }

      // Rate limiting
      if (config.rateLimit) {
        const limiter = rateLimit(config.rateLimit);
        if (!limiter(req, res)) {
          logSecurityEvent("rate_limit_exceeded", {
            ip: getClientIdentifier(req),
            url: req.url,
          });
          return res.status(429).json({ error: "Too many requests" });
        }
      }

      // Authentication check
      if (config.requireAuth) {
        const session = await getSession({ req });
        if (!session) {
          logSecurityEvent("unauthorized_access", {
            url: req.url,
            userAgent: req.headers["user-agent"],
          });
          return res.status(401).json({ error: "Unauthorized" });
        }
      }

      // Body size check
      if (config.maxBodySize && req.body) {
        const bodySize = JSON.stringify(req.body).length;
        if (bodySize > config.maxBodySize) {
          logSecurityEvent("body_too_large", {
            size: bodySize,
            maxSize: config.maxBodySize,
            url: req.url,
          });
          return res.status(413).json({ error: "Request body too large" });
        }
      }

      // Call the actual handler
      await handler(req, res);
    } catch (error) {
      console.error("Security middleware error:", error);
      logSecurityEvent(
        "middleware_error",
        {
          error: error instanceof Error ? error.message : "Unknown error",
          url: req.url,
        },
        "ERROR",
      );

      if (!res.headersSent) {
        res.status(500).json({ error: "Internal server error" });
      }
    }
  };
}

/**
 * CSRF token utilities (for form-based requests)
 */
export function generateCSRFToken(): string {
  return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
}

export function validateCSRFToken(
  token: string,
  sessionToken: string,
): boolean {
  return token === sessionToken;
}

/**
 * Sanitize and validate API request body
 */
export function sanitizeApiBody<T extends Record<string, any>>(
  body: any,
  schema: {
    [K in keyof T]: { type: string; maxLength?: number; required?: boolean };
  },
): Partial<T> {
  if (!body || typeof body !== "object") {
    return {};
  }

  const sanitized: Partial<T> = {};

  for (const [key, config] of Object.entries(schema)) {
    const value = body[key];

    if (
      config.required &&
      (value === undefined || value === null || value === "")
    ) {
      throw new Error(`Required field '${key}' is missing`);
    }

    if (value !== undefined && value !== null) {
      if (config.type === "string") {
        sanitized[key as keyof T] = sanitizeInput(
          value,
          config.maxLength,
        ) as any;
      } else if (config.type === "number") {
        const num = Number(value);
        if (!isNaN(num)) {
          sanitized[key as keyof T] = num as any;
        }
      } else if (config.type === "boolean") {
        sanitized[key as keyof T] = Boolean(value) as any;
      } else if (config.type === "array" && Array.isArray(value)) {
        sanitized[key as keyof T] = value.slice(0, 100) as any; // Limit array size
      }
    }
  }

  return sanitized;
}
