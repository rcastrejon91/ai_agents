/**
 * API utilities for reliable external API calls with retry logic
 */

import { logger } from "./logger";

export interface RetryConfig {
  maxRetries?: number;
  baseDelay?: number;
  maxDelay?: number;
  retryOn?: number[];
  timeout?: number;
}

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
  success: boolean;
}

/**
 * Sleep utility for retry delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Calculate exponential backoff delay
 */
function calculateDelay(attempt: number, baseDelay: number, maxDelay: number): number {
  const delay = baseDelay * Math.pow(2, attempt);
  return Math.min(delay, maxDelay);
}

/**
 * Fetch with retry logic and timeout handling
 */
export async function fetchWithRetry<T = any>(
  url: string,
  options: RequestInit = {},
  config: RetryConfig = {}
): Promise<ApiResponse<T>> {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 10000,
    retryOn = [429, 500, 502, 503, 504],
    timeout = 30000,
  } = config;

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Add timeout to fetch
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // If response is ok or not retryable, return result
      if (response.ok) {
        const data = await response.json();
        return {
          data,
          status: response.status,
          success: true,
        };
      }

      // If not retryable status, return error immediately
      if (!retryOn.includes(response.status)) {
        const errorText = await response.text();
        return {
          error: errorText || `HTTP ${response.status}`,
          status: response.status,
          success: false,
        };
      }

      // Log retry attempt
      logger.warn(`API call failed, attempt ${attempt + 1}/${maxRetries + 1}`, {
        url,
        status: response.status,
        attempt: attempt + 1,
      });

      lastError = new Error(`HTTP ${response.status}`);

    } catch (error: any) {
      lastError = error;
      
      // If it's an abort error (timeout), don't retry
      if (error.name === 'AbortError') {
        logger.error('API call timed out', { url, timeout });
        return {
          error: 'Request timeout',
          status: 408,
          success: false,
        };
      }

      logger.warn(`API call failed with error, attempt ${attempt + 1}/${maxRetries + 1}`, {
        url,
        error: error.message,
        attempt: attempt + 1,
      });
    }

    // If not the last attempt, wait before retrying
    if (attempt < maxRetries) {
      const delay = calculateDelay(attempt, baseDelay, maxDelay);
      logger.info(`Retrying API call in ${delay}ms`, { url, attempt: attempt + 1 });
      await sleep(delay);
    }
  }

  // All retries failed
  logger.error(`API call failed after ${maxRetries + 1} attempts`, {
    url,
    error: lastError?.message,
  });

  return {
    error: lastError?.message || 'Request failed after retries',
    status: 500,
    success: false,
  };
}

/**
 * Make OpenAI API call with retry logic
 */
export async function callOpenAI(
  apiKey: string,
  body: any,
  config: RetryConfig = {}
): Promise<ApiResponse> {
  return fetchWithRetry(
    'https://api.openai.com/v1/chat/completions',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify(body),
    },
    {
      maxRetries: 2,
      baseDelay: 1000,
      ...config,
    }
  );
}

/**
 * Health check for external APIs
 */
export async function healthCheck(url: string): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(url, {
      method: 'HEAD',
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return response.ok;
  } catch (error) {
    logger.warn(`Health check failed for ${url}`, { error: (error as Error).message });
    return false;
  }
}