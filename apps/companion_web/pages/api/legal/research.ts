import type { NextApiRequest, NextApiResponse } from 'next';
import { isAllowed, banner, requireJurisdiction, redact, shouldRefuse } from '../../../../../server/legal/guardrails';
import { tavilySearch, openaiSummarize, roleFrom, checkLimit } from './_common';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const role = roleFrom(req);
  if (!isAllowed(role)) return res.status(403).json({ error: 'forbidden' });

  const { query, jurisdiction, intent = 'research' } = (req.body as any) || {};
  if (!query || typeof query !== 'string') return res.status(400).json({ error: 'query required' });

  if (shouldRefuse(intent, role)) {
    return res.status(403).json({ error: 'refused', message: 'Please escalate to an attorney.' });
  }

  if (!checkLimit(req, res)) return;

  const { juris, note } = requireJurisdiction(jurisdiction);
  const search = await tavilySearch(query);
  const citationLines = search.results.map((r: any, i: number) => `[${i + 1}] ${r.title} (${r.url})`).join('\n');
  const prompt = `Jurisdiction: ${juris}.\nQuestion: ${query}\n\nSources:\n${citationLines}\n\nSummarize with citations.`;
  const summary = await openaiSummarize(prompt);

  console.log(`[LEGAL_AUDIT] research role=${role} juris=${juris} query=${redact(query)}`);

  return res.status(200).json({
    reply: `${banner} ${note}\n\n${summary}`,
    citations: search.results.map((r: any) => ({ title: r.title, url: r.url }))
  });
}
