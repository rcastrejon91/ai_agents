import type { NextApiRequest, NextApiResponse } from "next";
import { metricsCollector, checkAlerts, monitorServiceHealth } from "../../lib/monitoring";
import { sendErrorResponse, generateRequestId, logRequest } from "../../lib/api-errors";

interface MonitoringResponse {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  requestId: string;
  metrics: Record<string, any>;
  healthChecks: Array<{
    service: string;
    healthy: boolean;
    latency?: number;
    error?: string;
  }>;
  alerts: Array<{
    type: string;
    message: string;
    severity: "warning" | "error" | "critical";
  }>;
  summary: {
    totalRequests: number;
    overallErrorRate: number;
    averageResponseTime: number;
    activeAlerts: number;
  };
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<MonitoringResponse>
) {
  const requestId = generateRequestId();
  const startTime = Date.now();

  try {
    if (req.method !== "GET") {
      res.setHeader("Allow", ["GET"]);
      return res.status(405).json({
        status: "unhealthy",
        timestamp: new Date().toISOString(),
        requestId,
        metrics: {},
        healthChecks: [],
        alerts: [],
        summary: {
          totalRequests: 0,
          overallErrorRate: 0,
          averageResponseTime: 0,
          activeAlerts: 0,
        },
      });
    }

    // Optional API key protection for monitoring endpoint
    const authHeader = req.headers.authorization;
    const expectedKey = process.env.MONITORING_API_KEY;
    
    if (expectedKey && (!authHeader || authHeader !== `Bearer ${expectedKey}`)) {
      return res.status(401).json({
        status: "unhealthy",
        timestamp: new Date().toISOString(),
        requestId,
        metrics: {},
        healthChecks: [],
        alerts: [],
        summary: {
          totalRequests: 0,
          overallErrorRate: 0,
          averageResponseTime: 0,
          activeAlerts: 0,
        },
      });
    }

    // Get all metrics
    const allMetrics = metricsCollector.getAllMetrics();
    
    // Run health checks
    const healthChecks = await monitorServiceHealth();
    
    // Collect all alerts
    const allAlerts: Array<{
      type: string;
      message: string;
      severity: "warning" | "error" | "critical";
    }> = [];
    
    for (const [key, metrics] of Object.entries(allMetrics)) {
      const alerts = checkAlerts(metrics);
      allAlerts.push(...alerts);
    }

    // Calculate summary statistics
    const summary = {
      totalRequests: Object.values(allMetrics).reduce((sum, m) => sum + m.totalRequests, 0),
      overallErrorRate: calculateOverallErrorRate(allMetrics),
      averageResponseTime: calculateOverallAverageResponseTime(allMetrics),
      activeAlerts: allAlerts.length,
    };

    // Determine overall status
    let overallStatus: "healthy" | "degraded" | "unhealthy" = "healthy";
    
    const criticalAlerts = allAlerts.filter(a => a.severity === "critical");
    const errorAlerts = allAlerts.filter(a => a.severity === "error");
    const unhealthyServices = healthChecks.filter(h => !h.healthy);

    if (criticalAlerts.length > 0 || unhealthyServices.length > 0) {
      overallStatus = "unhealthy";
    } else if (errorAlerts.length > 0 || summary.overallErrorRate > 2) {
      overallStatus = "degraded";
    }

    const response: MonitoringResponse = {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      requestId,
      metrics: allMetrics,
      healthChecks,
      alerts: allAlerts,
      summary,
    };

    // Set appropriate HTTP status
    const httpStatus = overallStatus === "healthy" ? 200 : 
                      overallStatus === "degraded" ? 200 : 503;

    res.status(httpStatus).json(response);

    // Log the monitoring request
    await logRequest(req, res, undefined, Date.now() - startTime, requestId);

  } catch (error: any) {
    console.error("[monitoring] Failed to generate monitoring report:", error);
    
    sendErrorResponse(res, error, requestId);
    await logRequest(req, res, error, Date.now() - startTime, requestId);
  }
}

function calculateOverallErrorRate(allMetrics: Record<string, any>): number {
  let totalRequests = 0;
  let totalFailures = 0;

  for (const metrics of Object.values(allMetrics)) {
    totalRequests += metrics.totalRequests;
    totalFailures += metrics.failedRequests;
  }

  return totalRequests > 0 ? (totalFailures / totalRequests) * 100 : 0;
}

function calculateOverallAverageResponseTime(allMetrics: Record<string, any>): number {
  const responseTimes = Object.values(allMetrics)
    .filter((m: any) => m.totalRequests > 0)
    .map((m: any) => m.averageResponseTime);

  return responseTimes.length > 0 
    ? responseTimes.reduce((sum: number, time: number) => sum + time, 0) / responseTimes.length 
    : 0;
}