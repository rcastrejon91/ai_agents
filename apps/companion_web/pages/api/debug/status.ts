export default function handler(req, res) {
  const env = {
    OPENAI_API_KEY: !!process.env.OPENAI_API_KEY,
    DEBUG: !!process.env.DEBUG,
  };
  const openai = env.OPENAI_API_KEY ? { ok: true, note: '' } : { ok: false, note: 'no key' };
  res.status(200).json({ env, openai });
}
