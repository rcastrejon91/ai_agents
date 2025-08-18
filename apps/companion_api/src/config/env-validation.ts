/**
 * Environment variable validation and configuration
 */

interface EnvConfig {
  OPENAI_API_KEY: string;
  PORT: number;
  NODE_ENV: string;
  ALLOWED_ORIGINS?: string;
  STRIPE_SECRET_KEY?: string;
  STRIPE_WEBHOOK_SECRET?: string;
  // Backend URL configuration
  NEXT_PUBLIC_API_URL?: string;
  BACKEND_URL?: string;
  // Domain configuration
  NEXT_PUBLIC_BASE_URL?: string;
  NEXT_PUBLIC_APP_DOMAIN?: string;
  // Security configuration
  ORIGIN?: string;
  RP_ID?: string;
  // Admin configuration
  ADMIN_DASH_KEY?: string;
}

/**
 * Validates required environment variables
 */
export function validateEnvironment(): EnvConfig {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Required variables
  const requiredVars = ["OPENAI_API_KEY"];

  requiredVars.forEach((varName) => {
    if (!process.env[varName]) {
      errors.push(`${varName} is required`);
    }
  });

  // Validate OpenAI API key format
  if (
    process.env.OPENAI_API_KEY &&
    !process.env.OPENAI_API_KEY.startsWith("sk-")
  ) {
    errors.push('OPENAI_API_KEY must start with "sk-"');
  }

  // Validate PORT
  const port = parseInt(process.env.PORT || "8787", 10);
  if (isNaN(port) || port < 1 || port > 65535) {
    errors.push("PORT must be a valid port number (1-65535)");
  }

  // Validate NODE_ENV
  const validEnvs = ["development", "staging", "production"];
  const nodeEnv = process.env.NODE_ENV || "development";
  if (!validEnvs.includes(nodeEnv)) {
    errors.push(`NODE_ENV must be one of: ${validEnvs.join(", ")}`);
  }

  // Environment-specific validation
  if (nodeEnv === "production") {
    // Production-specific validations
    if (!process.env.ALLOWED_ORIGINS) {
      errors.push("ALLOWED_ORIGINS is required in production");
    } else {
      // Validate that production origins use HTTPS
      const origins = process.env.ALLOWED_ORIGINS.split(",").map(o => o.trim());
      origins.forEach(origin => {
        if (origin && !origin.startsWith("https://") && origin !== "localhost") {
          warnings.push(`Production origin should use HTTPS: ${origin}`);
        }
      });
    }

    // Validate backend URLs for production
    if (process.env.NEXT_PUBLIC_API_URL && !process.env.NEXT_PUBLIC_API_URL.startsWith("https://")) {
      warnings.push("NEXT_PUBLIC_API_URL should use HTTPS in production");
    }
    
    if (process.env.NEXT_PUBLIC_BASE_URL && !process.env.NEXT_PUBLIC_BASE_URL.startsWith("https://")) {
      warnings.push("NEXT_PUBLIC_BASE_URL should use HTTPS in production");
    }

    // Check WebAuthn configuration for production
    if (process.env.ORIGIN && !process.env.ORIGIN.startsWith("https://")) {
      warnings.push("ORIGIN should use HTTPS in production for WebAuthn");
    }
  }

  // URL validation helpers
  const validateUrl = (url: string, name: string) => {
    try {
      new URL(url);
    } catch {
      errors.push(`${name} must be a valid URL: ${url}`);
    }
  };

  // Validate URL formats if provided
  if (process.env.NEXT_PUBLIC_API_URL) {
    validateUrl(process.env.NEXT_PUBLIC_API_URL, "NEXT_PUBLIC_API_URL");
  }
  
  if (process.env.BACKEND_URL) {
    validateUrl(process.env.BACKEND_URL, "BACKEND_URL");
  }
  
  if (process.env.NEXT_PUBLIC_BASE_URL) {
    validateUrl(process.env.NEXT_PUBLIC_BASE_URL, "NEXT_PUBLIC_BASE_URL");
  }

  if (process.env.ORIGIN) {
    validateUrl(process.env.ORIGIN, "ORIGIN");
  }

  // Print warnings
  if (warnings.length > 0) {
    console.warn("⚠️  Environment validation warnings:");
    warnings.forEach((warning) => console.warn(`  ⚠️  ${warning}`));
  }

  if (errors.length > 0) {
    console.error("Environment validation failed:");
    errors.forEach((error) => console.error(`  ❌ ${error}`));
    process.exit(1);
  }

  console.log("✅ Environment validation passed");

  return {
    OPENAI_API_KEY: process.env.OPENAI_API_KEY!,
    PORT: port,
    NODE_ENV: nodeEnv,
    ALLOWED_ORIGINS: process.env.ALLOWED_ORIGINS,
    STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET: process.env.STRIPE_WEBHOOK_SECRET,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    BACKEND_URL: process.env.BACKEND_URL,
    NEXT_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_BASE_URL,
    NEXT_PUBLIC_APP_DOMAIN: process.env.NEXT_PUBLIC_APP_DOMAIN,
    ORIGIN: process.env.ORIGIN,
    RP_ID: process.env.RP_ID,
    ADMIN_DASH_KEY: process.env.ADMIN_DASH_KEY,
  };
}

/**
 * Get configuration for specific environment
 */
export function getEnvironmentConfig() {
  const env = process.env.NODE_ENV || "development";

  // Default backend URLs based on environment
  const getBackendUrl = () => {
    if (process.env.NEXT_PUBLIC_API_URL) {
      return process.env.NEXT_PUBLIC_API_URL;
    }
    
    switch (env) {
      case "production":
        return "https://api.yourdomain.com"; // Should be overridden in production
      case "staging":
        return "https://api-staging.yourdomain.com"; // Should be overridden in staging
      default:
        return "http://localhost:8787";
    }
  };

  const baseConfig = {
    development: {
      cors: {
        origin: true, // Allow all origins in development
        credentials: true,
      },
      rateLimit: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        maxRequests: 1000, // More lenient in development
      },
      backendUrl: getBackendUrl(),
      securityLevel: "low",
    },
    staging: {
      cors: {
        origin: (process.env.ALLOWED_ORIGINS || "").split(",").filter(Boolean),
        credentials: true,
      },
      rateLimit: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        maxRequests: 200,
      },
      backendUrl: getBackendUrl(),
      securityLevel: "medium",
    },
    production: {
      cors: {
        origin: (process.env.ALLOWED_ORIGINS || "").split(",").filter(Boolean),
        credentials: true,
      },
      rateLimit: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        maxRequests: 100, // Strict in production
      },
      backendUrl: getBackendUrl(),
      securityLevel: "high",
    },
  };

  return baseConfig[env as keyof typeof baseConfig] || baseConfig.development;
}

/**
 * Get environment-specific URLs for frontend
 */
export function getEnvironmentUrls() {
  const env = process.env.NODE_ENV || "development";
  
  return {
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 
            (env === "production" ? "https://api.yourdomain.com" : "http://localhost:8787"),
    baseUrl: process.env.NEXT_PUBLIC_BASE_URL || 
             (env === "production" ? "https://yourdomain.com" : "http://localhost:3000"),
    backendUrl: process.env.BACKEND_URL || 
                (env === "production" ? "https://api.yourdomain.com" : "http://localhost:5000"),
    domain: process.env.NEXT_PUBLIC_APP_DOMAIN || 
            (env === "production" ? "yourdomain.com" : "localhost:3000"),
  };
}
