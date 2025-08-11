export function allowedRoles(): Set<string> {
  const env = process.env.LEGAL_ALLOWED_ROLES;
  const roles = env ? env.split(',').map(r => r.trim()) : ['staff','firm_user'];
  return new Set(roles.filter(Boolean));
}

export function isAllowed(role: string): boolean {
  return allowedRoles().has(role);
}

export const banner = "\u26A0\uFE0F Not legal advice. For attorney review.";

export function requireJurisdiction(inputJurisdiction?: string): { juris: string, note: string } {
  const def = process.env.LEGAL_DEFAULT_JURISDICTION || 'US';
  if (inputJurisdiction && inputJurisdiction.trim()) {
    return { juris: inputJurisdiction, note: `Assuming ${inputJurisdiction}` };
  }
  return { juris: def, note: `Assuming ${def} (no jurisdiction provided)` };
}

export function redact(text: string): string {
  if (!text) return '';
  return text
    .replace(/sk-[a-zA-Z0-9]{16,}/g, '[redacted]')
    .replace(/tvly-[a-zA-Z0-9]{16,}/g, '[redacted]')
    .replace(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g, '[redacted]');
}

export function shouldRefuse(intent: string, role: string): boolean {
  if (!isAllowed(role)) return true;
  const lower = intent?.toLowerCase() || '';
  if (role === 'guest') return true;
  if (lower.includes('public') || lower.includes('advice')) return true;
  return false;
}
