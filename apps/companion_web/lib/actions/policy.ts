export async function checkScopes(plan: { steps: { kind: string }[] }) {
  const required = new Set(plan.steps.map((s) => s.kind));
  // TODO: read granted scopes from user session/profile
  const granted = new Set<string>(); // stub
  const missing = Array.from(required).filter((k) => !granted.has(k));
  return { granted: Array.from(granted), missing };
}

export function needsStrongAuth(plan: { steps: { kind: string }[] }) {
  return plan.steps.some((s) => /payments\.|transfer|book/.test(s.kind));
}
