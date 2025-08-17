/**
 * Environment Configuration System
 * Provides centralized configuration management for different environments
 */

const environments = {
  development: {
    name: 'development',
    api: {
      baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8787',
      timeout: 30000,
      retries: 3
    },
    security: {
      corsOrigins: ['http://localhost:3000', 'http://localhost:8787'],
      rateLimiting: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 100, // limit each IP to 100 requests per windowMs
        skipSuccessfulRequests: false
      },
      jwtSecret: process.env.JWT_SECRET || 'dev-secret-change-in-production',
      sessionSecret: process.env.SESSION_SECRET || 'dev-session-secret'
    },
    logging: {
      level: 'debug',
      enableConsole: true,
      enableFile: true
    },
    features: {
      enableDebugMode: true,
      enableMockData: true
    }
  },

  staging: {
    name: 'staging',
    api: {
      baseUrl: process.env.NEXT_PUBLIC_API_URL,
      timeout: 30000,
      retries: 2
    },
    security: {
      corsOrigins: process.env.ALLOWED_ORIGINS?.split(',') || [],
      rateLimiting: {
        windowMs: 15 * 60 * 1000,
        max: 50,
        skipSuccessfulRequests: true
      },
      jwtSecret: process.env.JWT_SECRET,
      sessionSecret: process.env.SESSION_SECRET
    },
    logging: {
      level: 'info',
      enableConsole: false,
      enableFile: true
    },
    features: {
      enableDebugMode: false,
      enableMockData: false
    }
  },

  production: {
    name: 'production',
    api: {
      baseUrl: process.env.NEXT_PUBLIC_API_URL,
      timeout: 30000,
      retries: 1
    },
    security: {
      corsOrigins: process.env.ALLOWED_ORIGINS?.split(',') || [],
      rateLimiting: {
        windowMs: 15 * 60 * 1000,
        max: 30,
        skipSuccessfulRequests: true
      },
      jwtSecret: process.env.JWT_SECRET,
      sessionSecret: process.env.SESSION_SECRET
    },
    logging: {
      level: 'warn',
      enableConsole: false,
      enableFile: true
    },
    features: {
      enableDebugMode: false,
      enableMockData: false
    }
  }
};

/**
 * Required environment variables for each environment
 */
const requiredEnvVars = {
  development: ['OPENAI_API_KEY'],
  staging: ['OPENAI_API_KEY', 'JWT_SECRET', 'SESSION_SECRET', 'ALLOWED_ORIGINS'],
  production: ['OPENAI_API_KEY', 'JWT_SECRET', 'SESSION_SECRET', 'ALLOWED_ORIGINS', 'STRIPE_SECRET_KEY']
};

/**
 * Get current environment configuration
 */
function getEnvironment() {
  const env = process.env.NODE_ENV || 'development';
  return environments[env] || environments.development;
}

/**
 * Validate required environment variables
 */
function validateEnvironment() {
  const env = process.env.NODE_ENV || 'development';
  const required = requiredEnvVars[env] || [];
  const missing = required.filter(varName => !process.env[varName]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables for ${env}: ${missing.join(', ')}`);
  }
  
  return true;
}

/**
 * Get configuration value with fallback
 */
function getConfig(path, fallback = null) {
  const config = getEnvironment();
  const keys = path.split('.');
  let value = config;
  
  for (const key of keys) {
    value = value?.[key];
    if (value === undefined) {
      return fallback;
    }
  }
  
  return value;
}

module.exports = {
  getEnvironment,
  validateEnvironment,
  getConfig,
  environments
};