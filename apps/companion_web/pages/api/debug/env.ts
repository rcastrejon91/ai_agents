// /api/debug/env
export default function handler(req, res) {
  const ok = !!process.env.OPENAI_API_KEY;
  // don't leak the key, just say if it's present
  res.status(ok ? 200 : 500).json({ openai_key_present: ok });
}
