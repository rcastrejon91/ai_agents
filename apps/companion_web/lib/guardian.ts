// Lightweight security utilities for Lyra
export type GuardEvent = {
  event: string;
  ip?: string | null;
  path?: string;
  method?: string;
  query?: string;
  user_agent?: string | null;
  referrer?: string | null;
  country?: string | null;
  city?: string | null;
  details?: Record<string, any>;
};

export const BLOCK_PATTERNS = [
  /(\%27)|(\')|(\-\-)|(\%23)|(#)/i,
  /\b(select|union|update|insert|drop|sleep|benchmark)\b/i,
  /\.\.[\/\\]/,
  /<script\b|onerror=|onload=|javascript:/i,
  /\b(\$where|mongo|db\.)/i,
];

export function looksMalicious(haystack: string) {
  if (!haystack) return false;
  if (haystack.length > 10000) return true;
  return BLOCK_PATTERNS.some((re) => re.test(haystack));
}

const _bucket = new Map<string, { t: number; tokens: number }>();
export function rateLimit(ip: string, limitPerMin = 90): boolean {
  const now = Date.now();
  const win = 60_000;
  const b = _bucket.get(ip) || { t: now, tokens: limitPerMin };
  const refill = Math.floor((now - b.t) / (win / limitPerMin));
  b.tokens = Math.min(limitPerMin, b.tokens + Math.max(0, refill));
  b.t = now;
  if (b.tokens <= 0) return false;
  b.tokens -= 1;
  _bucket.set(ip, b);
  return true;
}

export function scrubSecrets(text: string) {
  if (!text) return text;
  const rules: [RegExp, string][] = [
    [/(sk-[a-zA-Z0-9]{20,})/g, "[redacted-key]"],
    [/(AKIA[0-9A-Z]{16})/g, "[redacted-aws]"],
    [/([0-9a-f]{32,64})/gi, "[redacted-hash]"],
    [/(\b\d{3}-\d{2}-\d{4}\b)/g, "[redacted-ssn]"],
  ];
  for (const [re, tag] of rules) text = text.replace(re, tag);
  return text;
}

export async function edgeLog(event: GuardEvent) {
  try {
  const token = process.env.GUARDIAN_INGEST_TOKEN;
  if (!token) return;
  const base = process.env.NEXT_PUBLIC_BASE_URL || "";
  await fetch(`${base}/api/security/log`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-guardian-token": token },
      body: JSON.stringify(event),
      keepalive: true as any,
    }).catch(() => {});
  } catch {}
}

export async function alertWebhook(event: string, details: any = {}) {
  const hook = process.env.SECURITY_WEBHOOK_URL;
  if (!hook) return;
  try {
    await fetch(hook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event, details, ts: new Date().toISOString() }),
    });
  } catch {}
}
