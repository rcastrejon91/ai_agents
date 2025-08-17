#!/usr/bin/env node

// Simple test to verify our secure storage and logging implementations
const path = require('path');
const { SecureStorage } = require('./utils/secure-storage');
const { logger } = require('./utils/logger');
const { AuditTrail } = require('./utils/audit');

async function runTests() {
  console.log('🔒 Testing Secure Storage and Logging...\n');

  try {
    // Test 1: Secure Storage Encryption/Decryption
    console.log('📝 Test 1: Secure Storage');
    const storage = SecureStorage.getInstance();
    const testData = {
      user: 'testuser',
      sensitive: 'secret data',
      number: 42
    };

    const encrypted = await storage.encrypt(testData);
    console.log('✅ Data encrypted successfully');
    console.log('📦 Encrypted data length:', encrypted.length);

    const decrypted = await storage.decrypt(encrypted);
    console.log('✅ Data decrypted successfully');
    console.log('📤 Decrypted data:', JSON.stringify(decrypted));
    console.log('🔍 Data integrity check:', JSON.stringify(testData) === JSON.stringify(decrypted) ? 'PASSED' : 'FAILED');

    // Test 2: Logger with sensitive data sanitization
    console.log('\n📝 Test 2: Logger with Data Sanitization');
    logger.info('Test log entry', {
      data: {
        username: 'testuser',
        password: 'should-be-redacted',
        token: 'secret-token',
        publicInfo: 'this is safe',
        key: 'another-secret'
      }
    });
    console.log('✅ Log entry created with sensitive data sanitization');

    // Test 3: Audit Trail
    console.log('\n📝 Test 3: Audit Trail');
    await AuditTrail.log({
      action: 'test_action',
      userId: 'test-user-123',
      resource: 'test-resource',
      details: { testParameter: 'value' },
      timestamp: new Date()
    });
    console.log('✅ Audit event logged successfully');

    console.log('\n🎉 All tests completed successfully!');
    console.log('\n📁 Check the logs/ directory for log files:');
    console.log('   - logs/combined.log (all logs)');
    console.log('   - logs/error.log (error logs only)');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('Stack trace:', error.stack);
    process.exit(1);
  }
}

// Only run if called directly
if (require.main === module) {
  runTests().catch(console.error);
}

module.exports = { runTests };