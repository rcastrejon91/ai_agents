import { useState } from "react";

export default function ChatBox({ messages, sendMessage }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    setLoading(true);
    try {
      await sendMessage(input);
      setInput("");
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-box">
      <div className="messages">
        {messages.map((m, idx) => (
          <div key={idx} className={`message ${m.sender}`}>
            <div className="message-content">
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content loading">
              <span className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </span>
              Typing...
            </div>
          </div>
        )}
      </div>
      <div className="input-row">
        <input
          type="text"
          placeholder="Talk to Lyra..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          className={loading ? "loading" : ""}
        />
        <button 
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
