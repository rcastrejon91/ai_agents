/**
 * Environment configuration utilities for the web app
 */

export interface WebEnvConfig {
  NODE_ENV: string;
  NEXT_PUBLIC_API_URL?: string;
  NEXT_PUBLIC_BASE_URL?: string;
  NEXT_PUBLIC_APP_DOMAIN?: string;
  ORIGIN?: string;
  RP_ID?: string;
  ALLOWED_ORIGINS?: string;
}

/**
 * Validates environment variables for the web app
 */
export function validateWebEnvironment(): WebEnvConfig {
  const errors: string[] = [];
  const warnings: string[] = [];

  const nodeEnv = process.env.NODE_ENV || "development";
  const validEnvs = ["development", "staging", "production"];
  
  if (!validEnvs.includes(nodeEnv)) {
    errors.push(`NODE_ENV must be one of: ${validEnvs.join(", ")}`);
  }

  // Environment-specific validation
  if (nodeEnv === "production") {
    // Production-specific validations
    if (!process.env.NEXT_PUBLIC_API_URL) {
      warnings.push("NEXT_PUBLIC_API_URL should be set in production");
    } else if (!process.env.NEXT_PUBLIC_API_URL.startsWith("https://")) {
      warnings.push("NEXT_PUBLIC_API_URL should use HTTPS in production");
    }

    if (!process.env.NEXT_PUBLIC_BASE_URL) {
      warnings.push("NEXT_PUBLIC_BASE_URL should be set in production");
    } else if (!process.env.NEXT_PUBLIC_BASE_URL.startsWith("https://")) {
      warnings.push("NEXT_PUBLIC_BASE_URL should use HTTPS in production");
    }

    // WebAuthn configuration validation
    if (process.env.ORIGIN && !process.env.ORIGIN.startsWith("https://")) {
      warnings.push("ORIGIN should use HTTPS in production for WebAuthn");
    }

    if (process.env.RP_ID && process.env.RP_ID.includes("localhost")) {
      warnings.push("RP_ID should not be localhost in production");
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
  
  if (process.env.NEXT_PUBLIC_BASE_URL) {
    validateUrl(process.env.NEXT_PUBLIC_BASE_URL, "NEXT_PUBLIC_BASE_URL");
  }

  if (process.env.ORIGIN) {
    validateUrl(process.env.ORIGIN, "ORIGIN");
  }

  // Print warnings
  if (warnings.length > 0 && typeof console !== "undefined") {
    console.warn("⚠️  Web app environment validation warnings:");
    warnings.forEach((warning) => console.warn(`  ⚠️  ${warning}`));
  }

  if (errors.length > 0) {
    if (typeof console !== "undefined") {
      console.error("Web app environment validation failed:");
      errors.forEach((error) => console.error(`  ❌ ${error}`));
    }
    throw new Error("Environment validation failed");
  }

  if (typeof console !== "undefined") {
    console.log("✅ Web app environment validation passed");
  }

  return {
    NODE_ENV: nodeEnv,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_BASE_URL,
    NEXT_PUBLIC_APP_DOMAIN: process.env.NEXT_PUBLIC_APP_DOMAIN,
    ORIGIN: process.env.ORIGIN,
    RP_ID: process.env.RP_ID,
    ALLOWED_ORIGINS: process.env.ALLOWED_ORIGINS,
  };
}

/**
 * Get environment-specific URLs for the web app
 */
export function getWebEnvironmentUrls() {
  const env = process.env.NODE_ENV || "development";
  
  return {
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 
            (env === "production" ? "https://api.yourdomain.com" : "http://localhost:8787"),
    baseUrl: process.env.NEXT_PUBLIC_BASE_URL || 
             (env === "production" ? "https://yourdomain.com" : "http://localhost:3000"),
    domain: process.env.NEXT_PUBLIC_APP_DOMAIN || 
            (env === "production" ? "yourdomain.com" : "localhost:3000"),
    origin: process.env.ORIGIN || 
            (env === "production" ? "https://yourdomain.com" : "http://localhost:3000"),
    rpId: process.env.RP_ID || 
          (env === "production" ? "yourdomain.com" : "localhost"),
  };
}

/**
 * Get security configuration for the current environment
 */
export function getWebSecurityConfig() {
  const env = process.env.NODE_ENV || "development";
  
  const baseConfig = {
    development: {
      requireHttps: false,
      allowAllOrigins: true,
      securityLevel: "low" as const,
      rateLimit: {
        max: 1000,
        windowMs: 15 * 60 * 1000, // 15 minutes
      },
    },
    staging: {
      requireHttps: true,
      allowAllOrigins: false,
      securityLevel: "medium" as const,
      rateLimit: {
        max: 200,
        windowMs: 15 * 60 * 1000, // 15 minutes
      },
    },
    production: {
      requireHttps: true,
      allowAllOrigins: false,
      securityLevel: "high" as const,
      rateLimit: {
        max: 100,
        windowMs: 15 * 60 * 1000, // 15 minutes
      },
    },
  };

  return baseConfig[env as keyof typeof baseConfig] || baseConfig.development;
}