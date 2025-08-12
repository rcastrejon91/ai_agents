export default async function handler(_req: any, res: any) {
  const env = { OPENAI_API_KEY: !!process.env.OPENAI_API_KEY, DEBUG: process.env.NEXT_PUBLIC_LYRA_DEBUG === '1' };
  let openai = { ok:false, note:'' } as { ok: boolean; note: string };
  if (env.OPENAI_API_KEY) {
    try {
      const r = await fetch('https://api.openai.com/v1/models', {
        headers: { authorization: `Bearer ${process.env.OPENAI_API_KEY}` }
      });
      openai.ok = r.ok; openai.note = r.ok ? 'reachable' : `HTTP ${r.status}`;
    } catch (e: any) { openai.note = e?.message || 'network error'; }
  } else { openai.note = 'no key (demo/echo)'; }
  res.status(200).json({ env, openai });
}
