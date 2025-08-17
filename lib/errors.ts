/**
 * Comprehensive Error Handling System
 * Provides custom error classes, structured logging, and global error handling
 */

/**
 * Base error class with structured logging support
 */
export class BaseError extends Error {
  public readonly statusCode: number;
  public readonly errorCode: string;
  public readonly isOperational: boolean;
  public readonly metadata?: Record<string, any>;
  public readonly timestamp: Date;

  constructor(
    message: string,
    statusCode: number = 500,
    errorCode: string = 'INTERNAL_ERROR',
    isOperational: boolean = true,
    metadata?: Record<string, any>
  ) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    this.isOperational = isOperational;
    this.metadata = metadata;
    this.timestamp = new Date();

    // Maintains proper stack trace for V8 engines
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      statusCode: this.statusCode,
      errorCode: this.errorCode,
      timestamp: this.timestamp.toISOString(),
      metadata: this.metadata
    };
  }
}

/**
 * Authentication and authorization errors
 */
export class AuthenticationError extends BaseError {
  constructor(message: string = 'Authentication failed', metadata?: Record<string, any>) {
    super(message, 401, 'AUTH_FAILED', true, metadata);
  }
}

export class AuthorizationError extends BaseError {
  constructor(message: string = 'Insufficient permissions', metadata?: Record<string, any>) {
    super(message, 403, 'INSUFFICIENT_PERMISSIONS', true, metadata);
  }
}

export class TokenExpiredError extends BaseError {
  constructor(message: string = 'Token has expired', metadata?: Record<string, any>) {
    super(message, 401, 'TOKEN_EXPIRED', true, metadata);
  }
}

/**
 * Validation errors
 */
export class ValidationError extends BaseError {
  constructor(message: string = 'Validation failed', metadata?: Record<string, any>) {
    super(message, 400, 'VALIDATION_ERROR', true, metadata);
  }
}

export class InvalidInputError extends BaseError {
  constructor(message: string = 'Invalid input provided', metadata?: Record<string, any>) {
    super(message, 400, 'INVALID_INPUT', true, metadata);
  }
}

/**
 * Resource errors
 */
export class NotFoundError extends BaseError {
  constructor(message: string = 'Resource not found', metadata?: Record<string, any>) {
    super(message, 404, 'NOT_FOUND', true, metadata);
  }
}

export class ConflictError extends BaseError {
  constructor(message: string = 'Resource conflict', metadata?: Record<string, any>) {
    super(message, 409, 'CONFLICT', true, metadata);
  }
}

/**
 * Rate limiting errors
 */
export class RateLimitError extends BaseError {
  constructor(message: string = 'Rate limit exceeded', metadata?: Record<string, any>) {
    super(message, 429, 'RATE_LIMIT_EXCEEDED', true, metadata);
  }
}

/**
 * External service errors
 */
export class ExternalServiceError extends BaseError {
  constructor(message: string = 'External service error', metadata?: Record<string, any>) {
    super(message, 503, 'EXTERNAL_SERVICE_ERROR', true, metadata);
  }
}

export class DatabaseError extends BaseError {
  constructor(message: string = 'Database error', metadata?: Record<string, any>) {
    super(message, 500, 'DATABASE_ERROR', true, metadata);
  }
}

/**
 * Security errors
 */
export class SecurityError extends BaseError {
  constructor(message: string = 'Security violation detected', metadata?: Record<string, any>) {
    super(message, 403, 'SECURITY_VIOLATION', true, metadata);
  }
}

export class CorsError extends BaseError {
  constructor(message: string = 'CORS policy violation', metadata?: Record<string, any>) {
    super(message, 403, 'CORS_VIOLATION', true, metadata);
  }
}

/**
 * Structured error logger
 */
export class ErrorLogger {
  private static instance: ErrorLogger;

  static getInstance(): ErrorLogger {
    if (!ErrorLogger.instance) {
      ErrorLogger.instance = new ErrorLogger();
    }
    return ErrorLogger.instance;
  }

  log(error: Error, context?: Record<string, any>) {
    const errorInfo = {
      timestamp: new Date().toISOString(),
      name: error.name,
      message: error.message,
      stack: error.stack,
      context
    };

    if (error instanceof BaseError) {
      Object.assign(errorInfo, {
        statusCode: error.statusCode,
        errorCode: error.errorCode,
        isOperational: error.isOperational,
        metadata: error.metadata
      });
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error occurred:', errorInfo);
    }

    // In production, you would send this to your logging service
    // Example: await logToService(errorInfo);
    
    return errorInfo;
  }

  logHttpError(req: any, error: Error) {
    const context = {
      method: req.method,
      url: req.url,
      headers: req.headers,
      body: req.body,
      ip: req.ip || req.connection?.remoteAddress,
      userAgent: req.headers?.['user-agent']
    };

    return this.log(error, context);
  }
}

/**
 * Global error handler for Next.js API routes
 */
export function withErrorHandler(handler: Function) {
  return async (req: any, res: any) => {
    try {
      return await handler(req, res);
    } catch (error) {
      const logger = ErrorLogger.getInstance();
      const errorInfo = logger.logHttpError(req, error as Error);

      // Determine response based on error type
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({
          error: error.message,
          code: error.errorCode,
          timestamp: error.timestamp.toISOString()
        });
      } else {
        // Don't expose internal errors in production
        const isProduction = process.env.NODE_ENV === 'production';
        res.status(500).json({
          error: isProduction ? 'Internal server error' : (error as Error).message,
          code: 'INTERNAL_ERROR',
          timestamp: new Date().toISOString()
        });
      }
    }
  };
}

/**
 * Error monitoring integration placeholder
 */
export class ErrorMonitoring {
  static async reportError(error: Error, context?: Record<string, any>) {
    // Integrate with services like Sentry, Bugsnag, etc.
    // Example:
    // await Sentry.captureException(error, { extra: context });
    
    const logger = ErrorLogger.getInstance();
    logger.log(error, context);
  }

  static async reportHttpError(req: any, error: Error) {
    const context = {
      method: req.method,
      url: req.url,
      userAgent: req.headers?.['user-agent'],
      ip: req.ip
    };

    await this.reportError(error, context);
  }
}