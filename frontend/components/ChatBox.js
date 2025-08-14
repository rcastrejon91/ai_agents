import { useState } from "react";

export default function ChatBox({ messages, sendMessage }) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    sendMessage(input);
    setInput("");
  };

  return (
    <div className="chat-box">
      <div className="messages">
        {messages.map((m, idx) => (
          <div key={idx} className={m.sender}>
            {m.text}
          </div>
        ))}
      </div>
      <div className="input-row">
        <input
          type="text"
          placeholder="Talk to Lyra..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}
