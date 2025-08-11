import type { NextApiRequest, NextApiResponse } from 'next';

export async function tavilySearch(query: string) {
  const r = await fetch('https://api.tavily.com/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': process.env.TAVILY_API_KEY || ''
    },
    body: JSON.stringify({ query, include_answer: true, max_results: 6 })
  }).then(r => r.json());
  return {
    answer: r.answer || '',
    results: (r.results || []).map((x: any) => ({ title: x.title, url: x.url, snippet: x.snippet }))
  };
}

export async function openaiSummarize(prompt: string): Promise<string> {
  if (!process.env.OPENAI_API_KEY) return '(no model key)';
  const r = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are a legal research assistant. Cite sources with [1], [2].' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.2
    })
  }).then(r => r.json());
  return r?.choices?.[0]?.message?.content?.trim() || '';
}

export function roleFrom(req: NextApiRequest): string {
  return (req.headers['x-user-role'] as string) || 'guest';
}

export function checkLimit(req: NextApiRequest, res: NextApiResponse): boolean {
  const limit = parseInt(process.env.LEGAL_DAILY_LIMIT || '0', 10);
  if (!limit) return true;
  const current = parseInt(req.cookies['legal_daily'] || '0', 10) + 1;
  res.setHeader('Set-Cookie', `legal_daily=${current}; Path=/; HttpOnly; SameSite=Lax`);
  if (current > limit) {
    res.status(402).json({ error: 'limit', upgrade: process.env.BILLING_URL || null });
    return false;
  }
  return true;
}
