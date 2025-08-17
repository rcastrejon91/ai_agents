// API Monitoring and Metrics Collection
import { GuardEvent, edgeLog } from "./guardian";

export interface MetricEvent {
  type: "request" | "error" | "performance" | "health";
  endpoint: string;
  method: string;
  statusCode?: number;
  duration?: number;
  errorCode?: string;
  errorMessage?: string;
  requestId?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface PerformanceMetrics {
  endpoint: string;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  p95ResponseTime: number;
  errorRate: number;
  lastError?: {
    code: string;
    message: string;
    timestamp: string;
  };
  uptime: number;
}

// In-memory metrics storage (in production, use Redis or similar)
class MetricsCollector {
  private metrics: Map<string, {
    requests: Array<{
      timestamp: number;
      duration: number;
      success: boolean;
      errorCode?: string;
      errorMessage?: string;
    }>;
    startTime: number;
  }> = new Map();

  constructor() {
    // Clean up old metrics every hour
    setInterval(() => this.cleanup(), 60 * 60 * 1000);
  }

  recordRequest(
    endpoint: string,
    method: string,
    statusCode: number,
    duration: number,
    errorCode?: string,
    errorMessage?: string,
    requestId?: string
  ) {
    const key = `${method}:${endpoint}`;
    const now = Date.now();
    
    if (!this.metrics.has(key)) {
      this.metrics.set(key, {
        requests: [],
        startTime: now,
      });
    }

    const endpointMetrics = this.metrics.get(key)!;
    endpointMetrics.requests.push({
      timestamp: now,
      duration,
      success: statusCode >= 200 && statusCode < 400,
      errorCode,
      errorMessage,
    });

    // Log metric event
    const metricEvent: MetricEvent = {
      type: statusCode >= 400 ? "error" : "request",
      endpoint,
      method,
      statusCode,
      duration,
      errorCode,
      errorMessage,
      requestId,
      timestamp: new Date().toISOString(),
    };

    this.logMetricEvent(metricEvent);
  }

  recordHealthCheck(
    endpoint: string,
    healthy: boolean,
    latency?: number,
    error?: string
  ) {
    const metricEvent: MetricEvent = {
      type: "health",
      endpoint,
      method: "GET",
      statusCode: healthy ? 200 : 503,
      duration: latency,
      errorMessage: error,
      timestamp: new Date().toISOString(),
      metadata: {
        healthy,
      },
    };

    this.logMetricEvent(metricEvent);
  }

  getMetrics(endpoint: string, method: string = "POST"): PerformanceMetrics {
    const key = `${method}:${endpoint}`;
    const endpointMetrics = this.metrics.get(key);

    if (!endpointMetrics) {
      return {
        endpoint,
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        averageResponseTime: 0,
        p95ResponseTime: 0,
        errorRate: 0,
        uptime: 0,
      };
    }

    const { requests, startTime } = endpointMetrics;
    const now = Date.now();
    
    // Filter recent requests (last 24 hours)
    const recentRequests = requests.filter(
      req => now - req.timestamp < 24 * 60 * 60 * 1000
    );

    const totalRequests = recentRequests.length;
    const successfulRequests = recentRequests.filter(req => req.success).length;
    const failedRequests = totalRequests - successfulRequests;
    
    const durations = recentRequests.map(req => req.duration);
    const averageResponseTime = durations.length > 0 
      ? durations.reduce((sum, duration) => sum + duration, 0) / durations.length 
      : 0;

    // Calculate 95th percentile
    const sortedDurations = durations.sort((a, b) => a - b);
    const p95Index = Math.floor(sortedDurations.length * 0.95);
    const p95ResponseTime = sortedDurations[p95Index] || 0;

    const errorRate = totalRequests > 0 ? (failedRequests / totalRequests) * 100 : 0;

    // Find last error
    const lastErrorRequest = recentRequests
      .filter(req => !req.success)
      .sort((a, b) => b.timestamp - a.timestamp)[0];

    const lastError = lastErrorRequest ? {
      code: lastErrorRequest.errorCode || "UNKNOWN_ERROR",
      message: lastErrorRequest.errorMessage || "Unknown error",
      timestamp: new Date(lastErrorRequest.timestamp).toISOString(),
    } : undefined;

    const uptime = Math.round((now - startTime) / 1000); // in seconds

    return {
      endpoint,
      totalRequests,
      successfulRequests,
      failedRequests,
      averageResponseTime: Math.round(averageResponseTime),
      p95ResponseTime: Math.round(p95ResponseTime),
      errorRate: Math.round(errorRate * 100) / 100,
      lastError,
      uptime,
    };
  }

  getAllMetrics(): Record<string, PerformanceMetrics> {
    const result: Record<string, PerformanceMetrics> = {};
    
    for (const key of Array.from(this.metrics.keys())) {
      const [method, endpoint] = key.split(':', 2);
      result[key] = this.getMetrics(endpoint, method);
    }

    return result;
  }

  private async logMetricEvent(event: MetricEvent) {
    try {
      // Log to console for debugging
      if (event.type === "error") {
        console.error(`[metrics] ${event.method} ${event.endpoint} failed:`, {
          statusCode: event.statusCode,
          duration: event.duration,
          error: event.errorMessage,
          requestId: event.requestId,
        });
      } else if (event.type === "performance" || event.duration! > 5000) {
        console.warn(`[metrics] Slow request ${event.method} ${event.endpoint}:`, {
          duration: event.duration,
          requestId: event.requestId,
        });
      }

      // Send to guardian logging system
      const guardEvent: GuardEvent = {
        event: `api_${event.type}`,
        path: event.endpoint,
        method: event.method,
        details: {
          statusCode: event.statusCode,
          duration: event.duration,
          errorCode: event.errorCode,
          errorMessage: event.errorMessage,
          requestId: event.requestId,
          ...event.metadata,
        },
      };

      await edgeLog(guardEvent);
    } catch (error) {
      // Don't let logging errors break the main flow
      console.error("[metrics] Failed to log metric event:", error);
    }
  }

  private cleanup() {
    const now = Date.now();
    const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days

    for (const key of Array.from(this.metrics.keys())) {
      const endpointMetrics = this.metrics.get(key)!;
      endpointMetrics.requests = endpointMetrics.requests.filter(
        req => now - req.timestamp < maxAge
      );

      // Remove endpoints with no recent requests
      if (endpointMetrics.requests.length === 0) {
        this.metrics.delete(key);
      }
    }
  }
}

// Global metrics collector instance
export const metricsCollector = new MetricsCollector();

// Monitoring middleware helper
export function createMonitoringMiddleware() {
  return (req: any, res: any, next: any) => {
    const startTime = Date.now();
    const originalSend = res.send;
    
    res.send = function(body: any) {
      const duration = Date.now() - startTime;
      const statusCode = res.statusCode;
      
      // Extract error information from response body if available
      let errorCode, errorMessage;
      if (statusCode >= 400 && body) {
        try {
          const parsedBody = typeof body === 'string' ? JSON.parse(body) : body;
          errorCode = parsedBody.code;
          errorMessage = parsedBody.message;
        } catch (e) {
          // Ignore parsing errors
        }
      }

      metricsCollector.recordRequest(
        req.path || req.url,
        req.method,
        statusCode,
        duration,
        errorCode,
        errorMessage,
        req.requestId
      );

      return originalSend.call(this, body);
    };

    next();
  };
}

// Health check monitoring
export async function monitorServiceHealth() {
  const services = [
    {
      name: "lyra-api",
      url: "/api/lyra",
      check: async () => {
        const start = Date.now();
        try {
          const response = await fetch("/api/lyra?ping=1", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: "ping" }),
          });
          
          const latency = Date.now() - start;
          const healthy = response.ok;
          
          metricsCollector.recordHealthCheck(
            "/api/lyra",
            healthy,
            latency,
            healthy ? undefined : `HTTP ${response.status}`
          );
          
          return { healthy, latency };
        } catch (error: any) {
          const latency = Date.now() - start;
          metricsCollector.recordHealthCheck("/api/lyra", false, latency, error.message);
          return { healthy: false, latency, error: error.message };
        }
      },
    },
  ];

  const results = await Promise.all(
    services.map(async service => {
      const result = await service.check();
      return {
        service: service.name,
        ...result,
      };
    })
  );

  return results;
}

// Alert thresholds
export const ALERT_THRESHOLDS = {
  ERROR_RATE: 5, // 5% error rate
  RESPONSE_TIME: 5000, // 5 seconds
  AVAILABILITY: 99, // 99% availability
};

// Check if alerts should be triggered
export function checkAlerts(metrics: PerformanceMetrics): Array<{
  type: string;
  message: string;
  severity: "warning" | "error" | "critical";
}> {
  const alerts: Array<{
    type: string;
    message: string;
    severity: "warning" | "error" | "critical";
  }> = [];

  if (metrics.errorRate > ALERT_THRESHOLDS.ERROR_RATE) {
    alerts.push({
      type: "HIGH_ERROR_RATE",
      message: `Error rate ${metrics.errorRate}% exceeds threshold ${ALERT_THRESHOLDS.ERROR_RATE}%`,
      severity: metrics.errorRate > ALERT_THRESHOLDS.ERROR_RATE * 2 ? "critical" : "error",
    });
  }

  if (metrics.p95ResponseTime > ALERT_THRESHOLDS.RESPONSE_TIME) {
    alerts.push({
      type: "SLOW_RESPONSE",
      message: `95th percentile response time ${metrics.p95ResponseTime}ms exceeds threshold ${ALERT_THRESHOLDS.RESPONSE_TIME}ms`,
      severity: "warning",
    });
  }

  const availability = (metrics.successfulRequests / Math.max(metrics.totalRequests, 1)) * 100;
  if (availability < ALERT_THRESHOLDS.AVAILABILITY) {
    alerts.push({
      type: "LOW_AVAILABILITY",
      message: `Availability ${availability.toFixed(2)}% below threshold ${ALERT_THRESHOLDS.AVAILABILITY}%`,
      severity: "critical",
    });
  }

  return alerts;
}