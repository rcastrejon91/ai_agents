# Security and Environment Configuration

This document describes the enhanced security measures and environment configuration for the AI Agents repository, now fully deployment-ready.

## Overview

The implementation includes comprehensive security measures, enhanced environment validation, CORS configuration, backend URL handling, and deployment configurations that meet production-ready standards with proper environment-specific settings.

## Key Improvements Made

### 1. Enhanced Environment Configuration
- **Backend URL Management**: Automatic configuration based on environment (development/staging/production)
- **Production HTTPS Validation**: Warns about insecure URLs in production environments
- **Environment-Specific Defaults**: Smart defaults that change based on NODE_ENV
- **URL Validation**: Validates all URL environment variables for proper format

### 2. Security Enhancements
- **Environment-Specific Security Levels**: Low/Medium/High security based on environment
- **Production Security Warnings**: Alerts for insecure configurations in production
- **WebAuthn Configuration Validation**: Ensures proper HTTPS setup for authentication
- **Enhanced Rate Limiting**: Environment-specific rate limiting (1000/200/100 requests per 15min)

### 3. Deployment Readiness
- **Railway Configuration**: Enhanced with proper environment variable mapping
- **Health Check Improvements**: Better health check endpoints for deployment platforms
- **Environment Variable Documentation**: Comprehensive .env.example with production guidance
- **Build Compatibility**: Fixed all TypeScript and dependency issues

## Features Implemented

### 1. Environment Configuration

#### Enhanced .env.example

- Comprehensive documentation with clear sections
- All required and optional environment variables
- Security-focused configuration options
- Production deployment guidelines

#### Environment Validation

- **Location**: `apps/companion_api/src/config/env-validation.ts`
- **Features**:
  - Required variable validation
  - API key format validation (must start with `sk-`)
  - Port range validation (1-65535)
  - Environment type validation (development/staging/production)
  - Graceful error handling with clear error messages

### 2. CORS Configuration

#### Environment-Specific Settings

- **Development**: Allows all localhost origins for easy development
- **Staging**: Configurable origins from ALLOWED_ORIGINS environment variable
- **Production**: Strict origin validation from ALLOWED_ORIGINS

#### Features

- Preflight request handling
- Credential support
- Custom headers configuration
- Exposed headers for client access
- 24-hour cache for preflight responses

### 3. Security Measures

#### Rate Limiting

- **Development**: 1000 requests per 15 minutes (lenient for development)
- **Staging**: 200 requests per 15 minutes
- **Production**: 100 requests per 15 minutes (strict)
- IP-based tracking with automatic reset

#### Security Headers

- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `X-XSS-Protection: 1; mode=block` - XSS protection
- `Referrer-Policy: strict-origin-when-cross-origin` - Controls referrer information
- `Permissions-Policy` - Restricts access to sensitive APIs

#### Input Validation

- Message length validation (max 1000 characters)
- Empty message detection
- Type validation (must be string)
- Request body size limits (1MB)

### 4. Health Check Endpoints

#### `/health` endpoint

```json
{
  "ok": true,
  "timestamp": "2025-08-17T23:17:22.005Z",
  "environment": "development",
  "version": "1.0.0",
  "services": {
    "openai": true,
    "database": true
  }
}
```

#### `/ready` endpoint

- Readiness check for deployment platforms
- Can be extended with database connectivity checks

### 5. Railway Deployment Configuration

#### Application-Specific Configurations

- **companion_api**: `apps/companion_api/railway.json`
- **companion_web**: `apps/companion_web/railway.json`

#### Features

- Node.js optimized build configuration
- Health check integration
- Proper environment variable handling
- Restart policies for reliability

## Usage

### Development Setup

1. Copy environment file:

```bash
cp .env.example .env
```

2. Fill in required variables:

```bash
OPENAI_API_KEY=sk-your-api-key
NODE_ENV=development
PORT=8787
ALLOWED_ORIGINS=http://localhost:3000
```

3. Start the API:

```bash
cd apps/companion_api
npm install
npm run dev
```

### Production Deployment

1. Set environment variables in deployment platform:

```bash
OPENAI_API_KEY=sk-prod-key
NODE_ENV=production
ALLOWED_ORIGINS=https://yourdomain.com
PORT=8787
```

2. Deploy using Railway or your preferred platform

### Testing Security Features

Run the comprehensive test script:

```bash
./test_security_features.sh
```

## Environment Variables Reference

### Required Variables

- `OPENAI_API_KEY`: OpenAI API key (must start with `sk-`)

### Optional Variables

- `NODE_ENV`: Environment type (development/staging/production)
- `PORT`: Server port (default: 8787)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins
- `STRIPE_SECRET_KEY`: Stripe secret key for payments
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret

### Security Variables

- `ORIGIN`: WebAuthn origin for authentication
- `RP_ID`: WebAuthn relying party ID

## Validation Examples

### Valid Configuration

```bash
✅ Environment validation passed
🚀 API server running on port 8787
📝 Environment: development
🔒 CORS origins: true
⏱️  Rate limit: 1000 requests per 15 minutes
```

### Invalid Configuration

```bash
Environment validation failed:
  ❌ OPENAI_API_KEY is required
  ❌ PORT must be a valid port number (1-65535)
```

## Security Testing

### CORS Testing

```bash
# Test allowed origin
curl -H "Origin: http://localhost:3000" http://localhost:8787/health

# Test unauthorized origin (in production)
curl -H "Origin: http://malicious-site.com" http://localhost:8787/health
```

### Input Validation Testing

```bash
# Test empty message
curl -X POST http://localhost:8787/chat \
  -H "Content-Type: application/json" \
  -d '{}'

# Test too long message
curl -X POST http://localhost:8787/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"'$(python -c 'print("a" * 1001)')'"}''
```

### Rate Limiting Testing

```bash
# Make multiple requests to test rate limiting
for i in {1..150}; do
  curl -s http://localhost:8787/health > /dev/null
  echo "Request $i"
done
```

## Monitoring and Logging

The implementation includes comprehensive logging for:

- Environment validation results
- CORS policy violations
- Rate limit violations
- Input validation failures
- Security header application

All security events are logged with appropriate context for debugging and monitoring.
