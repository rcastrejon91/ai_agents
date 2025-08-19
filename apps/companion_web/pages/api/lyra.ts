import type { NextApiRequest, NextApiResponse } from "next";
import { scrubSecrets } from "../../lib/guardian";
import {
  withSecurity,
  sanitizeInput,
  sanitizeApiBody,
} from "../../lib/security";
import { logger } from "../../lib/logger";

const LYRA_MODEL = "gpt-4o-mini";

// Minimal Lyra API route that validates env wiring and proxies to OpenAI.
async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Validate and sanitize request body
    const body = sanitizeApiBody(req.body || {}, {
      message: { type: "string", maxLength: 2000, required: true },
      history: { type: "array" },
    });

    const message = body.message || "";
    const history = Array.isArray(body.history) ? body.history.slice(-10) : []; // Limit history

    if (!message) {
      logger.warn("Empty message received", { ip: req.socket.remoteAddress });
      return res.status(400).json({ error: "Message is required" });
    }

    // Sanitize history items
    const sanitizedHistory = history
      .filter(
        (item: any) =>
          item && typeof item === "object" && item.role && item.content
      )
      .map((item: any) => ({
        role: ["user", "assistant"].includes(item.role) ? item.role : "user",
        content: sanitizeInput(String(item.content), 1000),
      }));

    // naive tool inference: pick tools based on message keywords
    const tools: string[] = [];
    if (/\btrial|study|paper|pubmed|openalex|arxiv\b/i.test(message))
      tools.push("Discovery");
    if (/\bcbc|cmp|hemoglobin|glucose|platelet|wbc\b/i.test(message))
      tools.push("Labs");
    if (/\bdispatch|deliver|runner|iv|rad|or-|code blue|ops\b/i.test(message))
      tools.push("Ops");
    if (tools.length === 0) tools.push("Chat");

    // Health ping: allows ?ping=1 check without burning tokens
    if (req.query.ping) {
      return res.status(200).json({ reply: "pong", model: "demo", tools });
    }

    // Call OpenAI
    logger.info("Making OpenAI request", {
      messageLength: message.length,
      tools,
      historyLength: sanitizedHistory.length,
    });

    const openaiRes = await fetch(
      "https://api.openai.com/v1/chat/completions",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${key}`,
        },
        body: JSON.stringify({
          model: LYRA_MODEL,
          messages: [
            {
              role: "system",
              content: "You are Lyra, a concise, friendly assistant.",
            },
            ...sanitizedHistory,
            { role: "user", content: message },
          ],
        }),
      }
    );

    if (!openaiRes.ok) {
      let errText = "";
      try {
        errText = await openaiRes.text();
      } catch (err) {
        logger.error("Failed to read error body", { error: err });
        errText = "";
      }
      logger.error("OpenAI upstream error", {
        status: openaiRes.status,
        error: errText,
      });
      return res.status(502).json({ error: "Upstream error." });
    }

    const data = (await openaiRes.json()) as any;
    const reply: string | undefined =
      data?.choices?.[0]?.message?.content?.trim();
    const safeReply = scrubSecrets(
      reply ?? "I'm not sure what to say, but I'm here!"
    );

    logger.info("Successful OpenAI response", {
      replyLength: safeReply.length,
      model: LYRA_MODEL,
    });

    return res.status(200).json({ reply: safeReply, model: LYRA_MODEL, tools });
  } catch (e: any) {
    logger.error("Lyra API exception", {
      error: e?.message || e,
      stack: e?.stack,
    });
    return res.status(500).json({ error: "Server error." });
  }
}

// Export secured handler with rate limiting and method validation
export default withSecurity(handler, {
  allowedMethods: ["POST"],
  rateLimit: {
    max: 20, // 20 requests
    windowMs: 60 * 1000, // per minute
  },
  maxBodySize: 10000, // 10KB max body size
});
