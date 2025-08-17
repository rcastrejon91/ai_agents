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
}

/**
 * Validates required environment variables
 */
export function validateEnvironment(): EnvConfig {
  const errors: string[] = [];
  
  // Required variables
  const requiredVars = ['OPENAI_API_KEY'];
  
  requiredVars.forEach(varName => {
    if (!process.env[varName]) {
      errors.push(`${varName} is required`);
    }
  });
  
  // Validate OpenAI API key format
  if (process.env.OPENAI_API_KEY && !process.env.OPENAI_API_KEY.startsWith('sk-')) {
    errors.push('OPENAI_API_KEY must start with "sk-"');
  }
  
  // Validate PORT
  const port = parseInt(process.env.PORT || '8787', 10);
  if (isNaN(port) || port < 1 || port > 65535) {
    errors.push('PORT must be a valid port number (1-65535)');
  }
  
  // Validate NODE_ENV
  const validEnvs = ['development', 'staging', 'production'];
  const nodeEnv = process.env.NODE_ENV || 'development';
  if (!validEnvs.includes(nodeEnv)) {
    errors.push(`NODE_ENV must be one of: ${validEnvs.join(', ')}`);
  }
  
  if (errors.length > 0) {
    console.error('Environment validation failed:');
    errors.forEach(error => console.error(`  ❌ ${error}`));
    process.exit(1);
  }
  
  console.log('✅ Environment validation passed');
  
  return {
    OPENAI_API_KEY: process.env.OPENAI_API_KEY!,
    PORT: port,
    NODE_ENV: nodeEnv,
    ALLOWED_ORIGINS: process.env.ALLOWED_ORIGINS,
    STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET: process.env.STRIPE_WEBHOOK_SECRET,
  };
}

/**
 * Get configuration for specific environment
 */
export function getEnvironmentConfig() {
  const env = process.env.NODE_ENV || 'development';
  
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
    },
    staging: {
      cors: {
        origin: (process.env.ALLOWED_ORIGINS || '').split(',').filter(Boolean),
        credentials: true,
      },
      rateLimit: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        maxRequests: 200,
      },
    },
    production: {
      cors: {
        origin: (process.env.ALLOWED_ORIGINS || '').split(',').filter(Boolean),
        credentials: true,
      },
      rateLimit: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        maxRequests: 100, // Strict in production
      },
    },
  };
  
  return baseConfig[env as keyof typeof baseConfig] || baseConfig.development;
}