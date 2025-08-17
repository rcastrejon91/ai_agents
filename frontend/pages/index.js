import { useState, useRef } from "react";
import ChatBox from "../components/ChatBox";
import MicButton from "../components/MicButton";
import ModeBubble from "../components/ModeBubble";
import MuteToggle from "../components/MuteToggle";
import { config } from '../config';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [mode, setMode] = useState("default");
  const [muted, setMuted] = useState(false);
  const audioRef = useRef(null);

  const sendMessage = async (text) => {
    const res = await fetch(`${config.backendUrl}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();

    setMessages((prev) => [
      ...prev,
      { sender: "user", text },
      { sender: "lyra", text: data.reply },
    ]);
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
