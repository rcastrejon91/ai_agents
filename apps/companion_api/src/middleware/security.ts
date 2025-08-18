import { RateLimiterRedis } from 'rate-limiter-flexible';
import { Redis } from 'ioredis';
import { Request, Response, NextFunction } from 'express';

export class SecurityMiddleware {
  private rateLimiter: RateLimiterRedis;
  private redis: Redis;
  
  constructor() {
    this.redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
    this.rateLimiter = new RateLimiterRedis({
      storeClient: this.redis,
      points: 10,
      duration: 1,
      blockDuration: 60 * 15
    });
  }

  async rateLimit(req: Request): Promise<void> {
    try {
      const ip = req.ip || 
        req.headers['x-forwarded-for'] as string ||
        req.socket.remoteAddress ||
        'unknown';
      await this.rateLimiter.consume(ip);
    } catch (err) {
      throw new Error('Too Many Requests');
    }
  }

  rateLimitMiddleware() {
    return async (req: Request, res: Response, next: NextFunction) => {
      try {
        await this.rateLimit(req);
        next();
      } catch (error) {
        res.status(429).json({ error: 'Too Many Requests' });
      }
    };
  }

  validateInput(data: any): void {
    // Enhanced input validation with security patterns
    const patterns: Record<string, RegExp> = {
      email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
      password: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/,
      username: /^[a-zA-Z0-9_-]{3,16}$/
    };

    Object.entries(data).forEach(([key, value]) => {
      if (patterns[key] && typeof value === 'string' && !patterns[key].test(value)) {
        throw new Error(`Invalid ${key} format`);
      }
    });
  }

  validateInputMiddleware() {
    return (req: Request, res: Response, next: NextFunction) => {
      try {
        if (req.body && typeof req.body === 'object') {
          this.validateInput(req.body);
        }
        next();
      } catch (error) {
        res.status(400).json({ error: error instanceof Error ? error.message : 'Invalid input format' });
      }
    };
  }

  securityHeadersMiddleware() {
    return (req: Request, res: Response, next: NextFunction) => {
      // Security headers
      res.setHeader('X-Content-Type-Options', 'nosniff');
      res.setHeader('X-Frame-Options', 'DENY');
      res.setHeader('X-XSS-Protection', '1; mode=block');
      res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
      res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
      next();
    };
  }

  async cleanup(): Promise<void> {
    await this.redis.quit();
  }
}