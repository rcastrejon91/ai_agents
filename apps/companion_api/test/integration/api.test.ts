import request from 'supertest';
import express from 'express';
import { TestDatabase } from '../utils/TestDatabase';
import { TestRedis } from '../utils/TestRedis';
import { AuthenticationService } from '../../src/security/AuthenticationService';
import { ErrorHandler } from '../../src/utils/ErrorHandler';
import { CacheManager } from '../../src/utils/CacheManager';
import { MetricsCollector } from '../../src/monitoring/MetricsCollector';
import jwt from 'jsonwebtoken';

// Mock app for testing
const createTestApp = () => {
  const app = express();
  const metricsCollector = new MetricsCollector();
  
  app.use(express.json());
  app.use(metricsCollector.createMiddleware());

  // Test routes
  app.post('/auth/login', (req, res) => {
    const { username, password } = req.body;
    
    if (username === 'testuser' && password === 'testpass') {
      const accessToken = jwt.sign(
        { userId: '123', username }, 
        process.env.JWT_SECRET || 'test-secret',
        { expiresIn: '1h' }
      );
      const refreshToken = jwt.sign(
        { userId: '123', type: 'refresh' }, 
        process.env.JWT_SECRET || 'test-secret',
        { expiresIn: '7d' }
      );
      
      res.json({ accessToken, refreshToken });
    } else {
      res.status(401).json({ error: 'Invalid credentials' });
    }
  });

  app.get('/protected-route', async (req, res) => {
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const authService = new AuthenticationService();
    const isValid = await authService.validateToken(token);
    
    if (isValid) {
      res.json({ message: 'Access granted', user: { id: '123' } });
    } else {
      res.status(401).json({ error: 'Invalid token' });
    }
  });

  // Rate limiting test route
  let requestCount = 0;
  app.get('/api/test', (req, res) => {
    requestCount++;
    if (requestCount > 10) {
      return res.status(429).json({ error: 'Too many requests' });
    }
    res.json({ message: 'Success', count: requestCount });
  });

  // Metrics endpoint
  app.get('/metrics', async (req, res) => {
    try {
      const metrics = await metricsCollector.getMetrics();
      res.set('Content-Type', 'text/plain').send(metrics);
    } catch (error) {
      res.status(500).json({ error: 'Failed to get metrics' });
    }
  });

  // Error handling
  app.use(metricsCollector.createErrorMiddleware());
  app.use(ErrorHandler.handle);

  return app;
};

describe('API Integration Tests', () => {
  let testDb: TestDatabase;
  let testRedis: TestRedis;
  let app: express.Application;

  beforeAll(async () => {
    testDb = await TestDatabase.init();
    testRedis = await TestRedis.init();
    app = createTestApp();
    
    // Set test environment variables
    process.env.JWT_SECRET = 'test-secret';
    process.env.NODE_ENV = 'test';
  });

  afterAll(async () => {
    await testDb.cleanup();
    await testRedis.cleanup();
  });

  beforeEach(async () => {
    if (testRedis.isAvailable()) {
      await testRedis.clear();
    }
  });

  describe('Authentication', () => {
    it('should properly handle token validation', async () => {
      const response = await request(app)
        .post('/auth/login')
        .send({
          username: 'testuser',
          password: 'testpass'
        });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('accessToken');
      expect(response.body).toHaveProperty('refreshToken');
      expect(response.body.accessToken).toMatch(/^[\w-]+\.[\w-]+\.[\w-]+$/);
    });

    it('should reject invalid credentials', async () => {
      const response = await request(app)
        .post('/auth/login')
        .send({
          username: 'testuser',
          password: 'wrongpass'
        });

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('error', 'Invalid credentials');
    });

    it('should properly handle invalid tokens', async () => {
      const response = await request(app)
        .get('/protected-route')
        .set('Authorization', 'Bearer invalid-token');

      expect(response.status).toBe(401);
    });

    it('should accept valid tokens', async () => {
      // First login to get a valid token
      const loginResponse = await request(app)
        .post('/auth/login')
        .send({
          username: 'testuser',
          password: 'testpass'
        });

      const { accessToken } = loginResponse.body;

      // Use the token to access protected route
      const response = await request(app)
        .get('/protected-route')
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('message', 'Access granted');
    });

    it('should reject requests without tokens', async () => {
      const response = await request(app)
        .get('/protected-route');

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('error', 'No token provided');
    });
  });

  describe('Rate Limiting', () => {
    it('should enforce rate limits', async () => {
      const requests = Array(12).fill(null).map(() =>
        request(app).get('/api/test')
      );

      const responses = await Promise.all(requests);
      const tooManyRequests = responses.filter(r => r.status === 429);
      expect(tooManyRequests.length).toBeGreaterThan(0);
    });

    it('should allow requests within limits', async () => {
      const response = await request(app).get('/api/test');
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('message', 'Success');
    });
  });

  describe('Error Handling', () => {
    it('should handle 404 errors properly', async () => {
      const response = await request(app).get('/nonexistent-route');
      expect(response.status).toBe(404);
    });

    it('should return structured error responses', async () => {
      const response = await request(app).get('/nonexistent-route');
      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toHaveProperty('message');
      expect(response.body.error).toHaveProperty('code');
      expect(response.body.error).toHaveProperty('type');
      expect(response.body).toHaveProperty('timestamp');
    });
  });

  describe('Metrics', () => {
    it('should provide metrics endpoint', async () => {
      const response = await request(app).get('/metrics');
      expect(response.status).toBe(200);
      expect(response.headers['content-type']).toBe('text/plain; charset=utf-8');
      expect(response.text).toContain('process_memory_usage_bytes');
    });

    it('should track request metrics', async () => {
      // Make a few requests
      await request(app).get('/api/test');
      await request(app).get('/api/test');
      
      const response = await request(app).get('/metrics');
      expect(response.text).toContain('http_requests_total');
      expect(response.text).toContain('http_request_duration_seconds');
    });
  });

  describe('Cache Manager', () => {
    it('should handle cache operations gracefully when Redis is unavailable', async () => {
      const cacheManager = new CacheManager();
      
      // These should not throw errors even if Redis is unavailable
      await expect(cacheManager.get('test-key')).resolves.toBeNull();
      await expect(cacheManager.set('test-key', 'test-value')).resolves.toBeUndefined();
      await expect(cacheManager.del('test-key')).resolves.toBeUndefined();
    });

    it('should perform cache operations when Redis is available', async () => {
      if (!testRedis.isAvailable()) {
        console.log('Skipping Redis-dependent test - Redis not available');
        return;
      }

      const cacheManager = new CacheManager();
      
      // Test set and get
      await cacheManager.set('test-key', { data: 'test-value' });
      const result = await cacheManager.get('test-key');
      expect(result).toEqual({ data: 'test-value' });
      
      // Test deletion
      await cacheManager.del('test-key');
      const deletedResult = await cacheManager.get('test-key');
      expect(deletedResult).toBeNull();
    });
  });

  describe('Authentication Service', () => {
    it('should validate JWT tokens correctly', async () => {
      const authService = new AuthenticationService();
      
      const validToken = jwt.sign(
        { userId: '123', username: 'test' }, 
        process.env.JWT_SECRET || 'test-secret',
        { expiresIn: '1h' }
      );
      
      const isValid = await authService.validateToken(validToken);
      expect(isValid).toBe(true);
    });

    it('should reject expired tokens', async () => {
      const authService = new AuthenticationService();
      
      const expiredToken = jwt.sign(
        { userId: '123', username: 'test' }, 
        process.env.JWT_SECRET || 'test-secret',
        { expiresIn: '-1h' } // Already expired
      );
      
      const isValid = await authService.validateToken(expiredToken);
      expect(isValid).toBe(false);
    });

    it('should reject invalid tokens', async () => {
      const authService = new AuthenticationService();
      const isValid = await authService.validateToken('invalid-token');
      expect(isValid).toBe(false);
    });
  });
});