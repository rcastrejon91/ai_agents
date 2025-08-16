export function allowedRoles(): string[] {
  return (process.env.LEGAL_ALLOWED_ROLES || "staff,firm_user")
    .split(",")
    .map((r) => r.trim());
}

export function isAllowed(role: string): boolean {
  return allowedRoles().includes(role);
}

export const banner = "⚠️ Not legal advice. For attorney review.";

export function requireJurisdiction(j?: string): {
  juris: string;
  note: string;
} {
  const juris = j || process.env.LEGAL_DEFAULT_JURISDICTION || "US";
  return { juris, note: `Jurisdiction: ${juris}` };
}

export function shouldRefuse(intent: string, role: string): boolean {
  if (!isAllowed(role)) return true;
  return intent !== "research";
}

export function redact(str: string): string {
  return str
    .replace(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g, "[redacted]")
    .replace(/sk-[A-Za-z0-9]{10,}/g, "[redacted]")
    .replace(/tvly-[A-Za-z0-9]{10,}/g, "[redacted]");
}
