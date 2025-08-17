// API Error Handling Utilities for Lyra
import { NextApiRequest, NextApiResponse } from "next";
import { edgeLog, GuardEvent } from "./guardian";

// Custom error types
export class LyraAPIError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public readonly details?: Record<string, any>;
  public readonly isOperational: boolean;

  constructor(
    message: string,
    code: string,
    statusCode: number = 500,
    details?: Record<string, any>,
    isOperational: boolean = true
  ) {
    super(message);
    this.name = "LyraAPIError";
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
    this.isOperational = isOperational;
  }
}

export class ValidationError extends LyraAPIError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, "VALIDATION_ERROR", 400, details);
  }
}

export class UpstreamError extends LyraAPIError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, "UPSTREAM_ERROR", 502, details);
  }
}

export class TimeoutError extends LyraAPIError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, "TIMEOUT_ERROR", 504, details);
  }
}

export class RateLimitError extends LyraAPIError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, "RATE_LIMIT_ERROR", 429, details);
  }
}

// Standardized error response format
export interface ErrorResponse {
  error: string;
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
  requestId?: string;
}

// Request validation schema
export interface LyraRequest {
  message: string;
  history?: Array<{ role: string; content: string }>;
  model?: string;
  temperature?: number;
}

// Response format
export interface LyraResponse {
  reply: string;
  model: string;
  tools: string[];
  timestamp: string;
  requestId?: string;
}

// Timeout configuration
export const TIMEOUT_CONFIG = {
  DEFAULT: 30000, // 30 seconds
  OPENAI: 45000,  // 45 seconds for OpenAI calls
  RETRY_DELAY: 1000, // 1 second
  MAX_RETRIES: 3,
};

// Request validation
export function validateLyraRequest(body: any): LyraRequest {
  if (!body || typeof body !== "object") {
    throw new ValidationError("Request body must be a valid JSON object");
  }

  const { message, history, model, temperature } = body;

  if (!message || typeof message !== "string") {
    throw new ValidationError("Message is required and must be a string");
  }

  if (message.trim().length === 0) {
    throw new ValidationError("Message cannot be empty");
  }

  if (message.length > 10000) {
    throw new ValidationError("Message too long (max 10,000 characters)");
  }

  if (history && !Array.isArray(history)) {
    throw new ValidationError("History must be an array");
  }

  if (history && history.length > 50) {
    throw new ValidationError("History too long (max 50 messages)");
  }

  if (history) {
    for (const [index, msg] of history.entries()) {
      if (!msg || typeof msg !== "object") {
        throw new ValidationError(`History message at index ${index} must be an object`);
      }
      if (!msg.role || !msg.content) {
        throw new ValidationError(`History message at index ${index} must have role and content`);
      }
      if (!["user", "assistant", "system"].includes(msg.role)) {
        throw new ValidationError(`Invalid role "${msg.role}" at history index ${index}`);
      }
    }
  }

  if (model && typeof model !== "string") {
    throw new ValidationError("Model must be a string");
  }

  if (temperature !== undefined && (typeof temperature !== "number" || temperature < 0 || temperature > 2)) {
    throw new ValidationError("Temperature must be a number between 0 and 2");
  }

  return {
    message: message.trim(),
    history: history || [],
    model,
    temperature,
  };
}

// Fetch with timeout and retry logic
export async function fetchWithRetry(
  url: string,
  options: RequestInit,
  timeout: number = TIMEOUT_CONFIG.DEFAULT,
  maxRetries: number = TIMEOUT_CONFIG.MAX_RETRIES
): Promise<Response> {
  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      
      // Don't retry on 4xx client errors (except 429)
      if (response.status >= 400 && response.status < 500 && response.status !== 429) {
        return response;
      }

      // Return successful responses or non-retryable errors
      if (response.ok || attempt === maxRetries) {
        return response;
      }

      // Log retry attempt
      console.warn(`[api-retry] Attempt ${attempt + 1}/${maxRetries + 1} failed with status ${response.status}`);
      
    } catch (error: any) {
      clearTimeout(timeoutId);
      lastError = error;

      if (error.name === "AbortError") {
        lastError = new TimeoutError(`Request timed out after ${timeout}ms`);
      }

      // Don't retry on the last attempt
      if (attempt === maxRetries) {
        break;
      }

      console.warn(`[api-retry] Attempt ${attempt + 1}/${maxRetries + 1} failed:`, error.message);
    }

    // Wait before retrying (exponential backoff)
    if (attempt < maxRetries) {
      const delay = TIMEOUT_CONFIG.RETRY_DELAY * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError!;
}

// Error response handler
export function sendErrorResponse(
  res: NextApiResponse,
  error: Error,
  requestId?: string
): void {
  const timestamp = new Date().toISOString();
  
  if (error instanceof LyraAPIError) {
    const response: ErrorResponse = {
      error: "API Error",
      code: error.code,
      message: error.message,
      details: error.details,
      timestamp,
      requestId,
    };

    res.status(error.statusCode).json(response);
  } else {
    // Unexpected error - don't expose details
    const response: ErrorResponse = {
      error: "Internal Server Error",
      code: "INTERNAL_ERROR",
      message: "An unexpected error occurred",
      timestamp,
      requestId,
    };

    res.status(500).json(response);
  }
}

// Request logging
export async function logRequest(
  req: NextApiRequest,
  res: NextApiResponse,
  error?: Error,
  duration?: number,
  requestId?: string
): Promise<void> {
  const ip = (req.headers["x-forwarded-for"] as string) || req.socket.remoteAddress || null;
  const userAgent = req.headers["user-agent"] || null;
  
  const event: GuardEvent = {
    event: error ? "api_error" : "api_request",
    ip,
    path: req.url,
    method: req.method,
    user_agent: userAgent,
    details: {
      requestId,
      duration,
      statusCode: res.statusCode,
      error: error ? {
        message: error.message,
        code: error instanceof LyraAPIError ? error.code : "UNKNOWN_ERROR",
      } : undefined,
    },
  };

  await edgeLog(event);
}

// Generate request ID
export function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
}

// Health check helper
export interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  services: {
    openai: {
      status: "healthy" | "degraded" | "unhealthy";
      latency?: number;
      error?: string;
    };
    database?: {
      status: "healthy" | "degraded" | "unhealthy";
      latency?: number;
      error?: string;
    };
  };
  version: string;
}

export async function checkOpenAIHealth(): Promise<{ status: "healthy" | "degraded" | "unhealthy"; latency?: number; error?: string }> {
  const start = Date.now();
  try {
    const response = await fetchWithRetry(
      "https://api.openai.com/v1/models",
      {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        },
      },
      5000, // 5 second timeout for health check
      1 // No retries for health check
    );

    const latency = Date.now() - start;

    if (response.ok) {
      return { status: "healthy", latency };
    } else {
      return { 
        status: "degraded", 
        latency, 
        error: `HTTP ${response.status}` 
      };
    }
  } catch (error: any) {
    return { 
      status: "unhealthy", 
      error: error.message 
    };
  }
}