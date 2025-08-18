/**
 * Environment configuration and validation for companion-web
 */

export interface WebEnvConfig {
  NODE_ENV: string;
  OPENAI_API_KEY?: string;
  NEXT_PUBLIC_API_URL?: string;
  NEXT_PUBLIC_APP_DOMAIN?: string;
  NEXT_PUBLIC_BASE_URL?: string;
  ALLOWED_ORIGINS?: string;
  API_SECRET_KEY?: string;
}

/**
 * Validates environment variables for web application
 */
export function validateWebEnvironment(): WebEnvConfig {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Validate NODE_ENV
  const validEnvs = ["development", "staging", "production"];
  const nodeEnv = process.env.NODE_ENV || "development";
  if (!validEnvs.includes(nodeEnv)) {
    errors.push(`NODE_ENV must be one of: ${validEnvs.join(", ")}`);
  }

  // Check for OpenAI API key
  const openaiKey = process.env.OPENAI_API_KEY;
  if (openaiKey && !openaiKey.startsWith("sk-")) {
    errors.push('OPENAI_API_KEY must start with "sk-"');
  }

  // Validate URLs if provided
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (apiUrl) {
    try {
      new URL(apiUrl);
    } catch {
      errors.push("NEXT_PUBLIC_API_URL must be a valid URL");
    }
  }

  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL;
  if (baseUrl) {
    try {
      new URL(baseUrl);
    } catch {
      errors.push("NEXT_PUBLIC_BASE_URL must be a valid URL");
    }
  }

  // Environment-specific validations
  if (nodeEnv === "production") {
    if (!openaiKey) {
      errors.push("OPENAI_API_KEY is required in production");
    }
    if (!process.env.ALLOWED_ORIGINS) {
      warnings.push("ALLOWED_ORIGINS should be set in production for security");
    }
    if (!process.env.API_SECRET_KEY) {
      warnings.push("API_SECRET_KEY should be set in production for authentication");
    }
  }

  // Log results
  if (warnings.length > 0) {
    console.warn("Environment validation warnings:");
    warnings.forEach((warning) => console.warn(`  ⚠️  ${warning}`));
  }

  if (errors.length > 0) {
    console.error("Environment validation failed:");
    errors.forEach((error) => console.error(`  ❌ ${error}`));
    throw new Error(`Environment validation failed: ${errors.join(", ")}`);
  }

  console.log("✅ Web environment validation passed");

  return {
    NODE_ENV: nodeEnv,
    OPENAI_API_KEY: openaiKey,
    NEXT_PUBLIC_API_URL: apiUrl,
    NEXT_PUBLIC_APP_DOMAIN: process.env.NEXT_PUBLIC_APP_DOMAIN,
    NEXT_PUBLIC_BASE_URL: baseUrl,
    ALLOWED_ORIGINS: process.env.ALLOWED_ORIGINS,
    API_SECRET_KEY: process.env.API_SECRET_KEY,
  };
}

/**
 * Get configuration for specific environment
 */
export function getWebEnvironmentConfig() {
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

/**
 * Helper to check if required environment variables are present
 */
export function hasRequiredEnvVars(): boolean {
  try {
    validateWebEnvironment();
    return true;
  } catch {
    return false;
  }
}