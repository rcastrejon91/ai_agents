export const config = { api: { bodyParser: true } };

export default async function handler(req: any, res: any) {
  try {
    if (req.method !== 'POST') return res.status(405).end();
    const message = (req.body?.message || '').toString().trim();

    if (process.env.NEXT_PUBLIC_LYRA_DEBUG === '1') {
      return res.status(200).json({ reply: `🛠️ Debug: You said “${message}”.` });
    }

    if (!process.env.OPENAI_API_KEY) {
      return res.status(200).json({ reply: `(demo) ${message}` });
    }

    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: message || 'hi' }],
      }),
    });

    if (!r.ok) {
      const t = await r.text().catch(()=> '');
      console.error('[lyra] upstream', r.status, t.slice(0,300));
      return res.status(200).json({ reply: `⚠️ Live model is busy. Echo: “${message}”` });
    }

    const j = await r.json();
    const reply = j?.choices?.[0]?.message?.content?.trim() || '…';
    return res.status(200).json({ reply });
  } catch (e: any) {
    console.error('[lyra] exception', e?.stack || e);
    return res.status(200).json({ reply: '⚠️ Temporary hiccup. Try again.' });
  }
}
