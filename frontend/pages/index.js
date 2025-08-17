import { useState, useRef } from "react";
import ChatBox from "../components/ChatBox";
import MicButton from "../components/MicButton";
import ModeBubble from "../components/ModeBubble";
import MuteToggle from "../components/MuteToggle";
import { config } from "../config";

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [mode, setMode] = useState("default");
  const [muted, setMuted] = useState(false);
  const audioRef = useRef(null);

  const sendMessage = async (text) => {
    try {
      const res = await fetch(`${config.backendUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
        timeout: 10000, // 10 second timeout
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { sender: "user", text },
        { sender: "lyra", text: data.reply },
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        { sender: "user", text },
        { sender: "lyra", text: "Sorry, I'm having trouble connecting to the server. Please try again." },
      ]);
    }
  };

  return (
    <div className="app-container">
      <ModeBubble mode={mode} />
      <MuteToggle muted={muted} setMuted={setMuted} />
      <ChatBox messages={messages} sendMessage={sendMessage} />
      <MicButton sendMessage={sendMessage} />
    </div>
  );
}
