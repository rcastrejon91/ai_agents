#!/usr/bin/env node

/**
 * Demo script to test the enhanced API error handling
 * 
 * This script demonstrates:
 * - Health check endpoint
 * - Request validation
 * - Error response formats
 * - Monitoring capabilities
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

async function makeRequest(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    return { status: response.status, data, ok: response.ok };
  } catch (error) {
    return { status: 0, error: error.message, ok: false };
  }
}

async function testHealthEndpoint() {
  console.log('\n🏥 Testing Health Endpoint...');
  const result = await makeRequest(`${BASE_URL}/api/health`);
  
  console.log(`Status: ${result.status}`);
  console.log(`Response:`, JSON.stringify(result.data, null, 2));
  
  if (result.ok && result.data.status) {
    console.log(`✅ Health check passed - Status: ${result.data.status}`);
    if (result.data.services?.openai) {
      console.log(`   OpenAI Status: ${result.data.services.openai.status}`);
      if (result.data.services.openai.latency) {
        console.log(`   OpenAI Latency: ${result.data.services.openai.latency}ms`);
      }
    }
  } else {
    console.log('❌ Health check failed');
  }
}

async function testLyraValidRequest() {
  console.log('\n💬 Testing Lyra API with Valid Request...');
  const result = await makeRequest(`${BASE_URL}/api/lyra`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: 'Hello, this is a test message for the enhanced error handling system.'
    })
  });
  
  console.log(`Status: ${result.status}`);
  console.log(`Response:`, JSON.stringify(result.data, null, 2));
  
  if (result.ok && result.data.reply) {
    console.log(`✅ Valid request processed successfully`);
    console.log(`   Reply: ${result.data.reply.substring(0, 100)}...`);
    console.log(`   Model: ${result.data.model}`);
    console.log(`   Request ID: ${result.data.requestId}`);
  } else {
    console.log('❌ Valid request failed');
  }
}

async function testLyraInvalidRequest() {
  console.log('\n❌ Testing Lyra API with Invalid Request (empty message)...');
  const result = await makeRequest(`${BASE_URL}/api/lyra`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: ''  // Empty message should trigger validation error
    })
  });
  
  console.log(`Status: ${result.status}`);
  console.log(`Response:`, JSON.stringify(result.data, null, 2));
  
  if (result.status === 400 && result.data.code === 'VALIDATION_ERROR') {
    console.log(`✅ Validation error handled correctly`);
    console.log(`   Error Code: ${result.data.code}`);
    console.log(`   Error Message: ${result.data.message}`);
  } else {
    console.log('❌ Validation error not handled correctly');
  }
}

async function testLyraMethodNotAllowed() {
  console.log('\n🚫 Testing Lyra API with Invalid Method (GET)...');
  const result = await makeRequest(`${BASE_URL}/api/lyra`, {
    method: 'GET'
  });
  
  console.log(`Status: ${result.status}`);
  console.log(`Response:`, JSON.stringify(result.data, null, 2));
  
  if (result.status === 405) {
    console.log(`✅ Method not allowed handled correctly`);
    console.log(`   Error Code: ${result.data.code}`);
    console.log(`   Error Message: ${result.data.message}`);
  } else {
    console.log('❌ Method not allowed not handled correctly');
  }
}

async function testLyraPingEndpoint() {
  console.log('\n🏓 Testing Lyra Ping (Health Check)...');
  const result = await makeRequest(`${BASE_URL}/api/lyra?ping=1`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: 'ping'
    })
  });
  
  console.log(`Status: ${result.status}`);
  console.log(`Response:`, JSON.stringify(result.data, null, 2));
  
  if (result.ok && result.data.reply === 'pong') {
    console.log(`✅ Ping endpoint working correctly`);
  } else {
    console.log('❌ Ping endpoint not working');
  }
}

async function testMonitoringEndpoint() {
  console.log('\n📊 Testing Monitoring Endpoint...');
  const result = await makeRequest(`${BASE_URL}/api/monitoring`);
  
  console.log(`Status: ${result.status}`);
  
  // Only show summary of monitoring data (can be very large)
  if (result.ok && result.data) {
    console.log(`✅ Monitoring endpoint accessible`);
    console.log(`   Overall Status: ${result.data.status}`);
    console.log(`   Total Requests: ${result.data.summary?.totalRequests || 0}`);
    console.log(`   Error Rate: ${result.data.summary?.overallErrorRate || 0}%`);
    console.log(`   Active Alerts: ${result.data.summary?.activeAlerts || 0}`);
    console.log(`   Health Checks: ${result.data.healthChecks?.length || 0} services`);
  } else {
    console.log('❌ Monitoring endpoint not accessible');
    console.log(`Response:`, JSON.stringify(result.data, null, 2));
  }
}

async function runDemo() {
  console.log('🚀 API Error Handling Demo');
  console.log('=' .repeat(50));
  console.log(`Testing against: ${BASE_URL}`);
  
  try {
    await testHealthEndpoint();
    await testLyraPingEndpoint();
    await testLyraValidRequest();
    await testLyraInvalidRequest();
    await testLyraMethodNotAllowed();
    await testMonitoringEndpoint();
    
    console.log('\n✨ Demo completed!');
    console.log('\nTo run this demo:');
    console.log('1. Start your Next.js server: npm run dev');
    console.log('2. Run this script: node demo-api-error-handling.js');
    console.log('3. Optionally set BASE_URL: BASE_URL=http://your-server node demo-api-error-handling.js');
    
  } catch (error) {
    console.error('❌ Demo failed:', error.message);
  }
}

// Handle both Node.js and import usage
if (typeof require !== 'undefined' && require.main === module) {
  runDemo();
}

module.exports = { runDemo };