"use client";
import { useEffect, useRef, useState } from "react";
type SpeechRecognition = any;
const PHRASE = (
  process.env.NEXT_PUBLIC_ADMIN_WAKE || "access alpha lyra"
).toLowerCase();

export default function AdminVoiceGate() {
  const [listening, setListening] = useState(false);
  const [armed, setArmed] = useState(false);
  const recogRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    const SR =
      (window as any).webkitSpeechRecognition ||
      (window as any).SpeechRecognition;
    if (!SR) return;
    const rec: SpeechRecognition = new SR();
    rec.lang = "en-US";
    rec.continuous = true;
    rec.interimResults = false;
    rec.onresult = async (e: any) => {
      const text =
        e.results[e.results.length - 1][0].transcript?.toLowerCase().trim() ||
        "";
      if (!text) return;
      if (!armed && text.includes(PHRASE)) {
        setArmed(true);
        speak(
          "Admin wake phrase recognized. Say enable admin or disable admin.",
        );
        return;
      }
      if (armed) {
        if (text.includes("enable admin")) {
          await fetch("/api/admin/mode", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ passphrase: PHRASE, admin: true }),
          });
          speak(
            "Admin Mode enabled. Say a personality: Chill, Sassy, Sage, Gremlin, Guardian, or Gamer.",
          );
        } else if (text.includes("disable admin")) {
          await fetch("/api/admin/mode", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ passphrase: PHRASE, admin: false }),
          });
          speak("Admin Mode disabled.");
          setArmed(false);
        } else {
          const m = text.match(/(chill|sassy|sage|gremlin|guardian|gamer)/);
          if (m) {
            await fetch("/api/admin/mode", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ passphrase: PHRASE, personality: m[1] }),
            });
            speak(`${m[1]} personality locked in.`);
            setArmed(false);
          }
        }
      }
    };
    rec.onerror = () => setListening(false);
    recogRef.current = rec;
  }, []);
  function start() {
    try {
      recogRef.current?.start();
      setListening(true);
      speak("Listening for admin wake phrase.");
    } catch {}
  }
  function stop() {
    try {
      recogRef.current?.stop();
      setListening(false);
    } catch {}
  }
  function speak(text: string) {
    const u = new SpeechSynthesisUtterance(text);
    speechSynthesis.speak(u);
  }
  return (
    <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2">
      <button
        className="px-3 py-2 rounded bg-zinc-800 border border-zinc-700"
        onClick={listening ? stop : start}
      >
        {listening ? "🛑 Stop Admin Voice" : "🎙️ Admin Voice"}
      </button>
      <span className="text-xs text-zinc-400">
        {armed ? "Awaiting command…" : "Say: 'Access Alpha Lyra'"}
      </span>
    </div>
  );
}
