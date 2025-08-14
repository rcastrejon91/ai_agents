import { useState } from 'react';

export default function MicButton({ onTranscript }) {
  const [listening, setListening] = useState(false);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition not supported.');
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      onTranscript(transcript);
    };
    recognition.onend = () => setListening(false);
    recognition.start();
    setListening(true);
  };

  return (
    <button type="button" onClick={startListening}>
      {listening ? 'Listening…' : 'Speak'}
    </button>
  );
}
