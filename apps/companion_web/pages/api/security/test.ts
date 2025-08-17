import type { NextApiRequest, NextApiResponse } from 'next';
import { SecureStorage } from '../../../utils/secure-storage';
import { logger } from '../../../utils/logger';
import { AuditTrail, AuditEvent } from '../../../utils/audit';
import { SessionManager } from '../../../utils/session';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { action, testData, userId = 'test-user' } = req.body;

    switch (action) {
      case 'encrypt': {
        const storage = SecureStorage.getInstance();
        const encrypted = await storage.encrypt(testData);
        
        logger.info('Data encryption test', {
          action: 'encrypt',
          userId,
          success: true
        });

        return res.status(200).json({
          success: true,
          encrypted,
          message: 'Data encrypted successfully'
        });
      }

      case 'decrypt': {
        const storage = SecureStorage.getInstance();
        const decrypted = await storage.decrypt(testData);
        
        logger.info('Data decryption test', {
          action: 'decrypt',
          userId,
          success: true
        });

        return res.status(200).json({
          success: true,
          decrypted,
          message: 'Data decrypted successfully'
        });
      }

      case 'create_session': {
        const sessionId = await SessionManager.createSession(userId, testData || {});
        
        const auditEvent: AuditEvent = {
          action: 'session_created',
          userId,
          resource: 'session',
          details: { sessionId },
          timestamp: new Date()
        };
        
        await AuditTrail.log(auditEvent);

        return res.status(200).json({
          success: true,
          sessionId,
          message: 'Session created successfully'
        });
      }

      case 'get_session': {
        const session = await SessionManager.getSession(testData.sessionId);
        
        logger.info('Session retrieval test', {
          action: 'get_session',
          userId,
          sessionFound: !!session
        });

        return res.status(200).json({
          success: true,
          session,
          message: session ? 'Session found' : 'Session not found'
        });
      }

      case 'log_test': {
        // Test sensitive data sanitization
        logger.info('Logging test with sensitive data', {
          data: {
            username: 'testuser',
            password: 'secret123', // Should be redacted
            token: 'abc123', // Should be redacted
            publicInfo: 'this is safe'
          }
        });

        return res.status(200).json({
          success: true,
          message: 'Log test completed - check logs for sanitization'
        });
      }

      default:
        return res.status(400).json({
          error: 'Invalid action',
          availableActions: ['encrypt', 'decrypt', 'create_session', 'get_session', 'log_test']
        });
    }
  } catch (error) {
    logger.error('Security test API error', {
      error: error instanceof Error ? error.message : 'Unknown error',
      action: req.body?.action,
      userId: req.body?.userId || 'unknown'
    });

    return res.status(500).json({
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}