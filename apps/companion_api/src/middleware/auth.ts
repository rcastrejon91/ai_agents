/**
 * JWT Authentication middleware and utilities
 */
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { Config } from '../config/env.js';
import { AuthenticatedRequest } from './security.js';

export interface JwtPayload {
  userId: string;
  email?: string;
  type: 'access' | 'refresh';
}

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
}

/**
 * Generate JWT access and refresh tokens
 */
export const generateTokens = (user: { id: string; email?: string }, config: Config): TokenPair => {
  const accessPayload: JwtPayload = {
    userId: user.id,
    email: user.email,
    type: 'access'
  };

  const refreshPayload: JwtPayload = {
    userId: user.id,
    email: user.email,
    type: 'refresh'
  };

  const accessToken = jwt.sign(
    accessPayload,
    config.jwt.secret,
    { expiresIn: config.jwt.accessExpiresIn } as jwt.SignOptions
  );

  const refreshToken = jwt.sign(
    refreshPayload,
    config.jwt.refreshSecret,
    { expiresIn: config.jwt.refreshExpiresIn } as jwt.SignOptions
  );

  return { accessToken, refreshToken };
};

/**
 * Verify JWT token
 */
export const verifyToken = (token: string, secret: string): JwtPayload | null => {
  try {
    return jwt.verify(token, secret) as JwtPayload;
  } catch (error) {
    return null;
  }
};

/**
 * JWT Authentication middleware
 */
export const jwtAuthMiddleware = (config: Config) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        status: 401,
        message: 'Access token required',
        requestId: req.id
      });
    }

    const token = authHeader.substring(7);
    const payload = verifyToken(token, config.jwt.secret);

    if (!payload || payload.type !== 'access') {
      return res.status(401).json({
        status: 401,
        message: 'Invalid or expired access token',
        requestId: req.id
      });
    }

    req.user = {
      userId: payload.userId,
      email: payload.email
    };

    next();
  };
};

/**
 * Optional JWT Authentication middleware (doesn't fail if no token)
 */
export const optionalJwtAuthMiddleware = (config: Config) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    const authHeader = req.headers.authorization;
    
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      const payload = verifyToken(token, config.jwt.secret);

      if (payload && payload.type === 'access') {
        req.user = {
          userId: payload.userId,
          email: payload.email
        };
      }
    }

    next();
  };
};