import { sign, verify } from 'jsonwebtoken';
import { Redis } from 'ioredis';
import { randomBytes } from 'crypto';

export class JWTService {
  private redis: Redis;
  
  constructor() {
    this.redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
  }

  async createTokens(userId: string): Promise<{accessToken: string, refreshToken: string}> {
    const accessToken = sign({ userId }, process.env.JWT_SECRET || 'fallback-secret', { expiresIn: '15m' });
    const refreshToken = sign({ userId }, process.env.REFRESH_SECRET || 'fallback-refresh-secret', { expiresIn: '7d' });
    
    await this.redis.set(`refresh:${userId}`, refreshToken, 'EX', 60 * 60 * 24 * 7);
    return { accessToken, refreshToken };
  }

  async rotateApiKey(apiKeyId: string): Promise<string> {
    const newKey = randomBytes(32).toString('hex');
    await this.redis.set(`apikey:${apiKeyId}`, newKey, 'EX', 60 * 60 * 24 * 30);
    return newKey;
  }

  async verifyToken(token: string, secret?: string): Promise<any> {
    try {
      const secretToUse = secret || process.env.JWT_SECRET || 'fallback-secret';
      return verify(token, secretToUse);
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  async revokeRefreshToken(userId: string): Promise<void> {
    await this.redis.del(`refresh:${userId}`);
  }

  async isRefreshTokenValid(userId: string, token: string): Promise<boolean> {
    const storedToken = await this.redis.get(`refresh:${userId}`);
    return storedToken === token;
  }

  async getApiKey(apiKeyId: string): Promise<string | null> {
    return await this.redis.get(`apikey:${apiKeyId}`);
  }

  async cleanup(): Promise<void> {
    await this.redis.quit();
  }
}