/**
 * TypeScript middleware for Express.js backend with enhanced security and monitoring.
 */
import { Request, Response, NextFunction } from "express";
import { settings } from "./config";

// Rate limiting store
interface RateLimitBucket {
  tokens: number;
  lastUpdate: number;
}

class RateLimiter {
  private buckets: Map<string, RateLimitBucket> = new Map();
  private rate: number;
  private burst: number;

  constructor() {
    const config = settings.get();
    this.rate = config.security.rateLimitPerMinute;
    this.burst = config.security.rateLimitBurst;
  }

  allowRequest(clientId: string): boolean {
    const now = Date.now() / 1000;
    
    if (!this.buckets.has(clientId)) {
      this.buckets.set(clientId, {
        tokens: this.burst,
        lastUpdate: now
      });
    }

    const bucket = this.buckets.get(clientId)!;
    
    // Add tokens based on time elapsed
    const timePassed = now - bucket.lastUpdate;
    const tokensToAdd = timePassed * (this.rate / 60.0);
    bucket.tokens = Math.min(this.burst, bucket.tokens + tokensToAdd);
    bucket.lastUpdate = now;

    // Check if request is allowed
    if (bucket.tokens >= 1) {
      bucket.tokens -= 1;
      return true;
    }

    return false;
  }

  cleanup(maxAge: number = 3600): void {
    const now = Date.now() / 1000;
    for (const [clientId, bucket] of this.buckets.entries()) {
      if (now - bucket.lastUpdate > maxAge) {
        this.buckets.delete(clientId);
      }
    }
  }
}

const rateLimiter = new RateLimiter();

export function getClientIP(req: Request): string {
  // Check for proxy headers first
  const forwardedFor = req.headers['x-forwarded-for'];
  if (forwardedFor) {
    return Array.isArray(forwardedFor) 
      ? forwardedFor[0].split(',')[0].trim()
      : forwardedFor.split(',')[0].trim();
  }
  
  const realIP = req.headers['x-real-ip'];
  if (realIP && typeof realIP === 'string') {
    return realIP;
  }
  
  const cfIP = req.headers['cf-connecting-ip'];
  if (cfIP && typeof cfIP === 'string') {
    return cfIP;
  }
  
  return req.ip || req.connection.remoteAddress || 'unknown';
}

export function securityMiddleware(req: Request, res: Response, next: NextFunction): void {
  const config = settings.get();
  const clientIP = getClientIP(req);
  
  // Rate limiting
  if (!rateLimiter.allowRequest(clientIP)) {
    console.warn(`Rate limit exceeded for IP: ${clientIP}`);
    res.status(429).json({
      error: "rate_limit_exceeded",
      message: "Too many requests. Please try again later.",
      retryAfter: 60
    });
    return;
  }
  
  // Request size validation
  const contentLength = req.headers['content-length'];
  if (contentLength && parseInt(contentLength, 10) > config.security.maxRequestSize) {
    console.warn(`Request too large from IP: ${clientIP}, size: ${contentLength}`);
    res.status(413).json({
      error: "request_too_large",
      message: "Request body too large",
      maxSize: config.security.maxRequestSize
    });
    return;
  }
  
  // Add security headers
  const securityHeaders = settings.getSecurityHeaders();
  for (const [header, value] of Object.entries(securityHeaders)) {
    res.setHeader(header, value);
  }
  
  next();
}

export function requestLoggingMiddleware(req: Request, res: Response, next: NextFunction): void {
  const config = settings.get();
  const startTime = Date.now();
  const requestId = require('crypto').randomUUID();
  const clientIP = getClientIP(req);
  
  // Add request ID to request object
  (req as any).requestId = requestId;
  
  // Log request start
  if (config.monitoring.enableRequestLogging) {
    console.log(JSON.stringify({
      level: 'info',
      message: 'Request started',
      requestId,
      method: req.method,
      url: req.url,
      clientIP,
      userAgent: req.headers['user-agent'] || '',
      timestamp: new Date().toISOString()
    }));
  }
  
  // Override res.end to log completion
  const originalEnd = res.end.bind(res);
  (res as any).end = function(chunk?: any, encoding?: any, cb?: any) {
    const duration = Date.now() - startTime;
    
    if (config.monitoring.enableRequestLogging) {
      console.log(JSON.stringify({
        level: 'info',
        message: 'Request completed',
        requestId,
        statusCode: res.statusCode,
        durationMs: duration,
        responseSize: res.get('content-length') || 'unknown'
      }));
    }
    
    // Add request ID to response headers
    res.setHeader('X-Request-ID', requestId);
    
    return originalEnd(chunk, encoding, cb);
  };
  
  next();
}

export function errorHandlingMiddleware(
  err: Error, 
  req: Request, 
  res: Response, 
  next: NextFunction
): void {
  const requestId = (req as any).requestId || require('crypto').randomUUID();
  const config = settings.get();
  
  // Log the error
  console.error(JSON.stringify({
    level: 'error',
    message: 'Unhandled exception',
    requestId,
    error: err.message,
    errorType: err.constructor.name,
    path: req.path,
    method: req.method,
    stack: err.stack
  }));
  
  // Build error response
  const errorResponse: any = {
    error: "internal_server_error",
    message: "An unexpected error occurred",
    requestId
  };
  
  if (config.debug) {
    errorResponse.debug = {
      errorType: err.constructor.name,
      errorDetails: err.message
    };
  }
  
  res.status(500).json(errorResponse);
}

export function validateJSON(requiredFields?: string[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    if (req.method === 'POST' || req.method === 'PUT' || req.method === 'PATCH') {
      if (!req.body || typeof req.body !== 'object') {
        res.status(400).json({
          error: "invalid_json",
          message: "Request body must be valid JSON"
        });
        return;
      }
      
      if (requiredFields && requiredFields.length > 0) {
        const missingFields = requiredFields.filter(field => !(field in req.body));
        if (missingFields.length > 0) {
          res.status(400).json({
            error: "missing_fields",
            message: "Required fields are missing",
            missingFields
          });
          return;
        }
      }
    }
    
    next();
  };
}

export function corsMiddleware() {
  const corsOptions = settings.getCorsConfig();
  return require('cors')(corsOptions);
}

// Cleanup rate limiter buckets periodically
setInterval(() => {
  rateLimiter.cleanup();
}, 300000); // Every 5 minutes