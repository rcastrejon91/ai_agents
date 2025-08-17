/**
 * Environment validation and configuration
 */

export interface Config {
  port: number;
  nodeEnv: string;
  openai: {
    apiKey: string;
  };
  cors: {
    origins: string[];
  };
  jwt: {
    secret: string;
    refreshSecret: string;
    accessExpiresIn: string;
    refreshExpiresIn: string;
  };
  security: {
    rateLimit: {
      windowMs: number;
      max: number;
    };
  };
}

/**
 * Validates that all required environment variables are present
 */
export const validateEnv = (): void => {
  const required = [
    'NODE_ENV',
    'OPENAI_API_KEY',
    'JWT_SECRET',
    'JWT_REFRESH_SECRET',
    'ALLOWED_ORIGINS'
  ];
  
  const missing = required.filter(key => !process.env[key]);
  if (missing.length) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }
};

/**
 * Environment-specific configuration
 */
const environmentConfigs = {
  development: {
    logLevel: 'debug',
    corsOrigins: ['http://localhost:3000', 'http://localhost:3001'],
    rateLimit: {
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 200 // Higher limit for development
    }
  },
  production: {
    logLevel: 'error',
    corsOrigins: process.env.ALLOWED_ORIGINS?.split(',') || [],
    rateLimit: {
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100 // Stricter limit for production
    }
  },
  test: {
    logLevel: 'silent',
    corsOrigins: ['http://localhost:3000'],
    rateLimit: {
      windowMs: 15 * 60 * 1000,
      max: 1000 // Very high limit for testing
    }
  }
};

/**
 * Gets configuration based on current environment
 */
export const getConfig = (): Config => {
  validateEnv();
  
  const nodeEnv = process.env.NODE_ENV || 'development';
  const envConfig = environmentConfigs[nodeEnv as keyof typeof environmentConfigs] || environmentConfigs.development;
  
  return {
    port: Number(process.env.PORT || 8787),
    nodeEnv,
    openai: {
      apiKey: process.env.OPENAI_API_KEY!,
    },
    cors: {
      origins: envConfig.corsOrigins,
    },
    jwt: {
      secret: process.env.JWT_SECRET!,
      refreshSecret: process.env.JWT_REFRESH_SECRET!,
      accessExpiresIn: process.env.JWT_ACCESS_EXPIRES_IN || '15m',
      refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d',
    },
    security: {
      rateLimit: envConfig.rateLimit,
    },
  };
};