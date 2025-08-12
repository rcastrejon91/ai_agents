import policies from './state_policies.json';

export type Mode = 'therapy' | 'friend' | 'journal' | 'friend+journal';

/**
 * Gate requested companion mode based on jurisdiction policies.
 * If therapy is restricted for a jurisdiction, we fall back to friend+journal mode.
 */
export function gateCompanionMode(requested: Mode, jurisdiction: string): Mode {
  const policy = (policies as Record<string, { therapy?: boolean }>)[jurisdiction];
  if (requested === 'therapy' && policy && policy.therapy === false) {
    return 'friend+journal';
  }
  return requested;
}
