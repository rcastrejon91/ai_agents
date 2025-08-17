import { createClient } from 'redis';
import { SecureConfig } from '../config/secure_config';

const config = SecureConfig.getInstance();

let redisClient: ReturnType<typeof createClient> | null = null;

export const getRedisClient = async () => {
  if (!redisClient) {
    redisClient = createClient({
      url: config.get('REDIS_URL'),
    });

    redisClient.on('error', (err) => {
      console.error('Redis Client Error:', err);
    });

    await redisClient.connect();
  }

  return redisClient;
};

export const closeRedisClient = async () => {
  if (redisClient && redisClient.isOpen) {
    await redisClient.quit();
    redisClient = null;
  }
};

export { redisClient as redis };