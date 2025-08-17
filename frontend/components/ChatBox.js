import { useState } from "react";

export default function ChatBox({ messages, sendMessage }) {
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState("connected");

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    
    const messageText = input.trim();
    setInput("");
    setIsTyping(true);
    setConnectionStatus("connecting");
    
    try {
      await sendMessage(messageText);
      setConnectionStatus("connected");
    } catch (error) {
      console.error("Failed to send message:", error);
      setConnectionStatus("disconnected");
      // Add error message to chat
      const errorMessage = {
        sender: "system",
        text: "Failed to send message. Please check your connection and try again.",
        isError: true,
        timestamp: Date.now()
      };
      // Note: This would need to be handled by the parent component
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Connection Status Indicator */}
      <div className={`connection-status ${connectionStatus}`}>
        {connectionStatus === "connected" && "🟢 Connected"}
        {connectionStatus === "connecting" && "🟡 Connecting..."}
        {connectionStatus === "disconnected" && "🔴 Disconnected"}
      </div>

      <div className="chat-box">
        <div className="messages">
          {messages.map((m, idx) => (
            <div key={idx} className={`${m.sender} ${m.isError ? 'error-message' : ''}`}>
              {m.text}
              {m.timestamp && (
                <div style={{ fontSize: '10px', opacity: 0.5, marginTop: '4px' }}>
                  {new Date(m.timestamp).toLocaleTimeString()}
                </div>
              )}
            </div>
          ))}
          
          {/* Typing indicator */}
          {isTyping && (
            <div className="lyra">
              <span className="loading-dots">Lyra is typing</span>
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
            disabled={isTyping}
            maxLength={500}
          />
          <button 
            onClick={handleSend}
            disabled={isTyping || !input.trim()}
            title={isTyping ? "Sending..." : "Send message"}
          >
            {isTyping ? "..." : "Send"}
          </button>
        </div>
      </div>
    </>
  );
}
