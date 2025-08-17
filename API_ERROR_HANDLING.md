# API Error Handling System

This document describes the comprehensive API error handling improvements implemented for the Lyra AI system.

## Overview

The enhanced error handling system provides:
- Standardized error responses
- Comprehensive request validation  
- Timeout management with retry logic
- Detailed monitoring and diagnostics
- Health checks and status reporting
- Rate limiting and security features

## New Endpoints

### `/api/health`
Enhanced health check endpoint that monitors service availability.

**Method:** GET  
**Response:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "services": {
    "openai": {
      "status": "healthy|degraded|unhealthy",
      "latency": 150,
      "error": "Optional error message"
    }
  },
  "version": "1.0.0"
}
```

### `/api/monitoring`
Comprehensive monitoring dashboard with metrics and alerts.

**Method:** GET  
**Authentication:** Optional Bearer token via `MONITORING_API_KEY` env var  
**Response:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "requestId": "req_1234567890_abc123",
  "metrics": {
    "POST:/api/lyra": {
      "endpoint": "/api/lyra",
      "totalRequests": 1000,
      "successfulRequests": 950,
      "failedRequests": 50,
      "averageResponseTime": 1200,
      "p95ResponseTime": 2500,
      "errorRate": 5.0,
      "uptime": 86400
    }
  },
  "healthChecks": [...],
  "alerts": [...],
  "summary": {
    "totalRequests": 1000,
    "overallErrorRate": 5.0,
    "averageResponseTime": 1200,
    "activeAlerts": 0
  }
}
```

### `/api/lyra` (Enhanced)
The main Lyra API endpoint with comprehensive error handling.

**Method:** POST  
**Request:**
```json
{
  "message": "Your message here",
  "history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ],
  "model": "gpt-4o-mini",
  "temperature": 0.7
}
```

**Success Response:**
```json
{
  "reply": "AI response",
  "model": "gpt-4o-mini", 
  "tools": ["Chat"],
  "timestamp": "2024-01-01T00:00:00.000Z",
  "requestId": "req_1234567890_abc123"
}
```

**Error Response:**
```json
{
  "error": "API Error",
  "code": "VALIDATION_ERROR|UPSTREAM_ERROR|TIMEOUT_ERROR|RATE_LIMIT_ERROR",
  "message": "Detailed error message",
  "details": {},
  "timestamp": "2024-01-01T00:00:00.000Z",
  "requestId": "req_1234567890_abc123"
}
```

## Error Types

### ValidationError (400)
- Empty or missing message
- Message too long (>10,000 characters) 
- Invalid history format
- History too long (>50 messages)
- Invalid role in history messages

### UpstreamError (502)
- OpenAI API failures
- Invalid response format
- Empty responses from OpenAI

### TimeoutError (504) 
- Request timeouts (>45s for OpenAI calls)
- Connection timeouts

### RateLimitError (429)
- Too many requests (>30/minute by default)
- OpenAI rate limits

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key

# Optional monitoring
MONITORING_API_KEY=your-secret-monitoring-key
GUARDIAN_INGEST_TOKEN=your-guardian-token
NEXT_PUBLIC_BASE_URL=https://your-domain.com

# Optional security
SECURITY_WEBHOOK_URL=https://your-alerts-webhook.com
```

### Timeout Configuration

```typescript
const TIMEOUT_CONFIG = {
  DEFAULT: 30000,    // 30 seconds default
  OPENAI: 45000,     // 45 seconds for OpenAI
  RETRY_DELAY: 1000, // 1 second base delay
  MAX_RETRIES: 3,    // Maximum retry attempts
};
```

### Alert Thresholds

```typescript
const ALERT_THRESHOLDS = {
  ERROR_RATE: 5,      // 5% error rate threshold
  RESPONSE_TIME: 5000, // 5 second response time
  AVAILABILITY: 99,    // 99% availability threshold
};
```

## Features

### Request Validation
- Input sanitization and validation
- Length limits and format checking
- Security pattern detection
- Rate limiting by IP address

### Retry Logic
- Exponential backoff for failed requests
- Configurable retry attempts (default: 3)
- Smart retry logic (no retry on 4xx except 429)
- Timeout handling with proper error classification

### Monitoring & Metrics
- Real-time request/response metrics
- Performance tracking (avg, P95 response times)
- Error rate monitoring
- Uptime tracking
- Alert system for critical issues

### Security Features
- Rate limiting (30 requests/minute default)
- Secret scrubbing in responses
- Input validation against malicious patterns
- Request logging for security events

### Graceful Fallbacks
- Demo mode when OpenAI API key not configured
- Health ping endpoint for quick checks
- Service degradation handling
- Connection error recovery

## Usage Examples

### Basic Request
```javascript
const response = await fetch('/api/lyra', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello, how can you help me today?'
  })
});

const data = await response.json();
if (response.ok) {
  console.log('Reply:', data.reply);
} else {
  console.error('Error:', data.code, data.message);
}
```

### Health Check
```javascript
const health = await fetch('/api/health');
const status = await health.json();
console.log('Service Status:', status.status);
console.log('OpenAI Status:', status.services.openai.status);
```

### Monitoring Data
```javascript
const monitoring = await fetch('/api/monitoring', {
  headers: { 
    'Authorization': 'Bearer your-monitoring-key' 
  }
});
const metrics = await monitoring.json();
console.log('Total Requests:', metrics.summary.totalRequests);
console.log('Error Rate:', metrics.summary.overallErrorRate + '%');
```

## Testing

### Running the Demo
```bash
# Start the development server
npm run dev

# Run the demo script
node demo-api-error-handling.js

# Or with custom URL
BASE_URL=http://localhost:3000 node demo-api-error-handling.js
```

### Test Suite
```bash
# Run the error handling tests
npm test tests/api-error-handling.test.ts
```

The demo script tests:
- Health endpoint functionality
- Valid request processing
- Validation error handling
- Method validation
- Ping/health check
- Monitoring endpoint access

## Python Flask Implementation

The Python Flask implementation (`lyra_app/`) includes equivalent error handling:

```python
from error_handling import (
    error_handler,
    validate_lyra_request,
    ValidationError,
    UpstreamError
)

@app.route("/api/lyra", methods=["POST"])
@error_handler
def lyra():
    # Validation and error handling automatically applied
    validated_data = validate_lyra_request(request.get_json())
    # ... rest of implementation
```

## Monitoring Dashboard

The monitoring system provides:
- Real-time metrics collection
- Performance trend analysis  
- Error rate monitoring
- Service health tracking
- Automated alerting
- Request tracing

Access the monitoring data via `/api/monitoring` endpoint for integration with external monitoring tools like Grafana, DataDog, or custom dashboards.

## Development

### Adding New Error Types
```typescript
// In lib/api-errors.ts
export class CustomError extends LyraAPIError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, "CUSTOM_ERROR", 400, details);
  }
}
```

### Adding Monitoring Metrics
```typescript
// Record custom metrics
metricsCollector.recordRequest(
  endpoint,
  method, 
  statusCode,
  duration,
  errorCode,
  errorMessage,
  requestId
);
```

This system provides production-ready error handling with comprehensive monitoring and diagnostics capabilities.