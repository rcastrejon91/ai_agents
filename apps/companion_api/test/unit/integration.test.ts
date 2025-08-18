import { MetricsCollector } from '../../src/monitoring/MetricsCollector';
import { CacheManager } from '../../src/utils/CacheManager';
import { AuthenticationService } from '../../src/security/AuthenticationService';

describe('Integration Components Tests', () => {
  beforeAll(() => {
    process.env.NODE_ENV = 'test';
    process.env.JWT_SECRET = 'test-secret';
  });

  describe('MetricsCollector', () => {
    beforeEach(() => {
      // Clear metrics registry before each test
      const { register } = require('prom-client');
      register.clear();
    });

    it('should create metrics collector instance', () => {
      const metrics = new MetricsCollector();
      expect(metrics).toBeDefined();
    });

    it('should track requests without errors', () => {
      const metrics = new MetricsCollector();
      expect(() => {
        metrics.trackRequest('GET', '/test', 0.5, 200);
        metrics.trackError('TestError', '500', '/test');
      }).not.toThrow();
    });

    it('should provide middleware functions', () => {
      const metrics = new MetricsCollector();
      const middleware = metrics.createMiddleware();
      const errorMiddleware = metrics.createErrorMiddleware();
      
      expect(typeof middleware).toBe('function');
      expect(typeof errorMiddleware).toBe('function');
    });

    it('should get health metrics', () => {
      const metrics = new MetricsCollector();
      const health = metrics.getHealthMetrics();
      
      expect(health).toHaveProperty('memory');
      expect(health).toHaveProperty('uptime');
      expect(health).toHaveProperty('timestamp');
    });
  });

  describe('CacheManager', () => {
    it('should create cache manager instance', () => {
      const cache = new CacheManager();
      expect(cache).toBeDefined();
    });

    it('should handle cache operations gracefully when Redis unavailable', async () => {
      const cache = new CacheManager();
      
      // These should not throw even if Redis is unavailable
      await expect(cache.get('test')).resolves.toBeNull();
      await expect(cache.set('test', 'value')).resolves.toBeUndefined();
      await expect(cache.del('test')).resolves.toBeUndefined();
      await expect(cache.exists('test')).resolves.toBe(false);
    });

    it('should handle connection status check', async () => {
      const cache = new CacheManager();
      const isConnected = await cache.isConnected();
      expect(typeof isConnected).toBe('boolean');
    });
  });

  describe('AuthenticationService', () => {
    let authService: AuthenticationService;

    beforeEach(() => {
      authService = new AuthenticationService();
    });

    afterEach(async () => {
      await authService.cleanup();
    });

    it('should create authentication service instance', () => {
      expect(authService).toBeDefined();
    });

    it('should handle token validation when Redis unavailable', async () => {
      // Should not throw even if Redis is unavailable
      const result = await authService.validateToken('invalid-token');
      expect(typeof result).toBe('boolean');
    });

    it('should handle session operations gracefully', async () => {
      // These should not throw even if Redis is unavailable
      await expect(authService.revokeUserSessions('user123')).resolves.toBeUndefined();
      await expect(authService.blacklistToken('token123')).resolves.toBeUndefined();
    });
  });
});