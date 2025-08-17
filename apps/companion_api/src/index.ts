import express from "express";
import dotenv from "dotenv";
import OpenAI from "openai";
import bodyParser from "body-parser";
import billingRouter from "./billing.js";
import { checkFeature } from "../../companion_web/server/compliance/check";
import { getConfig } from "./config/env.js";
import { 
  createRateLimiter, 
  createCorsMiddleware, 
  createHelmetMiddleware, 
  requestIdMiddleware,
  AuthenticatedRequest 
} from "./middleware/security.js";
import { jwtAuthMiddleware, optionalJwtAuthMiddleware } from "./middleware/auth.js";
import { errorHandler, notFoundHandler, AppError, asyncHandler, logger } from "./middleware/error.js";
import { createAuthRoutes } from "./routes/auth.js";

dotenv.config();

// Initialize configuration and validate environment
const config = getConfig();
const app = express();

// Security middleware
app.use(createHelmetMiddleware());
app.use(requestIdMiddleware);
app.use(createRateLimiter(config));
app.use(createCorsMiddleware(config));

// JSON parsing for normal routes
app.use(bodyParser.json());

// Initialize OpenAI client
const client = new OpenAI({ apiKey: config.openai.apiKey });

// Auth routes (no authentication required)
app.use('/auth', createAuthRoutes(config));

// Health check (no authentication required)
app.get("/health", (_req, res) => res.json({ ok: true, timestamp: new Date().toISOString() }));

// Chat endpoint with optional authentication
app.post("/chat", optionalJwtAuthMiddleware(config), asyncHandler(async (req: AuthenticatedRequest, res: express.Response) => {
  const jur = String(req.body?.jurisdiction || "");
  const gate = checkFeature(jur, "companion.therapy");
  if (!gate.allowed)
    return res.status(403).json({ 
      error: "feature_unavailable", 
      gate,
      requestId: req.id 
    });

  const { message } = req.body || {};
  if (!message) {
    throw new AppError('Message is required', 400, 'MISSING_MESSAGE');
  }

  logger.info({
    event: 'chat_request',
    userId: req.user?.userId || 'anonymous',
    jurisdiction: jur,
    requestId: req.id
  });

  const r = await client.chat.completions.create({
    model: "gpt-4o-mini",
    temperature: 0.8,
    messages: [
      {
        role: "system",
        content: "You are Nova, a warm, playful companion. Keep replies short and supportive.",
      },
      { role: "user", content: String(message || "") },
    ],
  });
  
  const text = r.choices?.[0]?.message?.content ?? "Try again?";
  res.json({ 
    text,
    requestId: req.id
  });
}));

// Raw body ONLY on webhook for Stripe signature
app.post(
  "/stripe/webhook",
  express.raw({ type: "application/json" }),
  (req, res, next) => next(),
);
app.use(billingRouter);

// 404 handler
app.use(notFoundHandler);

// Global error handler (must be last)
app.use(errorHandler);

const PORT = config.port;
app.listen(PORT, () => {
  logger.info({
    message: `API server started on port ${PORT}`,
    environment: config.nodeEnv,
    port: PORT,
    timestamp: new Date().toISOString()
  });
});
