import express from "express";
import dotenv from "dotenv";
import OpenAI from "openai";
import bodyParser from "body-parser";
import billingRouter from "./billing.js";
import { checkFeature } from "../../companion_web/server/compliance/check";
import settings from "./config";
import {
  corsMiddleware,
  securityMiddleware,
  requestLoggingMiddleware,
  errorHandlingMiddleware,
  validateJSON,
  getClientIP
} from "./middleware";

dotenv.config();
const app = express();
const config = settings.get();

// Security and logging middleware
app.use(corsMiddleware());
app.use(bodyParser.json({ limit: config.security.maxRequestSize }));
app.use(securityMiddleware);
app.use(requestLoggingMiddleware);

const client = new OpenAI({ apiKey: config.api.openaiApiKey! });

// Enhanced health check endpoint
app.get("/health", (req, res) => {
  const healthStatus = {
    status: "healthy",
    timestamp: new Date().toISOString(),
    environment: config.environment,
    version: "1.0.0",
    checks: {
      openai: {
        status: config.api.openaiApiKey ? "configured" : "missing",
        message: config.api.openaiApiKey ? "API key configured" : "OpenAI API key not configured"
      },
      stripe: {
        status: config.api.stripeSecretKey ? "configured" : "missing",
        message: config.api.stripeSecretKey ? "API key configured" : "Stripe API key not configured"
      }
    },
    settings: {
      cors_origins: config.security.corsOrigins,
      rate_limit: config.security.rateLimitPerMinute,
      max_request_size: config.security.maxRequestSize
    }
  };
  
  res.json(healthStatus);
});

// System metrics endpoint
app.get("/metrics", (req, res) => {
  const metrics = {
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    cpu: process.cpuUsage(),
    timestamp: new Date().toISOString(),
    environment: config.environment
  };
  
  res.json(metrics);
});

app.post("/chat", validateJSON(["message"]), async (req, res) => {
  const jur = String(req.body?.jurisdiction || "");
  const gate = checkFeature(jur, "companion.therapy");
  if (!gate.allowed)
    return res.status(403).json({ error: "feature_unavailable", gate });
  try {
    const { message } = req.body || {};
    const r = await client.chat.completions.create({
      model: "gpt-4o-mini",
      temperature: 0.8,
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
    console.error(e);
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

// Error handling middleware (must be last)
app.use(errorHandlingMiddleware);

const PORT = Number(process.env.PORT || config.api.timeout || 8787);

app.listen(PORT, () => {
  console.log(`🚀 Companion API server running on port ${PORT}`);
  console.log(`📊 Environment: ${config.environment}`);
  console.log(`🔒 Security: Rate limit ${config.security.rateLimitPerMinute}/min`);
  console.log(`🌐 CORS: ${config.security.corsOrigins.join(", ")}`);
  
  if (config.debug) {
    console.log("🐛 Debug mode enabled");
  }
});
