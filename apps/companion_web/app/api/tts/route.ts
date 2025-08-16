export const runtime = "nodejs";
import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  let payload: any = {};
  try {
    payload = await req.json();
  } catch (err) {
    console.error("Failed to parse TTS request", err);
    payload = {};
  }
  const { text, voice } = payload;
  if (!text || !String(text).trim()) {
    return new Response(JSON.stringify({ ok: false, error: "missing_text" }), {
      status: 400,
    });
  }

  const model = "gpt-4o-mini-tts";
  const chosenVoice = voice || process.env.LYRA_VOICE || "alloy";

  const res = await fetch("https://api.openai.com/v1/audio/speech", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      voice: chosenVoice,
      input: String(text).slice(0, 4000),
      format: "mp3",
    }),
  });

  if (!res.ok) {
    let err = "";
    try {
      err = await res.text();
    } catch (e) {
      console.error("Failed to read TTS error response", e);
      err = "";
    }
    return new Response(
      JSON.stringify({ ok: false, error: "tts_failed", detail: err }),
      { status: 500 },
    );
  }

  const audio = res.body!;
  return new Response(audio, {
    status: 200,
    headers: {
      "Content-Type": "audio/mpeg",
      "Cache-Control": "no-store",
    },
  });
}
