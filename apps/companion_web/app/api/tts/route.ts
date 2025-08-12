export const runtime = 'nodejs';
import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  const { text, voice } = await req.json();
  if (!text || !String(text).trim()) {
    return new Response(
      JSON.stringify({ ok: false, error: 'missing_text' }),
      { status: 400 }
    );
  }

  const model = 'gpt-4o-mini-tts';
  const chosenVoice = voice || process.env.LYRA_VOICE || 'alloy';

  const res = await fetch('https://api.openai.com/v1/audio/speech', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model,
      voice: chosenVoice,
      input: String(text).slice(0, 4000),
      format: 'mp3'
    })
  });

  if (!res.ok) {
    const err = await res.text().catch(() => '');
    return new Response(
      JSON.stringify({ ok: false, error: 'tts_failed', detail: err }),
      { status: 500 }
    );
  }

  const body = res.body!;
  return new Response(body, {
    status: 200,
    headers: {
      'Content-Type': 'audio/mpeg',
      'Cache-Control': 'no-store'
    }
  });
}
