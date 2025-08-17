# Security Implementation Documentation

## Overview

This document describes the comprehensive security enhancements implemented in the AI Agents API server (`apps/companion_api`).

## Security Features

### 1. Environment Configuration (`src/config/env.ts`)

**Purpose**: Validates required environment variables and provides environment-specific configurations.

**Features**:
- Validates required environment variables at startup
- Environment-specific configurations (development, production, test)
- Type-safe configuration interface

**Required Environment Variables**:
```bash
NODE_ENV=development|production|test
OPENAI_API_KEY=your-openai-api-key
JWT_SECRET=your-jwt-secret-key
JWT_REFRESH_SECRET=your-jwt-refresh-secret-key
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 2. Rate Limiting (`src/middleware/security.ts`)

**Purpose**: Protects against abuse and DDoS attacks.

**Configuration**:
- **Development**: 200 requests per 15 minutes
- **Production**: 100 requests per 15 minutes  
- **Test**: 1000 requests per 15 minutes

**Implementation**:
- Uses `express-rate-limit` middleware
- Per-IP tracking with token bucket algorithm
- Returns 429 status with retry-after information

### 3. CORS Protection (`src/middleware/security.ts`)

**Purpose**: Prevents unauthorized cross-origin requests.

**Features**:
- Strict origin validation against allowed origins
- Supports credentials for authenticated requests
- Proper preflight handling

**Configuration**:
- Origins configured via `ALLOWED_ORIGINS` environment variable
- Supports multiple origins (comma-separated)
- Rejects requests from unauthorized origins

### 4. Security Headers (`src/middleware/security.ts`)

**Purpose**: Protects against common web vulnerabilities.

**Headers Applied**:
- **Content Security Policy**: Restricts resource loading
- **X-Frame-Options**: Prevents clickjacking (DENY)
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **Referrer-Policy**: Controls referrer information
- **Permissions-Policy**: Restricts browser features

### 5. JWT Authentication (`src/middleware/auth.ts`)

**Purpose**: Secure stateless authentication with token refresh capability.

**Features**:
- **Access Tokens**: Short-lived (15 minutes) for API access
- **Refresh Tokens**: Long-lived (7 days) for token renewal
- **Token Validation**: Automatic signature verification
- **Type Safety**: Strongly typed JWT payloads

**Endpoints**:
- `POST /auth/login` - Authenticate and get tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout (client-side token removal)
- `GET /auth/me` - Get current user profile (requires auth)

**Usage**:
```typescript
// Required authentication
app.use('/protected', jwtAuthMiddleware(config));

// Optional authentication
app.use('/optional', optionalJwtAuthMiddleware(config));
```

### 6. Error Handling (`src/middleware/error.ts`)

**Purpose**: Structured error handling with comprehensive logging.

**Features**:
- **Global Error Handler**: Catches all unhandled errors
- **Request Context**: Logs request details with errors
- **Request ID Tracking**: Unique ID for each request
- **Environment-Aware**: Different error details for dev/prod
- **Structured Logging**: JSON-formatted logs with context

**Error Response Format**:
```json
{
  "status": 400,
  "message": "Error description",
  "code": "ERROR_CODE",
  "requestId": "uuid-v4-request-id"
}
```

### 7. Request ID Tracking (`src/middleware/security.ts`)

**Purpose**: Enables request tracing and debugging.

**Features**:
- Unique UUID for each request
- Added to response headers (`X-Request-ID`)
- Included in all API responses
- Used in error logging for correlation

## Security Best Practices Implemented

### Input Validation
- JSON parsing with express body-parser
- Type checking for request parameters
- Sanitization of user inputs

### Authentication Security
- Separate secrets for access and refresh tokens
- Short-lived access tokens (15 minutes)
- Secure token generation with proper algorithms
- No sensitive data in JWT payloads

### Error Security
- No stack traces in production responses
- Sanitized error messages for external users
- Comprehensive internal logging for debugging

### Network Security
- CORS with strict origin validation
- Security headers to prevent common attacks
- Rate limiting to prevent abuse

## Configuration Examples

### Development Environment
```bash
NODE_ENV=development
JWT_SECRET=dev-secret-change-in-production
JWT_REFRESH_SECRET=dev-refresh-secret-change-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Production Environment
```bash
NODE_ENV=production
JWT_SECRET=super-secure-production-secret-32-chars-min
JWT_REFRESH_SECRET=super-secure-refresh-secret-32-chars-min
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## Testing

The implementation includes comprehensive testing:

1. **Health Check**: Basic server functionality
2. **Rate Limiting**: Multiple request handling
3. **CORS**: Origin validation
4. **Authentication**: Login, token usage, protected endpoints
5. **Error Handling**: 404 and error responses

Run tests with:
```bash
npm run dev  # Start server
node test-security.mjs  # Run security tests
```

## Monitoring and Alerts

### Log Monitoring
- All errors logged with full context
- Request patterns tracked
- Authentication events logged

### Security Events
- Failed authentication attempts
- Rate limit violations
- CORS violations
- Malformed requests

## Security Considerations

### Secrets Management
- Never commit secrets to version control
- Use environment variables for all sensitive data
- Rotate secrets regularly in production

### Token Security
- Access tokens should be stored securely (httpOnly cookies recommended)
- Refresh tokens should be stored even more securely
- Implement token blacklisting for enhanced security

### Network Security
- Use HTTPS in production
- Consider additional rate limiting at load balancer level
- Monitor for unusual traffic patterns

### Updates and Maintenance
- Keep dependencies updated
- Monitor security advisories
- Regular security audits

## Future Enhancements

1. **Token Blacklisting**: Redis-based token revocation
2. **Advanced Rate Limiting**: Per-user and per-endpoint limits
3. **Audit Logging**: Detailed security event logging
4. **Two-Factor Authentication**: Additional security layer
5. **API Key Management**: Alternative authentication method
6. **Intrusion Detection**: Automated threat detection