import { useState } from "react";

export default function MicButton({ onResult }) {
  const [recording, setRecording] = useState(false);

  function startListening() {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition not supported");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.onresult = (e) => {
      const text = e.results[0][0].transcript;
      onResult && onResult(text);
    };
    recognition.onend = () => setRecording(false);
    recognition.start();
    setRecording(true);
  }

  return (
    <button type="button" onClick={startListening}>
      {recording ? "Listening..." : "🎤"}
    </button>
  );
}
