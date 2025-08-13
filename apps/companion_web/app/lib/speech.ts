let unlocked = false;

// iOS/Chrome block audio until a user gesture. Call unlock() once from a click/tap.
export async function unlockAudio() {
  if (unlocked) return;
  try {
    const a = new Audio();
    a.muted = true;
    await a.play();
    unlocked = true;
  } catch (err) {
    console.error('Audio unlock failed', err);
  }
}

export async function speak(text: string, opts?: { voice?: string; volume?: number }) {
  const r = await fetch('/api/tts', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ text, voice: opts?.voice })
  });
  if (!r.ok) {
    console.warn('TTS failed', await r.text());
    return false;
  }
  const blob = await r.blob();
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.volume = Math.min(Math.max(opts?.volume ?? 0.5, 0), 1);
  try {
    await audio.play();
    return true;
  } catch (e) {
    console.warn('Autoplay blocked. User gesture required.');
    return false;
  }
}
