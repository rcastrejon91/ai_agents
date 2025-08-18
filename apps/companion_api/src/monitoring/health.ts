import { Redis } from 'ioredis';
import { Gauge, Counter, register } from 'prom-client';
import { Logger } from '../logging/logger.js';

export class HealthMonitor {
  private redis: Redis;
  private requestLatency: Gauge<string>;
  private errorRate: Counter<string>;
  private logger: Logger;

  constructor() {
    this.redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
    this.logger = new Logger();
    
    this.requestLatency = new Gauge({
      name: 'http_request_duration_seconds',
      help: 'Duration of HTTP requests in seconds',
      labelNames: ['method', 'route', 'status']
    });

    this.errorRate = new Counter({
      name: 'http_requests_errors_total',
      help: 'Total number of HTTP request errors',
      labelNames: ['method', 'route', 'status']
    });
  }

  async checkHealth(): Promise<{
    status: string;
    checks: Record<string, {status: string; message?: string}>
  }> {
    const checks = {
      redis: await this.checkRedis(),
      api: await this.checkAPI(),
      storage: await this.checkStorage()
    };

    const status = Object.values(checks).every(check => check.status === 'healthy')
      ? 'healthy'
      : 'unhealthy';

    this.logger.info('Health check completed', { status, checks });

    return { status, checks };
  }

  private async checkRedis(): Promise<{status: string; message?: string}> {
    try {
      const start = Date.now();
      await this.redis.ping();
      const duration = Date.now() - start;
      
      if (duration > 1000) {
        return {
          status: 'unhealthy',
          message: `Redis response time too high: ${duration}ms`
        };
      }
      
      return { status: 'healthy' };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: error instanceof Error ? error.message : 'Redis connection failed'
      };
    }
  }

  private async checkAPI(): Promise<{status: string; message?: string}> {
    try {
      // Check if OpenAI API key is configured
      if (!process.env.OPENAI_API_KEY) {
        return {
          status: 'unhealthy',
          message: 'OpenAI API key not configured'
        };
      }
      
      return { status: 'healthy' };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: error instanceof Error ? error.message : 'API check failed'
      };
    }
  }

  private async checkStorage(): Promise<{status: string; message?: string}> {
    try {
      // Basic storage check - could be expanded for actual database connections
      return { status: 'healthy' };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: error instanceof Error ? error.message : 'Storage check failed'
      };
    }
  }

  // Middleware to record request metrics
  metricsMiddleware() {
    return (req: any, res: any, next: any) => {
      const start = Date.now();
      
      res.on('finish', () => {
        const duration = (Date.now() - start) / 1000;
        const labels = {
          method: req.method,
          route: req.route?.path || req.path,
          status: res.statusCode.toString()
        };
        
        this.requestLatency.set(labels, duration);
        
        if (res.statusCode >= 400) {
          this.errorRate.inc(labels);
        }
      });
      
      next();
    };
  }

  // Get Prometheus metrics
  async getMetrics(): Promise<string> {
    return register.metrics();
  }

  async cleanup(): Promise<void> {
    await this.redis.quit();
  }
}