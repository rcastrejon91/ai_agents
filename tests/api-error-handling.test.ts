/**
 * Test suite for API error handling improvements
 * 
 * Tests the enhanced Lyra API error handling including:
 * - Request validation
 * - Error response format
 * - Timeout handling
 * - Health checks
 */

import { 
  validateLyraRequest, 
  ValidationError, 
  fetchWithRetry, 
  TimeoutError,
  checkOpenAIHealth,
  generateRequestId,
  TIMEOUT_CONFIG 
} from '../apps/companion_web/lib/api-errors';

// Mock environment variables for testing
process.env.OPENAI_API_KEY = 'sk-test-key-12345';

describe('API Error Handling', () => {
  
  describe('Request Validation', () => {
    
    test('validates valid request', () => {
      const validRequest = {
        message: 'Hello, world!',
        history: [
          { role: 'user', content: 'Previous message' },
          { role: 'assistant', content: 'Previous response' }
        ]
      };
      
      const result = validateLyraRequest(validRequest);
      expect(result.message).toBe('Hello, world!');
      expect(result.history).toHaveLength(2);
    });
    
    test('rejects empty message', () => {
      expect(() => {
        validateLyraRequest({ message: '' });
      }).toThrow(ValidationError);
    });
    
    test('rejects message too long', () => {
      const longMessage = 'a'.repeat(10001);
      expect(() => {
        validateLyraRequest({ message: longMessage });
      }).toThrow(ValidationError);
    });
    
    test('rejects invalid history format', () => {
      expect(() => {
        validateLyraRequest({ 
          message: 'test',
          history: [{ invalid: 'format' }]
        });
      }).toThrow(ValidationError);
    });
    
    test('rejects history too long', () => {
      const longHistory = Array(51).fill({ role: 'user', content: 'test' });
      expect(() => {
        validateLyraRequest({ 
          message: 'test',
          history: longHistory
        });
      }).toThrow(ValidationError);
    });
    
  });
  
  describe('Error Response Format', () => {
    
    test('ValidationError has correct format', () => {
      const error = new ValidationError('Test validation error', { field: 'message' });
      
      expect(error.code).toBe('VALIDATION_ERROR');
      expect(error.statusCode).toBe(400);
      expect(error.message).toBe('Test validation error');
      expect(error.details).toEqual({ field: 'message' });
      expect(error.isOperational).toBe(true);
    });
    
  });
  
  describe('Request ID Generation', () => {
    
    test('generates unique request IDs', () => {
      const id1 = generateRequestId();
      const id2 = generateRequestId();
      
      expect(id1).toMatch(/^req_\d+_[a-z0-9]+$/);
      expect(id2).toMatch(/^req_\d+_[a-z0-9]+$/);
      expect(id1).not.toBe(id2);
    });
    
  });
  
  describe('Timeout Configuration', () => {
    
    test('has proper timeout configuration', () => {
      expect(TIMEOUT_CONFIG.DEFAULT).toBe(30000);
      expect(TIMEOUT_CONFIG.OPENAI).toBe(45000);
      expect(TIMEOUT_CONFIG.MAX_RETRIES).toBe(3);
    });
    
  });
  
  describe('Health Check', () => {
    
    test('returns health status structure', async () => {
      // Mock fetch to simulate OpenAI health check
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
      });
      
      const health = await checkOpenAIHealth();
      
      expect(health).toHaveProperty('status');
      expect(['healthy', 'degraded', 'unhealthy']).toContain(health.status);
      
      if (health.status === 'healthy') {
        expect(health).toHaveProperty('latency');
        expect(typeof health.latency).toBe('number');
      }
    });
    
  });
  
});

// Integration test helper
export async function testLyraAPIEndpoint(baseUrl: string) {
  const tests = [];
  
  // Test health endpoint
  try {
    const healthResponse = await fetch(`${baseUrl}/api/health`);
    const healthData = await healthResponse.json();
    
    tests.push({
      name: 'Health Check',
      passed: healthResponse.status === 200 || healthResponse.status === 503,
      details: healthData
    });
  } catch (error) {
    tests.push({
      name: 'Health Check',
      passed: false,
      error: error.message
    });
  }
  
  // Test Lyra endpoint with valid request
  try {
    const lyraResponse = await fetch(`${baseUrl}/api/lyra`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'Hello test' })
    });
    
    const lyraData = await lyraResponse.json();
    
    tests.push({
      name: 'Lyra API Valid Request',
      passed: lyraResponse.status === 200 && lyraData.reply,
      details: lyraData
    });
  } catch (error) {
    tests.push({
      name: 'Lyra API Valid Request',
      passed: false,
      error: error.message
    });
  }
  
  // Test Lyra endpoint with invalid request
  try {
    const invalidResponse = await fetch(`${baseUrl}/api/lyra`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: '' }) // Empty message should fail
    });
    
    const invalidData = await invalidResponse.json();
    
    tests.push({
      name: 'Lyra API Invalid Request',
      passed: invalidResponse.status === 400 && invalidData.code === 'VALIDATION_ERROR',
      details: invalidData
    });
  } catch (error) {
    tests.push({
      name: 'Lyra API Invalid Request',
      passed: false,
      error: error.message
    });
  }
  
  // Test method not allowed
  try {
    const methodResponse = await fetch(`${baseUrl}/api/lyra`, {
      method: 'GET'
    });
    
    tests.push({
      name: 'Method Not Allowed',
      passed: methodResponse.status === 405,
      details: { status: methodResponse.status }
    });
  } catch (error) {
    tests.push({
      name: 'Method Not Allowed',
      passed: false,
      error: error.message
    });
  }
  
  return tests;
}

console.log('API Error Handling Tests Created');