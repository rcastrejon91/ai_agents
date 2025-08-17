/**
 * TypeScript configuration system for AI Agents platform.
 */

export interface DatabaseConfig {
  url?: string;
  maxConnections: number;
  queryTimeout: number;
  enableQueryLogging: boolean;
}

export interface RedisConfig {
  url?: string;
  maxConnections: number;
  defaultTtl: number;
  keyPrefix: string;
}

export interface SecurityConfig {
  secretKey?: string;
  adminToken?: string;
  corsOrigins: string[];
  corsCredentials: boolean;
  rateLimitPerMinute: number;
  rateLimitBurst: number;
  maxRequestSize: number;
}

export interface APIConfig {
  openaiApiKey?: string;
  tavilyApiKey?: string;
  stripeSecretKey?: string;
  stripeWebhookSecret?: string;
  timeout: number;
  maxRetries: number;
}

export interface MonitoringConfig {
  enableMetrics: boolean;
  enableHealthChecks: boolean;
  enableRequestLogging: boolean;
  logLevel: string;
  metricsPort: number;
}

export interface PerformanceConfig {
  enableCaching: boolean;
  cacheTtl: number;
  maxCacheSize: number;
  enableCompression: boolean;
  workerProcesses: number;
}

export interface AppSettings {
  environment: string;
  debug: boolean;
  database: DatabaseConfig;
  redis: RedisConfig;
  security: SecurityConfig;
  api: APIConfig;
  monitoring: MonitoringConfig;
  performance: PerformanceConfig;
}

class SettingsManager {
  private settings: AppSettings;

  constructor() {
    this.settings = this.loadSettings();
  }

  private loadSettings(): AppSettings {
    const environment = process.env.ENVIRONMENT || "development";
    const debug = process.env.DEBUG?.toLowerCase() === "true";

    return {
      environment,
      debug,
      database: this.loadDatabaseConfig(),
      redis: this.loadRedisConfig(),
      security: this.loadSecurityConfig(),
      api: this.loadAPIConfig(),
      monitoring: this.loadMonitoringConfig(),
      performance: this.loadPerformanceConfig(),
    };
  }

  private loadDatabaseConfig(): DatabaseConfig {
    return {
      url: process.env.DATABASE_URL,
      maxConnections: parseInt(process.env.DB_MAX_CONNECTIONS || "10", 10),
      queryTimeout: parseInt(process.env.DB_QUERY_TIMEOUT || "30", 10),
      enableQueryLogging: process.env.DB_ENABLE_QUERY_LOGGING?.toLowerCase() === "true",
    };
  }

  private loadRedisConfig(): RedisConfig {
    return {
      url: process.env.REDIS_URL,
      maxConnections: parseInt(process.env.REDIS_MAX_CONNECTIONS || "10", 10),
      defaultTtl: parseInt(process.env.REDIS_DEFAULT_TTL || "300", 10),
      keyPrefix: process.env.REDIS_KEY_PREFIX || "ai_agents",
    };
  }

  private loadSecurityConfig(): SecurityConfig {
    const corsOrigins = process.env.CORS_ORIGINS
      ? process.env.CORS_ORIGINS.split(",").map(origin => origin.trim())
      : ["http://localhost:3000"];

    return {
      secretKey: process.env.SECRET_KEY,
      adminToken: process.env.ADMIN_TOKEN,
      corsOrigins,
      corsCredentials: process.env.CORS_CREDENTIALS?.toLowerCase() !== "false",
      rateLimitPerMinute: parseInt(process.env.RATE_LIMIT_PER_MINUTE || "90", 10),
      rateLimitBurst: parseInt(process.env.RATE_LIMIT_BURST || "10", 10),
      maxRequestSize: parseInt(process.env.MAX_REQUEST_SIZE || String(1024 * 1024), 10),
    };
  }

  private loadAPIConfig(): APIConfig {
    return {
      openaiApiKey: process.env.OPENAI_API_KEY,
      tavilyApiKey: process.env.TAVILY_API_KEY,
      stripeSecretKey: process.env.STRIPE_SECRET_KEY,
      stripeWebhookSecret: process.env.STRIPE_WEBHOOK_SECRET,
      timeout: parseInt(process.env.API_TIMEOUT || "30", 10),
      maxRetries: parseInt(process.env.API_MAX_RETRIES || "3", 10),
    };
  }

  private loadMonitoringConfig(): MonitoringConfig {
    return {
      enableMetrics: process.env.ENABLE_METRICS?.toLowerCase() !== "false",
      enableHealthChecks: process.env.ENABLE_HEALTH_CHECKS?.toLowerCase() !== "false",
      enableRequestLogging: process.env.ENABLE_REQUEST_LOGGING?.toLowerCase() !== "false",
      logLevel: (process.env.LOG_LEVEL || "INFO").toUpperCase(),
      metricsPort: parseInt(process.env.METRICS_PORT || "9090", 10),
    };
  }

  private loadPerformanceConfig(): PerformanceConfig {
    return {
      enableCaching: process.env.ENABLE_CACHING?.toLowerCase() !== "false",
      cacheTtl: parseInt(process.env.CACHE_TTL || "300", 10),
      maxCacheSize: parseInt(process.env.MAX_CACHE_SIZE || "1000", 10),
      enableCompression: process.env.ENABLE_COMPRESSION?.toLowerCase() !== "false",
      workerProcesses: parseInt(process.env.WORKER_PROCESSES || "1", 10),
    };
  }

  get(): AppSettings {
    return this.settings;
  }

  isProduction(): boolean {
    return this.settings.environment.toLowerCase() === "production";
  }

  isDevelopment(): boolean {
    return this.settings.environment.toLowerCase() === "development";
  }

  getCorsConfig(): {
    origin: string[] | boolean;
    credentials: boolean;
    methods: string[];
    allowedHeaders: string[];
  } {
    if (this.isProduction()) {
      return {
        origin: this.settings.security.corsOrigins,
        credentials: this.settings.security.corsCredentials,
        methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allowedHeaders: ["Content-Type", "Authorization", "X-Admin-Key"],
      };
    } else {
      return {
        origin: this.settings.security.corsOrigins.length > 0 ? this.settings.security.corsOrigins : true,
        credentials: true,
        methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allowedHeaders: ["*"],
      };
    }
  }

  getSecurityHeaders(): Record<string, string> {
    if (this.isProduction()) {
      return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'",
      };
    }
    return {};
  }
}

// Global settings instance
export const settings = new SettingsManager();
export default settings;