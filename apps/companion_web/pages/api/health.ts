import type { NextApiRequest, NextApiResponse } from "next";
import { 
  HealthStatus, 
  checkOpenAIHealth, 
  sendErrorResponse, 
  logRequest, 
  generateRequestId 
} from "../../lib/api-errors";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<HealthStatus>
) {
  const requestId = generateRequestId();
  const startTime = Date.now();

  try {
    if (req.method !== "GET") {
      res.setHeader("Allow", ["GET"]);
      return res.status(405).json({
        status: "unhealthy",
        timestamp: new Date().toISOString(),
        services: {
          openai: { status: "unhealthy", error: "Method not allowed" }
        },
        version: process.env.npm_package_version || "unknown"
      });
    }

    // Check OpenAI service health
    const openaiHealth = await checkOpenAIHealth();
    
    // Determine overall health status
    let overallStatus: "healthy" | "degraded" | "unhealthy" = "healthy";
    
    if (openaiHealth.status === "unhealthy") {
      overallStatus = "unhealthy";
    } else if (openaiHealth.status === "degraded") {
      overallStatus = "degraded";
    }

    const healthStatus: HealthStatus = {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      services: {
        openai: openaiHealth,
      },
      version: process.env.npm_package_version || "unknown",
    };

    // Set appropriate HTTP status code
    const httpStatus = overallStatus === "healthy" ? 200 : 
                      overallStatus === "degraded" ? 200 : 503;

    res.status(httpStatus).json(healthStatus);

    // Log the health check
    await logRequest(req, res, undefined, Date.now() - startTime, requestId);

  } catch (error: any) {
    console.error("[health] Health check failed:", error);
    
    const healthStatus: HealthStatus = {
      status: "unhealthy",
      timestamp: new Date().toISOString(),
      services: {
        openai: { status: "unhealthy", error: "Health check failed" }
      },
      version: process.env.npm_package_version || "unknown",
    };

    res.status(503).json(healthStatus);
    
    // Log the error
    await logRequest(req, res, error, Date.now() - startTime, requestId);
  }
}