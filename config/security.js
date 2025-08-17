/**
 * Security Utilities
 * Provides input sanitization, validation, and security helpers
 */

const validator = require('validator');
const DOMPurify = require('isomorphic-dompurify');

/**
 * Input sanitization functions
 */
class InputSanitizer {
  /**
   * Sanitize HTML content
   */
  static sanitizeHtml(input) {
    if (typeof input !== 'string') return '';
    return DOMPurify.sanitize(input, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
      ALLOWED_ATTR: ['href']
    });
  }

  /**
   * Sanitize text input (remove HTML, trim whitespace)
   */
  static sanitizeText(input) {
    if (typeof input !== 'string') return '';
    return validator.escape(input.trim());
  }

  /**
   * Sanitize email input
   */
  static sanitizeEmail(input) {
    if (typeof input !== 'string') return '';
    const email = input.trim().toLowerCase();
    return validator.isEmail(email) ? email : '';
  }

  /**
   * Sanitize URL input
   */
  static sanitizeUrl(input) {
    if (typeof input !== 'string') return '';
    const url = input.trim();
    return validator.isURL(url, {
      protocols: ['http', 'https'],
      require_protocol: true
    }) ? url : '';
  }

  /**
   * Sanitize numeric input
   */
  static sanitizeNumber(input, options = {}) {
    const { min, max, isInteger = false } = options;
    const num = isInteger ? parseInt(input, 10) : parseFloat(input);
    
    if (isNaN(num)) return null;
    if (min !== undefined && num < min) return null;
    if (max !== undefined && num > max) return null;
    
    return num;
  }

  /**
   * Sanitize array input
   */
  static sanitizeArray(input, sanitizeItem = this.sanitizeText) {
    if (!Array.isArray(input)) return [];
    return input.map(item => sanitizeItem(item)).filter(item => item !== '');
  }

  /**
   * Deep sanitize object
   */
  static sanitizeObject(obj, schema = {}) {
    if (typeof obj !== 'object' || obj === null) return {};
    
    const sanitized = {};
    for (const [key, value] of Object.entries(obj)) {
      const sanitizer = schema[key] || this.sanitizeText;
      if (Array.isArray(value)) {
        sanitized[key] = this.sanitizeArray(value, sanitizer);
      } else if (typeof value === 'object') {
        sanitized[key] = this.sanitizeObject(value, schema[key] || {});
      } else {
        sanitized[key] = sanitizer(value);
      }
    }
    
    return sanitized;
  }
}

/**
 * Request validation schemas
 */
const ValidationSchemas = {
  user: {
    email: (value) => InputSanitizer.sanitizeEmail(value),
    name: (value) => InputSanitizer.sanitizeText(value),
    role: (value) => {
      const sanitized = InputSanitizer.sanitizeText(value);
      const allowedRoles = ['user', 'admin', 'moderator'];
      return allowedRoles.includes(sanitized) ? sanitized : 'user';
    }
  },
  
  chat: {
    message: (value) => InputSanitizer.sanitizeText(value),
    sessionId: (value) => {
      const sanitized = InputSanitizer.sanitizeText(value);
      return /^[a-zA-Z0-9-_]{1,50}$/.test(sanitized) ? sanitized : '';
    }
  },
  
  api: {
    id: (value) => {
      const sanitized = InputSanitizer.sanitizeText(value);
      return /^[a-zA-Z0-9-_]{1,50}$/.test(sanitized) ? sanitized : '';
    },
    query: (value) => InputSanitizer.sanitizeText(value),
    limit: (value) => InputSanitizer.sanitizeNumber(value, { min: 1, max: 100, isInteger: true }),
    offset: (value) => InputSanitizer.sanitizeNumber(value, { min: 0, isInteger: true })
  }
};

/**
 * Security headers configuration
 */
const SecurityHeaders = {
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'Content-Security-Policy': [
    "default-src 'self'",
    "img-src 'self' data: https:",
    "script-src 'self' 'unsafe-inline'", 
    "style-src 'self' 'unsafe-inline'",
    "connect-src 'self' https:",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "object-src 'none'"
  ].join('; ')
};

/**
 * Rate limiting configurations
 */
const RateLimitConfigs = {
  api: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again later',
    standardHeaders: true,
    legacyHeaders: false
  },
  
  auth: {
    windowMs: 15 * 60 * 1000,
    max: 5, // limit login attempts
    skipSuccessfulRequests: true,
    message: 'Too many authentication attempts, please try again later'
  },
  
  heavy: {
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 10, // limit heavy operations
    message: 'Too many heavy operations, please try again later'
  }
};

module.exports = {
  InputSanitizer,
  ValidationSchemas,
  SecurityHeaders,
  RateLimitConfigs
};