export async function safeFetchJSON(
  url: string,
  headers: Record<string, string> = {},
  ms = 12000
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

export function ts() {
  return new Date().toISOString();
}
