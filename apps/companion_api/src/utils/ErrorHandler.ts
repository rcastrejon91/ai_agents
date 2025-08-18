import { Request, Response, NextFunction } from 'express';
import * as Sentry from '@sentry/node';
import { Logger } from './Logger.js';

export class ErrorHandler {
  private static logger = new Logger('ErrorHandler');

  static async handle(
    error: any,
    req: Request,
    res: Response,
    next: NextFunction
  ): Promise<void> {
    // Enhancement: Structured error response
    const errorResponse = {
      error: {
        message: error.message || 'Internal server error',
        code: error.code || 500,
        type: error.name || 'Error'
      },
      requestId: (req as any).id || req.headers['x-request-id'] || 'unknown',
      timestamp: new Date().toISOString()
    };

    // Fix: Proper error status code mapping
    const statusCode = this.getHttpStatusCode(error);
    
    // Enhancement: Detailed error logging
    this.logError(error, req);
    
    // Don't send error details in production
    if (process.env.NODE_ENV === 'production' && statusCode >= 500) {
      errorResponse.error.message = 'Internal server error';
    }
    
    res.status(statusCode).json(errorResponse);
  }

  private static getHttpStatusCode(error: any): number {
    const errorMap: Record<string, number> = {
      ValidationError: 400,
      AuthenticationError: 401,
      AuthorizationError: 403,
      NotFoundError: 404,
      ConflictError: 409,
      RateLimitError: 429,
      TokenExpiredError: 401,
      JsonWebTokenError: 401,
      SyntaxError: 400
    };
    
    return errorMap[error.name] || error.statusCode || error.status || 500;
  }

  private static logError(error: any, req: Request): void {
    const errorInfo = {
      message: error.message,
      stack: error.stack,
      name: error.name,
      code: error.code,
      method: req.method,
      url: req.url,
      headers: req.headers,
      query: req.query,
      body: req.body,
      ip: req.ip,
      userAgent: req.get('User-Agent')
    };

    // Log to console
    this.logger.error('Request error occurred', errorInfo);

    // Send to Sentry if configured
    if (process.env.SENTRY_DSN) {
      Sentry.withScope(scope => {
        scope.setUser({ id: (req as any).user?.id });
        scope.setExtra('requestData', {
          method: req.method,
          url: req.url,
          headers: req.headers,
          query: req.query,
          body: req.body,
          ip: req.ip,
          userAgent: req.get('User-Agent')
        });
        scope.setLevel('error');
        Sentry.captureException(error);
      });
    }
  }

  static notFound(req: Request, res: Response, next: NextFunction): void {
    const error = new Error(`Not Found - ${req.originalUrl}`);
    error.name = 'NotFoundError';
    res.status(404);
    next(error);
  }

  static asyncHandler(fn: Function) {
    return (req: Request, res: Response, next: NextFunction) => {
      Promise.resolve(fn(req, res, next)).catch(next);
    };
  }

  static createError(message: string, type: string = 'Error', statusCode: number = 500): Error {
    const error = new Error(message);
    error.name = type;
    (error as any).statusCode = statusCode;
    return error;
  }
}