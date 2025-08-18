import type { NextApiRequest, NextApiResponse } from "next";

// Simple health check for external APIs
async function healthCheck(url: string): Promise<boolean> {
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
    console.warn(`Health check failed for ${url}`, error);
    return false;
  }
}

export default async function handler(
  _req: NextApiRequest,
  res: NextApiResponse,
) {
  try {
    const nodeEnv = process.env.NODE_ENV || "development";
    const openaiKey = process.env.OPENAI_API_KEY;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    
    // Check external service health
    const openaiHealthy = openaiKey 
      ? await healthCheck("https://api.openai.com/")
      : false;

    const companionApiHealthy = apiUrl
      ? await healthCheck(apiUrl)
      : false;

    const health = {
      ok: true,
      timestamp: new Date().toISOString(),
      environment: nodeEnv,
      version: process.env.npm_package_version || "1.0.0",
      services: {
        openai: openaiHealthy,
        companion_api: companionApiHealthy,
        env_validation: true,
      },
      config: {
        api_url: apiUrl,
        base_url: process.env.NEXT_PUBLIC_BASE_URL,
        has_openai_key: !!openaiKey,
        has_api_secret: !!process.env.API_SECRET_KEY,
      },
    };

    // Overall health status
    const allServicesHealthy = Object.values(health.services).every(Boolean);
    if (!allServicesHealthy) {
      health.ok = false;
      res.status(503);
    }

    console.log("Health check performed", { 
      services: health.services,
      environment: nodeEnv,
    });

    res.json(health);
  } catch (error) {
    console.error("Health check failed", error);
    
    res.status(500).json({
      ok: false,
      timestamp: new Date().toISOString(),
      error: "Health check failed",
      message: (error as Error).message,
    });
  }
}