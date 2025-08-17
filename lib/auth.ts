/**
 * Enhanced Authentication System
 * JWT with refresh tokens, session management, and role-based access control
 */

import jwt from 'jsonwebtoken';
import { NextApiRequest, NextApiResponse } from 'next';
import { getConfig } from '../config/environments';
import { AuthenticationError, AuthorizationError, TokenExpiredError, withErrorHandler } from './errors';

export interface User {
  id: string;
  email: string;
  role: string;
  permissions: string[];
  sessionId: string;
}

export interface TokenPayload {
  userId: string;
  email: string;
  role: string;
  permissions: string[];
  sessionId: string;
  type: 'access' | 'refresh';
  iat?: number;
  exp?: number;
}

export interface Session {
  id: string;
  userId: string;
  isActive: boolean;
  createdAt: Date;
  lastActivity: Date;
  refreshTokens: string[];
  deviceInfo?: {
    userAgent: string;
    ip: string;
  };
}

/**
 * In-memory session store (replace with Redis/database in production)
 */
class SessionStore {
  private sessions: Map<string, Session> = new Map();

  createSession(userId: string, deviceInfo?: any): Session {
    const sessionId = this.generateSessionId();
    const session: Session = {
      id: sessionId,
      userId,
      isActive: true,
      createdAt: new Date(),
      lastActivity: new Date(),
      refreshTokens: [],
      deviceInfo
    };

    this.sessions.set(sessionId, session);
    return session;
  }

  getSession(sessionId: string): Session | null {
    return this.sessions.get(sessionId) || null;
  }

  updateLastActivity(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.lastActivity = new Date();
    }
  }

  addRefreshToken(sessionId: string, refreshToken: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.refreshTokens.push(refreshToken);
      // Keep only last 5 refresh tokens
      if (session.refreshTokens.length > 5) {
        session.refreshTokens = session.refreshTokens.slice(-5);
      }
    }
  }

  removeRefreshToken(sessionId: string, refreshToken: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.refreshTokens = session.refreshTokens.filter(token => token !== refreshToken);
    }
  }

  invalidateSession(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.isActive = false;
      session.refreshTokens = [];
    }
  }

  invalidateAllUserSessions(userId: string): void {
    for (const session of this.sessions.values()) {
      if (session.userId === userId) {
        session.isActive = false;
        session.refreshTokens = [];
      }
    }
  }

  private generateSessionId(): string {
    return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Clean up expired sessions (call periodically)
  cleanup(): void {
    const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    for (const [sessionId, session] of this.sessions.entries()) {
      if (session.lastActivity < oneWeekAgo || !session.isActive) {
        this.sessions.delete(sessionId);
      }
    }
  }
}

const sessionStore = new SessionStore();

/**
 * Token management
 */
export class TokenManager {
  private static getSecrets() {
    const jwtSecret = getConfig('security.jwtSecret');
    if (!jwtSecret) {
      throw new Error('JWT secret not configured');
    }
    return { jwtSecret };
  }

  static generateTokens(user: User): { accessToken: string; refreshToken: string } {
    const { jwtSecret } = this.getSecrets();
    
    const payload: Omit<TokenPayload, 'type'> = {
      userId: user.id,
      email: user.email,
      role: user.role,
      permissions: user.permissions,
      sessionId: user.sessionId
    };

    const accessToken = jwt.sign(
      { ...payload, type: 'access' },
      jwtSecret,
      { expiresIn: '15m' }
    );

    const refreshToken = jwt.sign(
      { ...payload, type: 'refresh' },
      jwtSecret,
      { expiresIn: '7d' }
    );

    // Store refresh token in session
    sessionStore.addRefreshToken(user.sessionId, refreshToken);

    return { accessToken, refreshToken };
  }

  static verifyToken(token: string, expectedType: 'access' | 'refresh'): TokenPayload {
    const { jwtSecret } = this.getSecrets();
    
    try {
      const payload = jwt.verify(token, jwtSecret) as TokenPayload;
      
      if (payload.type !== expectedType) {
        throw new AuthenticationError('Invalid token type');
      }

      // Verify session is still active
      const session = sessionStore.getSession(payload.sessionId);
      if (!session || !session.isActive) {
        throw new AuthenticationError('Session expired');
      }

      // Update last activity
      sessionStore.updateLastActivity(payload.sessionId);

      return payload;
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        throw new TokenExpiredError('Token has expired');
      }
      throw new AuthenticationError('Invalid token');
    }
  }

  static refreshTokens(refreshToken: string): { accessToken: string; refreshToken: string } {
    const payload = this.verifyToken(refreshToken, 'refresh');
    
    // Verify refresh token exists in session
    const session = sessionStore.getSession(payload.sessionId);
    if (!session || !session.refreshTokens.includes(refreshToken)) {
      throw new AuthenticationError('Invalid refresh token');
    }

    // Remove old refresh token
    sessionStore.removeRefreshToken(payload.sessionId, refreshToken);

    // Generate new tokens
    const user: User = {
      id: payload.userId,
      email: payload.email,
      role: payload.role,
      permissions: payload.permissions,
      sessionId: payload.sessionId
    };

    return this.generateTokens(user);
  }

  static revokeRefreshToken(refreshToken: string): void {
    try {
      const payload = this.verifyToken(refreshToken, 'refresh');
      sessionStore.removeRefreshToken(payload.sessionId, refreshToken);
    } catch {
      // Token already invalid, ignore
    }
  }
}

/**
 * Role and permission management
 */
export class AccessControl {
  private static rolePermissions: Record<string, string[]> = {
    user: ['read:own', 'update:own'],
    moderator: ['read:own', 'update:own', 'read:all', 'moderate:content'],
    admin: ['*'], // Admin has all permissions
    staff: ['read:own', 'update:own', 'read:legal', 'write:legal'],
    firm_user: ['read:own', 'update:own', 'read:legal']
  };

  static hasPermission(userRole: string, userPermissions: string[], requiredPermission: string): boolean {
    // Admin has all permissions
    if (userRole === 'admin' || userPermissions.includes('*')) {
      return true;
    }

    // Check specific permission
    if (userPermissions.includes(requiredPermission)) {
      return true;
    }

    // Check wildcard permissions
    const parts = requiredPermission.split(':');
    for (let i = 1; i <= parts.length; i++) {
      const wildcardPermission = parts.slice(0, i).join(':') + ':*';
      if (userPermissions.includes(wildcardPermission)) {
        return true;
      }
    }

    return false;
  }

  static hasRole(userRole: string, requiredRoles: string[]): boolean {
    return requiredRoles.includes(userRole) || userRole === 'admin';
  }

  static getUserPermissions(role: string): string[] {
    return this.rolePermissions[role] || [];
  }
}

/**
 * Authentication middleware
 */
export function withAuth(requiredPermissions?: string[], requiredRoles?: string[]) {
  return function (handler: (req: NextApiRequest & { user: User }, res: NextApiResponse) => Promise<void>) {
    return withErrorHandler(async (req: NextApiRequest, res: NextApiResponse) => {
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        throw new AuthenticationError('Missing or invalid authorization header');
      }

      const token = authHeader.substring(7);
      const payload = TokenManager.verifyToken(token, 'access');

      // Create user object
      const user: User = {
        id: payload.userId,
        email: payload.email,
        role: payload.role,
        permissions: payload.permissions,
        sessionId: payload.sessionId
      };

      // Check role requirements
      if (requiredRoles && !AccessControl.hasRole(user.role, requiredRoles)) {
        throw new AuthorizationError(`Insufficient role. Required: ${requiredRoles.join(' or ')}`);
      }

      // Check permission requirements
      if (requiredPermissions) {
        for (const permission of requiredPermissions) {
          if (!AccessControl.hasPermission(user.role, user.permissions, permission)) {
            throw new AuthorizationError(`Missing required permission: ${permission}`);
          }
        }
      }

      // Add user to request
      (req as any).user = user;

      return handler(req as NextApiRequest & { user: User }, res);
    });
  };
}

/**
 * Session management functions
 */
export const SessionManager = {
  createSession: (userId: string, deviceInfo?: any) => sessionStore.createSession(userId, deviceInfo),
  getSession: (sessionId: string) => sessionStore.getSession(sessionId),
  invalidateSession: (sessionId: string) => sessionStore.invalidateSession(sessionId),
  invalidateAllUserSessions: (userId: string) => sessionStore.invalidateAllUserSessions(userId),
  cleanup: () => sessionStore.cleanup()
};

// Run cleanup every hour
setInterval(() => {
  SessionManager.cleanup();
}, 60 * 60 * 1000);