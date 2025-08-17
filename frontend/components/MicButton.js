import { useState, useEffect } from "react";

export default function MicButton({ sendMessage }) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check for speech recognition support
    const speechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!speechRecognition);
  }, []);

  const startListening = () => {
    if (!isSupported) {
      setError("Speech recognition is not supported in this browser");
      return;
    }

    if (isListening) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = navigator.language || "en-US";

    setIsListening(true);
    setError(null);

    recognition.onstart = () => {
      console.log("Speech recognition started");
    };

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      if (text.trim()) {
        sendMessage(text);
      }
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setIsListening(false);
      
      switch (event.error) {
        case "not-allowed":
          setError("Microphone access denied. Please allow microphone access and try again.");
          break;
        case "no-speech":
          setError("No speech detected. Please try again.");
          break;
        case "network":
          setError("Network error. Please check your connection.");
          break;
        default:
          setError("Speech recognition failed. Please try again.");
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    try {
      recognition.start();
    } catch (err) {
      console.error("Failed to start speech recognition:", err);
      setIsListening(false);
      setError("Failed to start speech recognition");
    }
  };

  if (!isSupported) {
    return (
      <button 
        className="mic-button" 
        disabled
        title="Speech recognition not supported in this browser"
        style={{ opacity: 0.5, cursor: "not-allowed" }}
      >
        🎤
      </button>
    );
  }

  return (
    <>
      <button 
        className={`mic-button ${isListening ? 'listening' : ''}`}
        onClick={startListening}
        disabled={isListening}
        title={isListening ? "Listening... Speak now" : "Click to speak"}
        style={{
          background: isListening ? "#dc3545" : "#28a745",
          animation: isListening ? "pulse 1.5s infinite" : "none"
        }}
      >
        {isListening ? "🔴" : "🎤"}
      </button>
      
      {error && (
        <div 
          className="error-message"
          style={{
            position: "fixed",
            bottom: "100px",
            right: "10px",
            maxWidth: "250px",
            zIndex: 1001
          }}
        >
          {error}
          <button 
            onClick={() => setError(null)}
            style={{
              marginLeft: "8px",
              background: "none",
              border: "none",
              color: "inherit",
              cursor: "pointer",
              fontSize: "16px"
            }}
          >
            ×
          </button>
        </div>
      )}
      
      <style jsx>{`
        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.1); }
          100% { transform: scale(1); }
        }
        
        .mic-button.listening {
          box-shadow: 0 0 20px rgba(220, 53, 69, 0.5);
        }
      `}</style>
    </>
  );
}
