/**
 * Simple test for UTC datetime utilities
 */

import { utcTimestamp, utcDate, formatUtcTimestamp, validateDateTimeInput } from '../app/lib/research/utils';

describe('UTC DateTime Utilities', () => {
  test('utcTimestamp returns YYYY-MM-DD HH:MM:SS format', () => {
    const timestamp = utcTimestamp();
    expect(timestamp).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/);
  });

  test('utcDate returns YYYY-MM-DD format', () => {
    const date = utcDate();
    expect(date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  test('formatUtcTimestamp formats date objects correctly', () => {
    const testDate = new Date('2024-01-15T14:30:45.123Z');
    const formatted = formatUtcTimestamp(testDate);
    expect(formatted).toBe('2024-01-15 14:30:45');
  });

  test('validateDateTimeInput validates different formats', () => {
    // Valid formats
    expect(validateDateTimeInput('2024-01-15 14:30:45')).toEqual({ valid: true });
    expect(validateDateTimeInput('2024-01-15')).toEqual({ valid: true });
    expect(validateDateTimeInput('2024-01-15T14:30:45Z')).toEqual({ valid: true });
    
    // Invalid formats
    expect(validateDateTimeInput('invalid')).toEqual({ 
      valid: false, 
      error: 'Invalid format. Expected YYYY-MM-DD HH:MM:SS, YYYY-MM-DD, or ISO format' 
    });
    expect(validateDateTimeInput('')).toEqual({ 
      valid: false, 
      error: 'Date/time string is required' 
    });
  });
});