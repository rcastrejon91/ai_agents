import { Redis } from 'ioredis';
import { Logger } from './Logger.js';

export class CacheManager {
  private redis: Redis;
  private logger: Logger;
  
  constructor() {
    this.logger = new Logger('CacheManager');
    
    // Fix: Add proper error handling for Redis connection
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD,
      tls: process.env.REDIS_TLS === 'true' ? {} : undefined,
      retryStrategy: (times: number) => {
        // Limit retries in test environment
        if (process.env.NODE_ENV === 'test' && times > 3) {
          this.logger.warn(`Redis retry limit reached in test environment`);
          return null; // Stop retrying
        }
        const delay = Math.min(times * 50, 2000);
        this.logger.warn(`Redis retry attempt ${times}, delay: ${delay}ms`);
        return delay;
      },
      maxRetriesPerRequest: process.env.NODE_ENV === 'test' ? 1 : 3,
      lazyConnect: true
    });

    this.redis.on('error', (error) => {
      this.logger.error('Redis connection error', { error: error.message });
    });

    this.redis.on('connect', () => {
      this.logger.info('Redis connected successfully');
    });

    this.redis.on('reconnecting', () => {
      this.logger.info('Redis reconnecting...');
    });

    this.redis.on('ready', () => {
      this.logger.info('Redis connection ready');
    });
  }

  async get<T>(key: string): Promise<T | null> {
    try {
      const data = await this.redis.get(key);
      if (data) {
        const parsed = JSON.parse(data);
        this.logger.debug('Cache hit', { key });
        return parsed;
      }
      this.logger.debug('Cache miss', { key });
      return null;
    } catch (error) {
      this.logger.error('Cache retrieval failed', { error: error instanceof Error ? error.message : error, key });
      return null;
    }
  }

  async set(key: string, value: any, ttl?: number): Promise<void> {
    try {
      const serialized = JSON.stringify(value);
      if (ttl) {
        await this.redis.set(key, serialized, 'EX', ttl);
        this.logger.debug('Cache stored with TTL', { key, ttl });
      } else {
        await this.redis.set(key, serialized);
        this.logger.debug('Cache stored without TTL', { key });
      }
    } catch (error) {
      this.logger.error('Cache storage failed', { error: error instanceof Error ? error.message : error, key });
    }
  }

  async del(key: string): Promise<void> {
    try {
      await this.redis.del(key);
      this.logger.debug('Cache key deleted', { key });
    } catch (error) {
      this.logger.error('Cache deletion failed', { error: error instanceof Error ? error.message : error, key });
    }
  }

  async exists(key: string): Promise<boolean> {
    try {
      const result = await this.redis.exists(key);
      return result === 1;
    } catch (error) {
      this.logger.error('Cache existence check failed', { error: error instanceof Error ? error.message : error, key });
      return false;
    }
  }

  async expire(key: string, seconds: number): Promise<void> {
    try {
      await this.redis.expire(key, seconds);
      this.logger.debug('Cache expiry set', { key, seconds });
    } catch (error) {
      this.logger.error('Cache expiry setting failed', { error: error instanceof Error ? error.message : error, key });
    }
  }

  async increment(key: string, amount: number = 1): Promise<number> {
    try {
      const result = await this.redis.incrby(key, amount);
      this.logger.debug('Cache incremented', { key, amount, result });
      return result;
    } catch (error) {
      this.logger.error('Cache increment failed', { error: error instanceof Error ? error.message : error, key });
      return 0;
    }
  }

  async keys(pattern: string): Promise<string[]> {
    try {
      const keys = await this.redis.keys(pattern);
      this.logger.debug('Cache keys retrieved', { pattern, count: keys.length });
      return keys;
    } catch (error) {
      this.logger.error('Cache keys retrieval failed', { error: error instanceof Error ? error.message : error, pattern });
      return [];
    }
  }

  async flushPattern(pattern: string): Promise<void> {
    try {
      const keys = await this.keys(pattern);
      if (keys.length > 0) {
        await this.redis.del(...keys);
        this.logger.info('Cache pattern flushed', { pattern, count: keys.length });
      }
    } catch (error) {
      this.logger.error('Cache pattern flush failed', { error: error instanceof Error ? error.message : error, pattern });
    }
  }

  async isConnected(): Promise<boolean> {
    try {
      await this.redis.ping();
      return true;
    } catch (error) {
      return false;
    }
  }

  async cleanup(): Promise<void> {
    try {
      await this.redis.quit();
      this.logger.info('Redis connection closed successfully');
    } catch (error) {
      this.logger.error('Error closing Redis connection', { error: error instanceof Error ? error.message : error });
    }
  }
}