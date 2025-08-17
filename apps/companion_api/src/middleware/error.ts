/**
 * Error handling middleware
 */
import { Request, Response, NextFunction } from 'express';
import { AuthenticatedRequest } from './security.js';

export interface ApiError extends Error {
  status?: number;
  code?: string;
}

/**
 * Custom error class for API errors
 */
export class AppError extends Error implements ApiError {
  public status: number;
  public code: string;

  constructor(message: string, status: number = 500, code: string = 'INTERNAL_ERROR') {
    super(message);
    this.status = status;
    this.code = code;
    this.name = 'AppError';
  }
}

/**
 * Simple logger utility
 */
export const logger = {
  error: (data: any) => {
    console.error('[ERROR]', new Date().toISOString(), JSON.stringify(data, null, 2));
  },
  warn: (data: any) => {
    console.warn('[WARN]', new Date().toISOString(), JSON.stringify(data, null, 2));
  },
  info: (data: any) => {
    console.info('[INFO]', new Date().toISOString(), JSON.stringify(data, null, 2));
  },
  debug: (data: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.debug('[DEBUG]', new Date().toISOString(), JSON.stringify(data, null, 2));
    }
  }
};

/**
 * Global error handler middleware
 */
export const errorHandler = (
  err: ApiError,
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
) => {
  const status = err.status || 500;
  const message = err.message || 'Internal server error';
  const code = (err as AppError).code || 'INTERNAL_ERROR';

  // Log error details
  logger.error({
    error: {
      name: err.name,
      message: err.message,
      stack: err.stack,
      code,
      status
    },
    request: {
      method: req.method,
      path: req.path,
      headers: {
        'user-agent': req.headers['user-agent'],
        'content-type': req.headers['content-type'],
        'origin': req.headers.origin,
        'referer': req.headers.referer
      },
      query: req.query,
      params: req.params,
      userId: req.user?.userId || 'anonymous'
    },
    requestId: req.id,
    timestamp: new Date().toISOString()
  });

  // Don't expose internal error details in production
  const isProduction = process.env.NODE_ENV === 'production';
  const responseMessage = isProduction && status === 500 
    ? 'Internal server error' 
    : message;

  res.status(status).json({
    status,
    message: responseMessage,
    code,
    requestId: req.id,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

/**
 * 404 handler middleware
 */
export const notFoundHandler = (req: AuthenticatedRequest, res: Response) => {
  const error = new AppError(`Route ${req.method} ${req.path} not found`, 404, 'NOT_FOUND');
  
  logger.warn({
    message: 'Route not found',
    request: {
      method: req.method,
      path: req.path,
      headers: {
        'user-agent': req.headers['user-agent'],
        'origin': req.headers.origin
      }
    },
    requestId: req.id,
    timestamp: new Date().toISOString()
  });

  res.status(404).json({
    status: 404,
    message: error.message,
    code: error.code,
    requestId: req.id
  });
};

/**
 * Async error wrapper utility
 */
export const asyncHandler = (fn: Function) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};