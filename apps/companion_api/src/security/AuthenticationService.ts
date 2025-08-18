import { verify, decode } from 'jsonwebtoken';
import { Redis } from 'ioredis';
import { createHash } from 'crypto';
import { Logger } from '../utils/Logger.js';

export class AuthenticationService {
  private redis: Redis;
  private logger: Logger;
  
  constructor() {
    this.logger = new Logger('AuthenticationService');
    
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD,
      tls: process.env.REDIS_TLS === 'true' ? {} : undefined,
      retryStrategy: (times: number) => {
        // Limit retries in test environment
        if (process.env.NODE_ENV === 'test' && times > 3) {
          return null; // Stop retrying
        }
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
      maxRetriesPerRequest: process.env.NODE_ENV === 'test' ? 1 : 3
    });

    this.redis.on('error', (error) => {
      this.logger.error('Redis connection error', { error });
    });

    this.redis.on('connect', () => {
      this.logger.info('Redis connected successfully');
    });
  }

  async validateToken(token: string): Promise<boolean> {
    try {
      // Fix: Add token blacklist check
      const isBlacklisted = await this.redis.get(`blacklist:${token}`);
      if (isBlacklisted) {
        this.logger.warn('Token validation failed: token is blacklisted', { token: token.substring(0, 10) + '...' });
        return false;
      }

      const decoded = verify(token, process.env.JWT_SECRET || 'default-secret');
      // Fix: Add additional validation for token claims
      if (!this.validateTokenClaims(decoded)) {
        this.logger.warn('Token validation failed: invalid claims', { token: token.substring(0, 10) + '...' });
        return false;
      }

      return true;
    } catch (error) {
      this.logger.error('Token validation failed', { error });
      return false;
    }
  }

  private validateTokenClaims(decoded: any): boolean {
    const now = Math.floor(Date.now() / 1000);
    // Fix: Add proper timestamp validation
    const isValid = decoded.exp > now && decoded.iat <= now;
    
    if (!isValid) {
      this.logger.warn('Token claims validation failed', { 
        exp: decoded.exp, 
        iat: decoded.iat, 
        now,
        expired: decoded.exp <= now,
        future: decoded.iat > now
      });
    }
    
    return isValid;
  }

  async blacklistToken(token: string, expiryInSeconds?: number): Promise<void> {
    try {
      const expiry = expiryInSeconds || 86400; // 24 hours default
      await this.redis.set(`blacklist:${token}`, '1', 'EX', expiry);
      this.logger.info('Token blacklisted successfully', { token: token.substring(0, 10) + '...', expiry });
    } catch (error) {
      this.logger.error('Failed to blacklist token', { error, token: token.substring(0, 10) + '...' });
    }
  }

  async revokeUserSessions(userId: string): Promise<void> {
    try {
      // Enhancement: Revoke all user sessions
      const pattern = `session:${userId}:*`;
      const keys = await this.redis.keys(pattern);
      if (keys.length > 0) {
        await this.redis.del(...keys);
        this.logger.info(`Revoked ${keys.length} sessions for user`, { userId });
      } else {
        this.logger.info('No sessions found to revoke', { userId });
      }
    } catch (error) {
      this.logger.error('Failed to revoke user sessions', { error, userId });
    }
  }

  async createSession(userId: string, sessionData: any, ttl: number = 86400): Promise<string> {
    try {
      const sessionId = createHash('sha256').update(`${userId}:${Date.now()}:${Math.random()}`).digest('hex');
      const sessionKey = `session:${userId}:${sessionId}`;
      
      await this.redis.set(sessionKey, JSON.stringify(sessionData), 'EX', ttl);
      this.logger.info('Session created successfully', { userId, sessionId: sessionId.substring(0, 10) + '...', ttl });
      
      return sessionId;
    } catch (error) {
      this.logger.error('Failed to create session', { error, userId });
      throw error;
    }
  }

  async getSession(userId: string, sessionId: string): Promise<any | null> {
    try {
      const sessionKey = `session:${userId}:${sessionId}`;
      const data = await this.redis.get(sessionKey);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      this.logger.error('Failed to get session', { error, userId, sessionId: sessionId.substring(0, 10) + '...' });
      return null;
    }
  }

  async cleanup(): Promise<void> {
    try {
      await this.redis.quit();
      this.logger.info('Redis connection closed successfully');
    } catch (error) {
      this.logger.error('Error closing Redis connection', { error });
    }
  }
}