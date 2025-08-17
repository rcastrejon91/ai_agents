/**
 * Authentication routes
 */
import { Router, Response } from 'express';
import { Config } from '../config/env.js';
import { generateTokens, verifyToken, jwtAuthMiddleware } from '../middleware/auth.js';
import { AppError, asyncHandler } from '../middleware/error.js';
import { AuthenticatedRequest } from '../middleware/security.js';

export const createAuthRoutes = (config: Config) => {
  const router = Router();

  /**
   * Login endpoint - generates JWT tokens
   * In a real app, this would validate credentials against a database
   */
  router.post('/login', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const { email, password } = req.body;

    if (!email || !password) {
      throw new AppError('Email and password are required', 400, 'MISSING_CREDENTIALS');
    }

    // TODO: Implement actual credential validation
    // For now, we'll create a mock user for demonstration
    const user = {
      id: 'user_' + Date.now(),
      email: email
    };

    const tokens = generateTokens(user, config);

    res.json({
      message: 'Login successful',
      user: {
        id: user.id,
        email: user.email
      },
      tokens,
      requestId: req.id
    });
  }));

  /**
   * Refresh token endpoint
   */
  router.post('/refresh', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      throw new AppError('Refresh token is required', 400, 'MISSING_REFRESH_TOKEN');
    }

    const payload = verifyToken(refreshToken, config.jwt.refreshSecret);

    if (!payload || payload.type !== 'refresh') {
      throw new AppError('Invalid or expired refresh token', 401, 'INVALID_REFRESH_TOKEN');
    }

    const user = {
      id: payload.userId,
      email: payload.email
    };

    const tokens = generateTokens(user, config);

    res.json({
      message: 'Tokens refreshed successfully',
      user,
      tokens,
      requestId: req.id
    });
  }));

  /**
   * Logout endpoint (client-side should discard tokens)
   */
  router.post('/logout', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    // In a more sophisticated implementation, we might maintain a blacklist of tokens
    res.json({
      message: 'Logout successful',
      requestId: req.id
    });
  }));

  /**
   * Get current user profile
   */
  router.get('/me', jwtAuthMiddleware(config), asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    res.json({
      user: req.user,
      requestId: req.id
    });
  }));

  return router;
};