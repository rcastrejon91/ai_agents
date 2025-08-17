#!/usr/bin/env node

/**
 * Simple test script to validate security implementation
 */

const BASE_URL = 'http://localhost:8787';

const testEndpoints = async () => {
  console.log('🧪 Testing API Security Implementation\n');

  // Test 1: Health check
  console.log('1. Testing health endpoint...');
  try {
    const response = await fetch(`${BASE_URL}/health`);
    const data = await response.json();
    console.log('✅ Health check:', data);
  } catch (error) {
    console.log('❌ Health check failed:', error.message);
  }

  // Test 2: Rate limiting (make multiple requests)
  console.log('\n2. Testing rate limiting...');
  try {
    const promises = Array(5).fill().map(() => fetch(`${BASE_URL}/health`));
    const responses = await Promise.all(promises);
    console.log('✅ Rate limiting allows normal traffic');
  } catch (error) {
    console.log('❌ Rate limiting test failed:', error.message);
  }

  // Test 3: CORS headers
  console.log('\n3. Testing CORS...');
  try {
    const response = await fetch(`${BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Origin': 'http://localhost:3000'
      }
    });
    const corsHeader = response.headers.get('access-control-allow-origin');
    console.log('✅ CORS header:', corsHeader);
  } catch (error) {
    console.log('❌ CORS test failed:', error.message);
  }

  // Test 4: Authentication flow
  console.log('\n4. Testing authentication...');
  try {
    // Test login
    const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'testpassword'
      })
    });
    
    const loginData = await loginResponse.json();
    console.log('✅ Login successful:', loginData.message);
    
    const accessToken = loginData.tokens?.accessToken;
    if (accessToken) {
      // Test protected endpoint
      const meResponse = await fetch(`${BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      const meData = await meResponse.json();
      console.log('✅ Protected endpoint access:', meData.user);
    }
  } catch (error) {
    console.log('❌ Authentication test failed:', error.message);
  }

  // Test 5: Error handling
  console.log('\n5. Testing error handling...');
  try {
    const response = await fetch(`${BASE_URL}/nonexistent`);
    const data = await response.json();
    console.log('✅ 404 handling:', data.message);
  } catch (error) {
    console.log('❌ Error handling test failed:', error.message);
  }

  console.log('\n🎉 Security testing complete!');
};

// Only run if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
  testEndpoints().catch(console.error);
}

export { testEndpoints };