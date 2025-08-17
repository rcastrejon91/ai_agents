"use client";
import { useEffect, useRef, useState } from "react";
type SpeechRecognition = any;
const PHRASE = (
  process.env.NEXT_PUBLIC_ADMIN_WAKE || "access alpha lyra"
).toLowerCase();

export default function AdminVoiceGate() {
  const [listening, setListening] = useState(false);
  const [armed, setArmed] = useState(false);
  const [voicesLoaded, setVoicesLoaded] = useState(false);
  const recogRef = useRef<SpeechRecognition | null>(null);

  // Initialize voices
  useEffect(() => {
    const loadVoices = () => {
      const voices = speechSynthesis.getVoices();
      if (voices.length > 0) {
        setVoicesLoaded(true);
        console.log(
          "Available voices:",
          voices.map((v) => v.name),
        );
      }
    };

    // Load voices immediately if available
    loadVoices();

    // Also listen for the voiceschanged event (needed for some browsers)
    speechSynthesis.addEventListener("voiceschanged", loadVoices);

    return () => {
      speechSynthesis.removeEventListener("voiceschanged", loadVoices);
    };
  }, []);

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
    // Cancel any existing speech
    speechSynthesis.cancel();

    const u = new SpeechSynthesisUtterance(text);

    // Configure voice settings for better quality
    u.rate = 0.9; // Slightly slower for clarity
    u.pitch = 1.0; // Normal pitch
    u.volume = 0.8; // Comfortable volume

    // Try to use a preferred voice if available
    const voices = speechSynthesis.getVoices();
    const preferredVoice = voices.find(
      (voice) =>
        voice.lang.startsWith("en") &&
        (voice.name.includes("Google") ||
          voice.name.includes("Microsoft") ||
          voice.default),
    );
    if (preferredVoice) {
      u.voice = preferredVoice;
    }

    // Add error handling and fallback
    u.onerror = (event) => {
      console.warn("Speech synthesis error:", event.error);
      // Fallback: try basic speech without voice configuration
      const fallback = new SpeechSynthesisUtterance(text);
      fallback.rate = 1.0;
      fallback.volume = 0.8;
      try {
        speechSynthesis.speak(fallback);
      } catch (err) {
        console.error("Speech synthesis completely failed:", err);
      }
    };

    // Add completion handler
    u.onend = () => {
      console.log("Speech synthesis completed");
    };

    try {
      speechSynthesis.speak(u);
    } catch (err) {
      console.error("Speech synthesis failed:", err);
    }
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
