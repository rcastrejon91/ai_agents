import { Redis } from 'ioredis';

export class TestRedis {
  private redis: Redis;
  private isInitialized = false;

  private constructor() {
    this.redis = new Redis({
      host: process.env.TEST_REDIS_HOST || 'localhost',
      port: parseInt(process.env.TEST_REDIS_PORT || '6379'),
      db: parseInt(process.env.TEST_REDIS_DB || '1'), // Use different DB for tests
      password: process.env.TEST_REDIS_PASSWORD,
      retryStrategy: () => null // Don't retry in tests
    });
  }

  static async init(): Promise<TestRedis> {
    const instance = new TestRedis();
    
    try {
      await instance.redis.ping();
      instance.isInitialized = true;
      console.log('Test Redis connected successfully');
    } catch (error) {
      console.warn('Test Redis not available, some tests may be skipped', error);
      instance.isInitialized = false;
    }
    
    return instance;
  }

  async cleanup(): Promise<void> {
    if (this.isInitialized) {
      try {
        await this.redis.flushdb(); // Clear test database
        await this.redis.quit();
        console.log('Test Redis cleaned up successfully');
      } catch (error) {
        console.error('Error cleaning up test Redis:', error);
      }
    }
  }

  getClient(): Redis {
    return this.redis;
  }

  isAvailable(): boolean {
    return this.isInitialized;
  }

  async clear(): Promise<void> {
    if (this.isInitialized) {
      await this.redis.flushdb();
    }
  }
}