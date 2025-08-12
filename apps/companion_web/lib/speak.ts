export function speak(text: string) {
  try {
    if (!text) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 1.0; u.pitch = 1.0; u.volume = 1.0;
    const use = () => {
      const vs = window.speechSynthesis.getVoices();
      const v = vs.find(v => /en/i.test(v.lang)) || vs[0];
      if (v) u.voice = v;
      window.speechSynthesis.speak(u);
    };
    if (window.speechSynthesis.getVoices().length) use();
    else window.speechSynthesis.onvoiceschanged = use;
  } catch {}
}
