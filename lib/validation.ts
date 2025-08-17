/**
 * Request Validation Middleware
 * Provides comprehensive input validation and sanitization for API routes
 */

import { NextApiRequest, NextApiResponse } from 'next';
import { InputSanitizer, ValidationSchemas } from '../config/security';
import { ValidationError, withErrorHandler } from './errors';

/**
 * Validation rules for different endpoint types
 */
export interface ValidationRule {
  field: string;
  required?: boolean;
  type?: 'string' | 'number' | 'email' | 'url' | 'array' | 'object';
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  pattern?: RegExp;
  customValidator?: (value: any) => boolean;
  sanitizer?: (value: any) => any;
}

export interface ValidationSchema {
  body?: ValidationRule[];
  query?: ValidationRule[];
  headers?: ValidationRule[];
}

/**
 * Validate and sanitize a value according to rules
 */
function validateAndSanitizeValue(value: any, rule: ValidationRule): any {
  const { field, required, type, minLength, maxLength, min, max, pattern, customValidator, sanitizer } = rule;

  // Check if required field is present
  if (required && (value === undefined || value === null || value === '')) {
    throw new ValidationError(`Field '${field}' is required`);
  }

  // If field is not present and not required, return undefined
  if (value === undefined || value === null) {
    return undefined;
  }

  // Apply custom sanitizer first
  let sanitizedValue = sanitizer ? sanitizer(value) : value;

  // Type-specific validation and sanitization
  switch (type) {
    case 'string':
      sanitizedValue = InputSanitizer.sanitizeText(sanitizedValue);
      if (minLength !== undefined && sanitizedValue.length < minLength) {
        throw new ValidationError(`Field '${field}' must be at least ${minLength} characters long`);
      }
      if (maxLength !== undefined && sanitizedValue.length > maxLength) {
        throw new ValidationError(`Field '${field}' must be no more than ${maxLength} characters long`);
      }
      break;

    case 'number':
      sanitizedValue = InputSanitizer.sanitizeNumber(sanitizedValue, { min, max });
      if (sanitizedValue === null) {
        throw new ValidationError(`Field '${field}' must be a valid number`);
      }
      break;

    case 'email':
      sanitizedValue = InputSanitizer.sanitizeEmail(sanitizedValue);
      if (!sanitizedValue) {
        throw new ValidationError(`Field '${field}' must be a valid email address`);
      }
      break;

    case 'url':
      sanitizedValue = InputSanitizer.sanitizeUrl(sanitizedValue);
      if (!sanitizedValue) {
        throw new ValidationError(`Field '${field}' must be a valid URL`);
      }
      break;

    case 'array':
      if (!Array.isArray(sanitizedValue)) {
        throw new ValidationError(`Field '${field}' must be an array`);
      }
      sanitizedValue = InputSanitizer.sanitizeArray(sanitizedValue);
      break;

    case 'object':
      if (typeof sanitizedValue !== 'object' || Array.isArray(sanitizedValue)) {
        throw new ValidationError(`Field '${field}' must be an object`);
      }
      sanitizedValue = InputSanitizer.sanitizeObject(sanitizedValue);
      break;
  }

  // Pattern validation
  if (pattern && !pattern.test(String(sanitizedValue))) {
    throw new ValidationError(`Field '${field}' format is invalid`);
  }

  // Custom validation
  if (customValidator && !customValidator(sanitizedValue)) {
    throw new ValidationError(`Field '${field}' failed custom validation`);
  }

  return sanitizedValue;
}

/**
 * Validate and sanitize request data
 */
function validateRequest(req: NextApiRequest, schema: ValidationSchema) {
  const result: { body?: any; query?: any; headers?: any } = {};

  // Validate body
  if (schema.body) {
    result.body = {};
    for (const rule of schema.body) {
      result.body[rule.field] = validateAndSanitizeValue(req.body?.[rule.field], rule);
    }
  }

  // Validate query parameters
  if (schema.query) {
    result.query = {};
    for (const rule of schema.query) {
      result.query[rule.field] = validateAndSanitizeValue(req.query?.[rule.field], rule);
    }
  }

  // Validate headers
  if (schema.headers) {
    result.headers = {};
    for (const rule of schema.headers) {
      result.headers[rule.field] = validateAndSanitizeValue(req.headers?.[rule.field], rule);
    }
  }

  return result;
}

/**
 * Middleware to validate requests
 */
export function withValidation(schema: ValidationSchema) {
  return function (handler: (req: NextApiRequest, res: NextApiResponse, validated: any) => Promise<void>) {
    return withErrorHandler(async (req: NextApiRequest, res: NextApiResponse) => {
      const validated = validateRequest(req, schema);
      return handler(req, res, validated);
    });
  };
}

/**
 * Common validation schemas
 */
export const CommonSchemas = {
  // Chat message validation
  chatMessage: {
    body: [
      { field: 'message', required: true, type: 'string' as const, minLength: 1, maxLength: 5000 },
      { field: 'sessionId', required: false, type: 'string' as const, pattern: /^[a-zA-Z0-9-_]{1,50}$/ }
    ]
  },

  // User authentication
  userLogin: {
    body: [
      { field: 'email', required: true, type: 'email' as const },
      { field: 'password', required: true, type: 'string' as const, minLength: 8 }
    ]
  },

  // API pagination
  pagination: {
    query: [
      { field: 'limit', required: false, type: 'number' as const, min: 1, max: 100 },
      { field: 'offset', required: false, type: 'number' as const, min: 0 }
    ]
  },

  // Admin authentication
  adminAuth: {
    headers: [
      { field: 'x-admin-key', required: true, type: 'string' as const }
    ]
  },

  // Medical query
  medicalQuery: {
    body: [
      { field: 'query', required: true, type: 'string' as const, minLength: 1, maxLength: 1000 },
      { field: 'jurisdiction', required: false, type: 'string' as const, pattern: /^[A-Z]{2}(-[A-Z]{2,3})?$/ }
    ]
  },

  // Legal research
  legalResearch: {
    body: [
      { field: 'query', required: true, type: 'string' as const, minLength: 1, maxLength: 2000 },
      { field: 'jurisdiction', required: false, type: 'string' as const },
      { field: 'intent', required: false, type: 'string' as const }
    ]
  }
};

/**
 * Method validation middleware
 */
export function withMethodValidation(allowedMethods: string[]) {
  return function (handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void>) {
    return withErrorHandler(async (req: NextApiRequest, res: NextApiResponse) => {
      if (!allowedMethods.includes(req.method || '')) {
        res.setHeader('Allow', allowedMethods.join(', '));
        throw new ValidationError(`Method ${req.method} not allowed`, { allowedMethods });
      }
      return handler(req, res);
    });
  };
}

/**
 * Content-Type validation middleware
 */
export function withContentTypeValidation(allowedTypes: string[] = ['application/json']) {
  return function (handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void>) {
    return withErrorHandler(async (req: NextApiRequest, res: NextApiResponse) => {
      const contentType = req.headers['content-type'];
      if (req.method !== 'GET' && req.method !== 'OPTIONS') {
        if (!contentType || !allowedTypes.some(type => contentType.includes(type))) {
          throw new ValidationError(`Content-Type must be one of: ${allowedTypes.join(', ')}`);
        }
      }
      return handler(req, res);
    });
  };
}