# Secure Data Storage and Logging

This document describes the secure data storage and logging utilities implemented in the companion web application.

## Overview

The implementation provides five main components:

1. **SecureStorage** - AES-256-GCM encryption/decryption
2. **Logger** - Winston-based structured logging with data sanitization
3. **AuditTrail** - Audit event logging system
4. **FileSecurityManager** - Secure file operations
5. **SessionManager** - Redis-based encrypted session management

## Components

### SecureStorage

Provides secure encryption and decryption using AES-256-GCM algorithm.

```typescript
import { SecureStorage } from '../utils/secure-storage';

const storage = SecureStorage.getInstance();

// Encrypt data
const encrypted = await storage.encrypt({ sensitive: 'data', user: 'john' });

// Decrypt data
const decrypted = await storage.decrypt(encrypted);
```

### Logger

Winston-based logger with automatic sanitization of sensitive fields.

```typescript
import { logger } from '../utils/logger';

// This will automatically redact password, token, secret, key fields
logger.info('User login', {
  data: {
    username: 'john',
    password: 'secret123', // Will be redacted as [REDACTED]
    loginTime: new Date()
  }
});
```

### AuditTrail

Structured audit event logging for compliance and security monitoring.

```typescript
import { AuditTrail, AuditEvent } from '../utils/audit';

const auditEvent: AuditEvent = {
  action: 'user_login',
  userId: 'user123',
  resource: 'authentication',
  details: { ip: '192.168.1.1', userAgent: '...' },
  timestamp: new Date()
};

await AuditTrail.log(auditEvent);
```

### FileSecurityManager

Secure file and directory operations with proper permissions.

```typescript
import { FileSecurityManager } from '../utils/file-security';

// Create secure directory (permissions: 700)
await FileSecurityManager.secureDirectory('/path/to/dir');

// Write secure file (permissions: 600)
await FileSecurityManager.writeSecureFile('/path/to/file.txt', 'content');

// Secure existing file
await FileSecurityManager.secureFile('/path/to/existing/file.txt');
```

### SessionManager

Redis-based session management with encryption.

```typescript
import { SessionManager } from '../utils/session';

// Create session
const sessionId = await SessionManager.createSession('user123', { 
  role: 'admin', 
  preferences: {} 
});

// Get session
const session = await SessionManager.getSession(sessionId);

// Invalidate session
await SessionManager.invalidateSession(sessionId);

// Invalidate all user sessions
await SessionManager.invalidateAllUserSessions('user123');
```

## Environment Variables

Add these to your `.env` file:

```env
# Required: Base64-encoded 32-byte encryption key
ENCRYPTION_KEY=your-base64-encoded-key

# Optional: Redis connection URL (default: redis://localhost:6379)
REDIS_URL=redis://localhost:6379

# Optional: Log level (default: info)
LOG_LEVEL=info

# Optional: Session duration in seconds (default: 86400 = 24 hours)
SESSION_DURATION=86400
```

## Test API

A test API endpoint is available at `/api/security/test` for testing all functionality:

```bash
# Test encryption
curl -X POST /api/security/test \
  -H "Content-Type: application/json" \
  -d '{"action": "encrypt", "testData": {"secret": "hello"}}'

# Test session creation
curl -X POST /api/security/test \
  -H "Content-Type: application/json" \
  -d '{"action": "create_session", "userId": "test", "testData": {"role": "user"}}'

# Test logging with sensitive data
curl -X POST /api/security/test \
  -H "Content-Type: application/json" \
  -d '{"action": "log_test"}'
```

## Log Files

Logs are written to:
- `logs/combined.log` - All log entries
- `logs/error.log` - Error entries only

Log files automatically rotate when they reach 5MB, keeping the last 5 files.

## Security Features

- **Encryption**: AES-256-GCM with random IVs and authentication tags
- **Data Sanitization**: Automatic redaction of sensitive fields (password, token, secret, key)
- **File Permissions**: Secure directory (700) and file (600) permissions
- **Session Security**: Encrypted session data stored in Redis with TTL
- **Audit Trail**: Comprehensive event logging for security monitoring

## Dependencies

- `winston` - Logging framework
- `redis` - Redis client for session storage
- `crypto` - Node.js built-in crypto module (AES-256-GCM)

## Example Integration

Here's how to integrate the security utilities into an existing API endpoint:

```typescript
import type { NextApiRequest, NextApiResponse } from 'next';
import { logger } from '../utils/logger';
import { AuditTrail, AuditEvent } from '../utils/audit';
import { SecureStorage } from '../utils/secure-storage';
import { SessionManager } from '../utils/session';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Log all API requests with sanitization
  logger.info('API request received', {
    method: req.method,
    url: req.url,
    userAgent: req.headers['user-agent'],
    ip: req.headers['x-forwarded-for'] || req.socket.remoteAddress,
    data: req.body // Sensitive fields will be automatically sanitized
  });

  try {
    if (req.method === 'POST') {
      const { sessionId, sensitiveData } = req.body;

      // Validate session
      const session = await SessionManager.getSession(sessionId);
      if (!session) {
        logger.warn('Invalid session access attempt', { sessionId });
        return res.status(401).json({ error: 'Invalid session' });
      }

      // Encrypt sensitive data
      const storage = SecureStorage.getInstance();
      const encryptedData = await storage.encrypt(sensitiveData);

      // Log audit event
      const auditEvent: AuditEvent = {
        action: 'sensitive_data_processed',
        userId: session.userId,
        resource: 'user_data',
        details: { dataSize: JSON.stringify(sensitiveData).length },
        timestamp: new Date()
      };
      
      await AuditTrail.log(auditEvent);

      return res.status(200).json({ success: true });
    }

    return res.status(405).json({ error: 'Method not allowed' });

  } catch (error) {
    logger.error('API request failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
      method: req.method,
      url: req.url
    });

    return res.status(500).json({ error: 'Internal server error' });
  }
}
```

## Notes

- The SecureConfig class automatically generates an encryption key if none is provided (with a warning)
- All sensitive data is sanitized before logging
- Session data is encrypted before storage in Redis
- File operations use secure permissions by default
- The implementation follows singleton patterns for configuration and storage