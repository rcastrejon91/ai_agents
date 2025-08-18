import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import OpenAI from "openai";
import bodyParser from "body-parser";
import billingRouter from "./billing.js";
import { checkFeature } from "../../companion_web/server/compliance/check";
import {
  validateEnvironment,
  getEnvironmentConfig,
  getEnvironmentUrls,
} from "./config/env-validation.js";

dotenv.config();

// Validate environment variables on startup
const envConfig = validateEnvironment();
const appConfig = getEnvironmentConfig();
const urlConfig = getEnvironmentUrls();

const app = express();

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

    callback(new Error("Not allowed by CORS"));
  },
  credentials: appConfig.cors.credentials,
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization", "X-Requested-With"],
  exposedHeaders: ["X-Total-Count"],
  maxAge: 86400, // 24 hours
};

app.use(cors(corsOptions));

// Rate limiting and security middleware
const rateLimit = new Map<string, { count: number; resetTime: number }>();

app.use((req, res, next) => {
  const ip =
    (req.headers["x-forwarded-for"] as string) ||
    (req.headers["x-real-ip"] as string) ||
    req.connection.remoteAddress ||
    "unknown";
  const now = Date.now();

  const current = rateLimit.get(ip);
  if (!current || now > current.resetTime) {
    rateLimit.set(ip, {
      count: 1,
      resetTime: now + appConfig.rateLimit.windowMs,
    });
  } else {
    current.count++;
    if (current.count > appConfig.rateLimit.maxRequests) {
      return res.status(429).json({ error: "Too many requests" });
    }
  }

  // Security headers
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("X-XSS-Protection", "1; mode=block");
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  res.setHeader(
    "Permissions-Policy",
    "geolocation=(), microphone=(), camera=()",
  );

  next();
});

// JSON body parser with size limit
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

// Enhanced health check endpoint
app.get("/health", (_req, res) => {
  const health = {
    ok: true,
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || "development",
    version: process.env.npm_package_version || "1.0.0",
    services: {
      openai: !!process.env.OPENAI_API_KEY,
      database: true, // Add actual database check if needed
    },
  };

  res.json(health);
});

// Readiness check for deployment platforms
app.get("/ready", (_req, res) => {
  // Add any readiness checks here (database connections, etc.)
  res.json({ ready: true });
});

app.post("/chat", validateChatInput, async (req, res) => {
  const jur = String(req.body?.jurisdiction || "");
  const gate = checkFeature(jur, "companion.therapy");
  if (!gate.allowed)
    return res.status(403).json({ error: "feature_unavailable", gate });

  try {
    const { message } = req.body;
    const r = await client.chat.completions.create({
      model: "gpt-4o-mini",
      temperature: 0.8,
      max_tokens: 500, // Limit response length
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
    res.json({ text });
  } catch (e: any) {
    console.error("Chat error:", e);
    res.status(500).json({ error: "chat_failed" });
  }
});

// Raw body ONLY on webhook for Stripe signature
app.post(
  "/stripe/webhook",
  express.raw({ type: "application/json" }),
  (req, res, next) => next(),
);
app.use(billingRouter);

const PORT = envConfig.PORT;
app.listen(PORT, () => {
  console.log(`🚀 API server running on port ${PORT}`);
  console.log(`📝 Environment: ${envConfig.NODE_ENV}`);
  console.log(`🌐 Backend URL: ${urlConfig.backendUrl}`);
  console.log(`🌐 API URL: ${urlConfig.apiUrl}`);
  console.log(`🔒 CORS origins: ${JSON.stringify(appConfig.cors.origin)}`);
  console.log(`🔒 Security level: ${appConfig.securityLevel}`);
  console.log(
    `⏱️  Rate limit: ${appConfig.rateLimit.maxRequests} requests per ${appConfig.rateLimit.windowMs / 1000 / 60} minutes`,
  );
});
