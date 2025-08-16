import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import OpenAI from "openai";
import bodyParser from "body-parser";
import billingRouter from "./billing.js";
import { checkFeature } from "../../companion_web/server/compliance/check";

dotenv.config();
const app = express();

// JSON for normal routes
app.use(cors());
app.use(bodyParser.json());

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY! });

app.get("/health", (_req, res) => res.json({ ok: true }));

app.post("/chat", async (req, res) => {
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

const PORT = Number(process.env.PORT || 8787);
app.listen(PORT, () => console.log(`API on :${PORT}`));
