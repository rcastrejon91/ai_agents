import { randomBytes } from 'crypto';
import { SecureStorage } from './secure-storage';
import { getRedisClient } from '../lib/redis';

const storage = SecureStorage.getInstance();
const SESSION_DURATION = 24 * 60 * 60; // 24 hours

export class SessionManager {
  static async createSession(userId: string, data: any): Promise<string> {
    const sessionId = randomBytes(32).toString('hex');
    const encryptedData = await storage.encrypt({ userId, ...data });
    
    const redis = await getRedisClient();
    await redis.setEx(
      `session:${sessionId}`,
      SESSION_DURATION,
      encryptedData
    );
    
    return sessionId;
  }

  static async getSession(sessionId: string): Promise<any | null> {
    const redis = await getRedisClient();
    const encryptedData = await redis.get(`session:${sessionId}`);
    if (!encryptedData) {
      return null;
    }
    
    return storage.decrypt(encryptedData);
  }

  static async invalidateSession(sessionId: string): Promise<void> {
    const redis = await getRedisClient();
    await redis.del(`session:${sessionId}`);
  }

  static async invalidateAllUserSessions(userId: string): Promise<void> {
    const redis = await getRedisClient();
    const keys = await redis.keys('session:*');
    
    for (const key of keys) {
      const encryptedData = await redis.get(key);
      if (encryptedData) {
        try {
          const sessionData = await storage.decrypt(encryptedData);
          if (sessionData.userId === userId) {
            await redis.del(key);
          }
        } catch (error) {
          // Skip invalid sessions
          console.warn(`Failed to decrypt session ${key}:`, error);
        }
      }
    }
  }
}