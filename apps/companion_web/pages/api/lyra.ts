import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const { message, mode = 'chill' } = (req.body ?? {}) as { message?: string; mode?: string };

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Missing "message" in body' });
    }

    if (!process.env.OPENAI_API_KEY) {
      return res.status(200).json({ reply: `(demo:${mode}) ${message}` });
    }

    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: `You are Lyra, a ${mode} assistant.` },
          { role: 'user', content: message },
        ],
      }),
    });

    if (!r.ok) {
      const errText = await r.text();
      console.error('[lyra] openai error:', errText);
      return res
        .status(500)
        .json({ error: "Sorry, I'm having trouble responding right now." });
    }

    const data = await r.json();
    const reply = data?.choices?.[0]?.message?.content?.trim();
    return res
      .status(200)
      .json({ reply: reply ?? "I'm not sure what to say, but I'm here!" });
  } catch (err) {
    console.error('[lyra] error:', err);
    return res
      .status(500)
      .json({ error: "I'm having trouble replying right now." });
  }
}

