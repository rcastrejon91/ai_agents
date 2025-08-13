// Use a provider like Moov/Stripe Treasury/Unit/Lithic + Plaid/Teller for link.
// Until then, simulate and log a pending transfer for manual approval.

export async function transferFunds(p: { from: string; to: string; amount: number; memo?: string }) {
  if (!p.amount || p.amount <= 0) return { error: 'invalid_amount' };
  // STUB: create a "transfer request" record; your backend later completes via provider API.
  return { status: 'pending', provider: 'manual', summary: `$${p.amount} ${p.from} → ${p.to}`, memo: p.memo || '' };
}
