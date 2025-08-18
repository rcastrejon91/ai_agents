import { Logger } from '../../src/utils/Logger';
import { ErrorHandler } from '../../src/utils/ErrorHandler';
import jwt from 'jsonwebtoken';

describe('Core Components Unit Tests', () => {
  beforeAll(() => {
    process.env.JWT_SECRET = 'test-secret';
    process.env.NODE_ENV = 'test';
  });

  describe('Logger', () => {
    it('should create logger with context', () => {
      const logger = new Logger('TestContext');
      expect(logger).toBeDefined();
    });

    it('should log messages without throwing errors', () => {
      const logger = new Logger('TestContext');
      expect(() => {
        logger.info('Test info message');
        logger.error('Test error message');
        logger.warn('Test warn message');
        logger.debug('Test debug message');
      }).not.toThrow();
    });
  });

  describe('ErrorHandler', () => {
    it('should map error types to HTTP status codes correctly', () => {
      const validationError = new Error('Validation failed');
      validationError.name = 'ValidationError';
      
      const authError = new Error('Authentication failed');
      authError.name = 'AuthenticationError';
      
      // Access private method via any type for testing
      const getStatusCode = (ErrorHandler as any).getHttpStatusCode;
      
      expect(getStatusCode(validationError)).toBe(400);
      expect(getStatusCode(authError)).toBe(401);
    });

    it('should create custom errors', () => {
      const error = ErrorHandler.createError('Test error', 'TestError', 418);
      expect(error.message).toBe('Test error');
      expect(error.name).toBe('TestError');
      expect((error as any).statusCode).toBe(418);
    });

    it('should provide async handler wrapper', () => {
      const asyncFn = async (req: any, res: any, next: any) => {
        throw new Error('Async error');
      };
      
      const wrappedFn = ErrorHandler.asyncHandler(asyncFn);
      expect(wrappedFn).toBeDefined();
      expect(typeof wrappedFn).toBe('function');
    });
  });

  describe('JWT Operations', () => {
    it('should create and verify JWT tokens', () => {
      const payload = { userId: '123', username: 'test' };
      const secret = process.env.JWT_SECRET || 'test-secret';
      
      const token = jwt.sign(payload, secret, { expiresIn: '1h' });
      expect(token).toBeDefined();
      
      const decoded = jwt.verify(token, secret) as any;
      expect(decoded.userId).toBe('123');
      expect(decoded.username).toBe('test');
    });

    it('should reject expired tokens', () => {
      const payload = { userId: '123', username: 'test' };
      const secret = process.env.JWT_SECRET || 'test-secret';
      
      const expiredToken = jwt.sign(payload, secret, { expiresIn: '-1h' });
      
      expect(() => {
        jwt.verify(expiredToken, secret);
      }).toThrow();
    });
  });
});