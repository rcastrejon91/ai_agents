import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import OpenAI from "openai";
import bodyParser from "body-parser";
import * as Sentry from '@sentry/node';
import { randomUUID } from 'crypto';
import billingRouter from "./billing.js";
import { checkFeature } from "../../companion_web/server/compliance/check";
import {
  validateEnvironment,
  getEnvironmentConfig,
} from "./config/env-validation.js";
import { ErrorHandler } from "./utils/ErrorHandler.js";
import { MetricsCollector } from "./monitoring/MetricsCollector.js";
import { CacheManager } from "./utils/CacheManager.js";
import { AuthenticationService } from "./security/AuthenticationService.js";
import { Logger } from "./utils/Logger.js";

dotenv.config();

// Initialize Sentry if DSN is provided
if (process.env.SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.NODE_ENV || 'development',
    tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  });
}

// Validate environment variables on startup
const envConfig = validateEnvironment();
const appConfig = getEnvironmentConfig();

// Initialize services
const logger = new Logger('App');
const metricsCollector = new MetricsCollector();
const cacheManager = new CacheManager();
const authService = new AuthenticationService();

const app = express();

// Request ID middleware
app.use((req, res, next) => {
  (req as any).id = randomUUID();
  res.setHeader('X-Request-ID', (req as any).id);
  next();
});

// Metrics middleware
app.use(metricsCollector.createMiddleware());

// Security headers middleware
app.use((req, res, next) => {
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  next();
});

// CORS configuration
const corsOptions = {
  origin: function (
    origin: string | undefined,
    callback: (err: Error | null, allow?: boolean) => void,
  ) {
    // Allow requests with no origin (like mobile apps or curl requests)
    if (!origin) return callback(null, true);

    const isDevelopment = envConfig.NODE_ENV === "development";
    const isLocalhost =
      origin.includes("localhost") || origin.includes("127.0.0.1");

    if (isDevelopment && isLocalhost) {
      return callback(null, true);
    }

    // Use environment-specific configuration
    if (appConfig.cors.origin === true) {
      return callback(null, true);
    }

    const allowedOrigins = Array.isArray(appConfig.cors.origin)
      ? appConfig.cors.origin
      : [];
    if (allowedOrigins.length === 0 || allowedOrigins.includes(origin)) {
      return callback(null, true);
    }

    logger.warn('CORS policy violation', { origin, allowedOrigins });
    callback(new Error("Not allowed by CORS"));
  },
  credentials: true,
  exposedHeaders: ["X-Request-ID"],
  maxAge: 86400, // 24 hours
};

app.use(cors(corsOptions));
app.use(bodyParser.json({ limit: "1mb" }));

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY! });

// Input validation middleware
const validateChatInput = (
  req: express.Request,
  res: express.Response,
  next: express.NextFunction,
) => {
  const { message } = req.body || {};

  if (!message || typeof message !== "string") {
    return res
      .status(400)
      .json({ error: "Message is required and must be a string" });
  }

  if (message.length > 1000) {
    return res
      .status(400)
      .json({ error: "Message too long (max 1000 characters)" });
  }

  if (message.trim().length === 0) {
    return res.status(400).json({ error: "Message cannot be empty" });
  }

  next();
};

// Rate limiting middleware
let requestCounts = new Map<string, { count: number; resetTime: number }>();
const rateLimit = (req: express.Request, res: express.Response, next: express.NextFunction) => {
  const ip = req.ip || 'unknown';
  const now = Date.now();
  const windowMs = appConfig.rateLimit.windowMs;
  const maxRequests = appConfig.rateLimit.maxRequests;

  const current = requestCounts.get(ip) || { count: 0, resetTime: now + windowMs };
  
  if (now > current.resetTime) {
    current.count = 0;
    current.resetTime = now + windowMs;
  }

  current.count++;
  requestCounts.set(ip, current);

  if (current.count > maxRequests) {
    logger.warn('Rate limit exceeded', { ip, count: current.count, maxRequests });
    metricsCollector.trackError('RateLimitError', '429', req.path);
    return res.status(429).json({ error: 'Too many requests' });
  }

  next();
};

app.use(rateLimit);

// Clean up old rate limit entries periodically
setInterval(() => {
  const now = Date.now();
  for (const [ip, data] of requestCounts.entries()) {
    if (now > data.resetTime) {
      requestCounts.delete(ip);
    }
  }
}, 300000); // Every 5 minutes

// Authentication middleware
const authenticateToken = async (req: express.Request, res: express.Response, next: express.NextFunction) => {
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  const isValid = await authService.validateToken(token);
  if (!isValid) {
    metricsCollector.trackError('AuthenticationError', '401', req.path);
    return res.status(401).json({ error: 'Invalid or expired token' });
  }

  next();
};

// Health check endpoint with enhanced metrics
app.get("/health", async (_req, res) => {
  const health = {
    ok: true,
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || "development",
    version: process.env.npm_package_version || "1.0.0",
    services: {
      openai: !!process.env.OPENAI_API_KEY,
      redis: await cacheManager.isConnected(),
      database: true, // Add actual database check if needed
    },
    metrics: metricsCollector.getHealthMetrics()
  };

  res.json(health);
});

// Readiness check for deployment platforms
app.get("/ready", async (_req, res) => {
  const checks = {
    redis: await cacheManager.isConnected(),
    // Add other readiness checks here
  };
  
  const ready = Object.values(checks).every(Boolean);
  res.status(ready ? 200 : 503).json({ ready, checks });
});

// Metrics endpoint
app.get("/metrics", async (_req, res) => {
  try {
    const metrics = await metricsCollector.getMetrics();
    res.set('Content-Type', 'text/plain').send(metrics);
  } catch (error) {
    logger.error('Failed to get metrics', { error });
    res.status(500).json({ error: 'Failed to get metrics' });
  }
});

// Chat endpoint with caching and improved error handling
app.post("/chat", validateChatInput, async (req, res) => {
  const jur = String(req.body?.jurisdiction || "");
  const gate = checkFeature(jur, "companion.therapy");
  if (!gate.allowed)
    return res.status(403).json({ error: "feature_unavailable", gate });

  try {
    const { message } = req.body;
    const cacheKey = `chat:${Buffer.from(message).toString('base64')}`;
    
    // Try to get cached response
    const cachedResponse = await cacheManager.get(cacheKey);
    if (cachedResponse) {
      logger.info('Chat response served from cache', { messageLength: message.length });
      return res.json(cachedResponse);
    }

    const r = await client.chat.completions.create({
      model: "gpt-4o-mini",
      temperature: 0.8,
      max_tokens: 500,
      messages: [
        {
          role: "system",
          content:
            "You are Nova, a warm, playful companion. Keep replies short and supportive.",
        },
        { role: "user", content: String(message || "") },
      ],
    });
    
    const text = r.choices?.[0]?.message?.content ?? "Try again?";
    const response = { text };
    
    // Cache the response for 5 minutes
    await cacheManager.set(cacheKey, response, 300);
    
    logger.info('Chat response generated and cached', { messageLength: message.length, responseLength: text.length });
    res.json(response);
  } catch (e: any) {
    logger.error("Chat error", { error: e.message, stack: e.stack });
    metricsCollector.trackError(e.name || 'ChatError', e.code || 'unknown', '/chat');
    res.status(500).json({ error: "chat_failed" });
  }
});

// Protected test endpoint
app.get("/protected", authenticateToken, (_req, res) => {
  res.json({ message: "Access granted to protected resource" });
});

// Raw body ONLY on webhook for Stripe signature
app.post(
  "/stripe/webhook",
  express.raw({ type: "application/json" }),
  (req, res, next) => next(),
);
app.use(billingRouter);

// Error handling middleware
app.use(ErrorHandler.notFound);
app.use(metricsCollector.createErrorMiddleware());
app.use(ErrorHandler.handle);

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  
  try {
    await Promise.all([
      cacheManager.cleanup(),
      authService.cleanup()
    ]);
    logger.info('Cleanup completed');
  } catch (error) {
    logger.error('Error during cleanup', { error });
  }
  
  process.exit(0);
});

const PORT = envConfig.PORT;
app.listen(PORT, () => {
  logger.info(`🚀 API server running on port ${PORT}`);
  logger.info(`📝 Environment: ${envConfig.NODE_ENV}`);
  logger.info(`🔒 CORS origins: ${JSON.stringify(appConfig.cors.origin)}`);
  logger.info(`⏱️  Rate limit: ${appConfig.rateLimit.maxRequests} requests per ${appConfig.rateLimit.windowMs / 1000 / 60} minutes`);
  logger.info('🎯 Enhanced features: Metrics, Caching, Security, Error Handling');
});

export { app };