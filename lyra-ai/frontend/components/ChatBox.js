import { useState } from "react";
import MicButton from "./MicButton";

export default function ChatBox({ muted }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Enhanced speech synthesis function
  function speakText(text) {
    if (muted || typeof window === "undefined") return;

    // Cancel any existing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    // Configure for better quality
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 0.8;

    // Try to select a good voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(
      (voice) =>
        voice.lang.startsWith("en") &&
        (voice.name.includes("Google") ||
          voice.name.includes("Microsoft") ||
          voice.default),
    );
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    // Error handling
    utterance.onerror = (event) => {
      console.warn("Speech error:", event.error);
    };

    try {
      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.error("Speech failed:", err);
    }
  }

  async function sendMessage(e) {
    e.preventDefault();
    const userMessage = input.trim();
    if (!userMessage || loading) return;

    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setMessages((prev) => [...prev, { sender: "lyra", text: data.reply }]);

      // Speak the response
      speakText(data.reply);
    } catch (err) {
      console.error("Chat error", err);
      setError(err.message);
      setMessages((prev) => [
        ...prev,
        {
          sender: "lyra",
          text: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleVoice(text) {
    setInput(text);
  }

  return (
    <div className="chat-container">
      <div className="chat-window">
        {messages.map((m, idx) => (
          <div key={idx} className={`message ${m.sender}`}>
            <div className="message-content">{m.text}</div>
          </div>
        ))}
        {loading && (
          <div className="message lyra">
            <div className="message-content loading">
              <span className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </span>
              Lyra is typing...
            </div>
          </div>
        )}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}
      </div>
      <form onSubmit={sendMessage} className="chat-form">
        <div className="input-container">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message"
            disabled={loading}
            className={loading ? "loading" : ""}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? "..." : "Send"}
          </button>
          <MicButton onResult={handleVoice} disabled={loading} />
        </div>
      </form>
    </div>
  );
}
