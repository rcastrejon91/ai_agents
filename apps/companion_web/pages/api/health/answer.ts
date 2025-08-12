import type { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';
import { createClient } from '@supabase/supabase-js';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { question } = (req.body ?? {}) as { question?: string };
  if (!question) return res.status(400).json({ error: 'Missing question' });

  try {
    const supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );
    const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

    const embed = await openai.embeddings.create({
      model: 'text-embedding-3-small',
      input: question,
    });
    const embedding = embed.data[0].embedding;
    const { data: matches } = await supabase.rpc('match_doc_chunks', {
      embedding,
      match_threshold: 0.8,
      match_count: 5,
    });

    if (!matches || matches.length === 0 || (matches[0] as any).similarity < 0.8) {
      return res.status(200).json({
        reply: 'Not enough evidence—try adding a source in Admin ▸ Sources.',
      });
    }

    const context = (matches as any[]).map((m) => m.content).join('\n\n');
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content:
            'You are Lyra, a cautious health assistant. Use provided sources and respond safely.',
        },
        { role: 'user', content: `Question: ${question}\n\nSources:\n${context}` },
      ],
    });

    const reply = completion.choices[0]?.message?.content?.trim() || 'No answer.';
    return res.status(200).json({ reply, sources: matches });
  } catch (err) {
    console.error('[health/answer] error:', err);
    return res
      .status(500)
      .json({ error: "I'm having trouble replying right now." });
  }
}
