export async function safeFetchJSON(
  url: string,
  headers: Record<string, string> = {},
  ms = 12000,
) {
  const ctrl = new AbortController();
  const to = setTimeout(() => ctrl.abort(), ms);
  try {
    const r = await fetch(url, { headers, signal: ctrl.signal });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return await r.json();
  } finally {
    clearTimeout(to);
  }
}

export function riskGate(text: string): { allowed: boolean; reason?: string } {
  const blocked = [
    /exploit|malware|weapon|biohazard|overthrow|dox/i,
    /self[-\s]?harm|suicide|anorexia/i,
  ];
  if (process.env.RESEARCH_SAFE_MODE === "1") {
    if (blocked.some((rx) => rx.test(text)))
      return { allowed: false, reason: "violates safety policy" };
  }
  return { allowed: true };
}

/**
 * UTC timestamp utilities for consistent date/time handling across the application
 */

export function ts() {
  return new Date().toISOString();
}

/**
 * Get current UTC timestamp in YYYY-MM-DD HH:MM:SS format
 */
export function utcTimestamp(): string {
  const now = new Date();
  return now.toISOString().replace('T', ' ').substring(0, 19);
}

/**
 * Get current UTC date in YYYY-MM-DD format
 */
export function utcDate(): string {
  return new Date().toISOString().substring(0, 10);
}

/**
 * Format a date object to UTC timestamp string (YYYY-MM-DD HH:MM:SS)
 */
export function formatUtcTimestamp(date: Date): string {
  return date.toISOString().replace('T', ' ').substring(0, 19);
}

/**
 * Validate if a date string is in proper format and represents a valid date
 */
export function validateDateTimeInput(dateTimeStr: string): { valid: boolean; error?: string } {
  if (!dateTimeStr || typeof dateTimeStr !== 'string') {
    return { valid: false, error: 'Date/time string is required' };
  }

  // Check for YYYY-MM-DD HH:MM:SS format
  const timestampRegex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/;
  // Check for YYYY-MM-DD format
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  // Check for ISO string format
  const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$/;

  if (!timestampRegex.test(dateTimeStr) && !dateRegex.test(dateTimeStr) && !isoRegex.test(dateTimeStr)) {
    return { valid: false, error: 'Invalid format. Expected YYYY-MM-DD HH:MM:SS, YYYY-MM-DD, or ISO format' };
  }

  // Validate the actual date
  const date = new Date(dateTimeStr);
  if (isNaN(date.getTime())) {
    return { valid: false, error: 'Invalid date/time value' };
  }

  return { valid: true };
}
