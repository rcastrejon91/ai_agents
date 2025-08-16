export default function MicButton({ sendMessage }) {
  const startListening = () => {
    const recognition = new (window.SpeechRecognition ||
      window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.start();
    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      sendMessage(text);
    };
  };

  return (
    <button className="mic-button" onClick={startListening}>
      🎤
    </button>
  );
}
