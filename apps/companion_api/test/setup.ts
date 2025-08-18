// Test setup file
import dotenv from 'dotenv';

// Load test environment variables
dotenv.config({ path: '.env.test' });

// Set default test environment variables
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-secret-key-for-testing';
process.env.TEST_REDIS_HOST = process.env.TEST_REDIS_HOST || 'localhost';
process.env.TEST_REDIS_PORT = process.env.TEST_REDIS_PORT || '6379';
process.env.TEST_REDIS_DB = process.env.TEST_REDIS_DB || '1';

// Increase timeout for integration tests
jest.setTimeout(30000);

// Mock console methods for cleaner test output
const originalConsole = { ...console };

beforeAll(() => {
  // Mock console.log to reduce noise during tests
  console.log = jest.fn();
  console.info = jest.fn();
  
  // Keep error and warn for debugging
  console.error = originalConsole.error;
  console.warn = originalConsole.warn;
});

afterAll(() => {
  // Restore console methods
  Object.assign(console, originalConsole);
});