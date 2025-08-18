import type { NextApiRequest, NextApiResponse } from "next";
import { withSecurity } from "../../lib/security";

function getWebEnvironmentConfig() {
  const env = process.env.NODE_ENV || "development";

  const baseConfig = {
    development: {
      apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8787",
      baseUrl: process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000",
      cors: {
        origin: true, // Allow all origins in development
        credentials: true,
      },
    },
    staging: {
      apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8787",
      baseUrl: process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000",
      cors: {
        origin: (process.env.ALLOWED_ORIGINS || "").split(",").filter(Boolean),
        credentials: true,
      },
    },
    production: {
      apiUrl: process.env.NEXT_PUBLIC_API_URL,
      baseUrl: process.env.NEXT_PUBLIC_BASE_URL,
      cors: {
        origin: (process.env.ALLOWED_ORIGINS || "").split(",").filter(Boolean),
        credentials: true,
      },
    },
  };

  return baseConfig[env as keyof typeof baseConfig] || baseConfig.development;
}

async function handler(_req: NextApiRequest, res: NextApiResponse) {
  const config = getWebEnvironmentConfig();
  
  // Return configuration without sensitive information
  res.json({
    environment: process.env.NODE_ENV || "development",
    api_url: config.apiUrl,
    base_url: config.baseUrl,
    features: {
      openai_available: !!process.env.OPENAI_API_KEY,
      api_secret_configured: !!process.env.API_SECRET_KEY,
      cors_configured: !!process.env.ALLOWED_ORIGINS,
    },
    cors: {
      allowed_origins: config.cors.origin === true ? "all (development)" : config.cors.origin,
      credentials: config.cors.credentials,
    },
  });
}

// Export with rate limiting to prevent abuse
export default withSecurity(handler, {
  allowedMethods: ["GET"],
  rateLimit: {
    max: 10, // 10 requests
    windowMs: 60 * 1000, // per minute
  },
});