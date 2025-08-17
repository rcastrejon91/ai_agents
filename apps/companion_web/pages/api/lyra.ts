import type { NextApiRequest, NextApiResponse } from "next";
import { scrubSecrets, rateLimit } from "../../lib/guardian";
import {
  validateLyraRequest,
  fetchWithRetry,
  sendErrorResponse,
  logRequest,
  generateRequestId,
  LyraResponse,
  ValidationError,
  UpstreamError,
  RateLimitError,
  TIMEOUT_CONFIG,
} from "../../lib/api-errors";
import { metricsCollector } from "../../lib/monitoring";

const LYRA_MODEL = "gpt-4o-mini";

// Enhanced Lyra API route with comprehensive error handling and monitoring
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const requestId = generateRequestId();
  const startTime = Date.now();
  let validatedRequest: any = null;

  try {
    // Method validation
    if (req.method !== "POST") {
      res.setHeader("Allow", ["POST"]);
      throw new ValidationError("Only POST method is allowed");
    }

    // Rate limiting
    const ip = (req.headers["x-forwarded-for"] as string) || req.socket.remoteAddress || "unknown";
    if (!rateLimit(ip, 30)) { // 30 requests per minute
      throw new RateLimitError("Too many requests. Please try again later.");
    }

    // Request validation
    validatedRequest = validateLyraRequest(req.body);
    const { message, history, model, temperature } = validatedRequest;

    // Tool inference based on message keywords
    const tools: string[] = [];
    if (/\btrial|study|paper|pubmed|openalex|arxiv\b/i.test(message))
      tools.push("Discovery");
    if (/\bcbc|cmp|hemoglobin|glucose|platelet|wbc\b/i.test(message))
      tools.push("Labs");
    if (/\bdispatch|deliver|runner|iv|rad|or-|code blue|ops\b/i.test(message))
      tools.push("Ops");
    if (tools.length === 0) tools.push("Chat");

    // Environment validation
    const key = process.env.OPENAI_API_KEY;
    if (!key) {
      console.error("[lyra] missing OPENAI_API_KEY");
      
      // Return demo response when no API key is configured
      const demoReply = `(demo mode) Using ${tools.join(" + ")} → ${message.substring(0, 100)}${message.length > 100 ? "..." : ""}`;
      const response: LyraResponse = {
        reply: demoReply,
        model: "demo",
        tools,
        timestamp: new Date().toISOString(),
        requestId,
      };
      
      res.status(200).json(response);
      
      // Record metrics
      const duration = Date.now() - startTime;
      metricsCollector.recordRequest("/api/lyra", "POST", 200, duration, undefined, undefined, requestId);
      
      await logRequest(req, res, undefined, duration, requestId);
      return;
    }

    // Health ping: allows quick health check without burning tokens
    if (req.query.ping) {
      const response: LyraResponse = {
        reply: "pong",
        model: "demo",
        tools: [],
        timestamp: new Date().toISOString(),
        requestId,
      };
      
      res.status(200).json(response);
      
      // Record metrics
      const duration = Date.now() - startTime;
      metricsCollector.recordRequest("/api/lyra", "POST", 200, duration, undefined, undefined, requestId);
      
      await logRequest(req, res, undefined, duration, requestId);
      return;
    }

    // Prepare messages for OpenAI
    const messages = [
      {
        role: "system",
        content: "You are Lyra, a concise, friendly assistant. Keep responses helpful and under 500 words.",
      },
      ...history,
      { role: "user", content: message },
    ];

    // Call OpenAI with retry logic and timeout
    const openaiRes = await fetchWithRetry(
      "https://api.openai.com/v1/chat/completions",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${key}`,
        },
        body: JSON.stringify({
          model: model || LYRA_MODEL,
          messages,
          temperature: temperature ?? 0.7,
          max_tokens: 500,
        }),
      },
      TIMEOUT_CONFIG.OPENAI,
      TIMEOUT_CONFIG.MAX_RETRIES
    );

    if (!openaiRes.ok) {
      let errorDetails: any = {};
      try {
        const errorText = await openaiRes.text();
        errorDetails = { 
          status: openaiRes.status, 
          statusText: openaiRes.statusText,
          body: errorText.substring(0, 500) // Limit error body size
        };
      } catch (err) {
        console.error("[lyra] failed to read error response body", err);
        errorDetails = { 
          status: openaiRes.status, 
          statusText: openaiRes.statusText 
        };
      }

      console.error("[lyra] OpenAI API error:", errorDetails);
      throw new UpstreamError(
        `OpenAI API request failed with status ${openaiRes.status}`,
        errorDetails
      );
    }

    // Parse OpenAI response
    let data: any;
    try {
      data = await openaiRes.json();
    } catch (err) {
      console.error("[lyra] failed to parse OpenAI response JSON", err);
      throw new UpstreamError("Invalid response format from OpenAI API");
    }

    // Extract and validate response
    const reply: string | undefined = data?.choices?.[0]?.message?.content?.trim();
    if (!reply) {
      console.error("[lyra] empty or invalid response from OpenAI", data);
      throw new UpstreamError("Empty response from OpenAI API", { 
        response: data 
      });
    }

    // Security: scrub any secrets from the response
    const safeReply = scrubSecrets(reply);
    
    // Prepare successful response
    const response: LyraResponse = {
      reply: safeReply,
      model: model || LYRA_MODEL,
      tools,
      timestamp: new Date().toISOString(),
      requestId,
    };

    res.status(200).json(response);
    
    // Record successful metrics
    const duration = Date.now() - startTime;
    metricsCollector.recordRequest("/api/lyra", "POST", 200, duration, undefined, undefined, requestId);
    
    // Log successful request
    await logRequest(req, res, undefined, duration, requestId);

  } catch (error: any) {
    console.error("[lyra] request failed:", {
      requestId,
      error: error.message,
      stack: error.stack,
      request: validatedRequest ? { message: validatedRequest.message?.substring(0, 100) } : null,
    });

    // Record error metrics
    const duration = Date.now() - startTime;
    const statusCode = error.statusCode || 500;
    metricsCollector.recordRequest(
      "/api/lyra", 
      "POST", 
      statusCode, 
      duration, 
      error.code || "UNKNOWN_ERROR",
      error.message,
      requestId
    );

    // Send standardized error response
    sendErrorResponse(res, error, requestId);
    
    // Log error
    await logRequest(req, res, error, duration, requestId);
  }
}
