import { useState, useRef, useCallback, useEffect } from "react";
import ChatBox from "../components/ChatBox";
import MicButton from "../components/MicButton";
import ModeBubble from "../components/ModeBubble";
import MuteToggle from "../components/MuteToggle";

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [mode, setMode] = useState("default");
  const [muted, setMuted] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const audioRef = useRef(null);

  // Check online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const sendMessage = useCallback(async (text) => {
    if (!isOnline) {
      setMessages((prev) => [
        ...prev,
        { 
          sender: "system", 
          text: "You're offline. Please check your internet connection.", 
          isError: true,
          timestamp: Date.now()
        }
      ]);
      throw new Error("Offline");
    }

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      const data = await res.json();

      if (data.error) {
        throw new Error(data.error);
      }

      const newMessages = [
        { 
          sender: "user", 
          text, 
          timestamp: Date.now() 
        },
        { 
          sender: "lyra", 
          text: data.reply || "I'm sorry, I couldn't generate a response.",
          timestamp: Date.now()
        },
      ];

      setMessages((prev) => [...prev, ...newMessages]);

      // Handle speech synthesis with error handling
      if (!muted && data.reply && 'speechSynthesis' in window) {
        try {
          const utterance = new SpeechSynthesisUtterance(data.reply);
          utterance.onerror = (event) => {
            console.warn("Speech synthesis error:", event.error);
          };
          window.speechSynthesis.speak(utterance);
        } catch (speechError) {
          console.warn("Speech synthesis failed:", speechError);
        }
      }

    } catch (error) {
      console.error("Chat error:", error);
      
      const errorMessage = {
        sender: "system",
        text: error.message.includes("fetch") 
          ? "Network error. Please check your connection and try again."
          : `Error: ${error.message}`,
        isError: true,
        timestamp: Date.now()
      };

      setMessages((prev) => [
        ...prev,
        { sender: "user", text, timestamp: Date.now() },
        errorMessage
      ]);
      
      throw error; // Re-throw for ChatBox to handle
    }
  }, [muted, isOnline]);

  return (
    <div className="app-container">
      <ModeBubble mode={mode} />
      <MuteToggle muted={muted} setMuted={setMuted} />
      <ChatBox messages={messages} sendMessage={sendMessage} />
      <MicButton sendMessage={sendMessage} />
      
      {/* Offline indicator */}
      {!isOnline && (
        <div 
          style={{
            position: "fixed",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            background: "#f8d7da",
            color: "#721c24",
            padding: "12px 24px",
            borderRadius: "8px",
            border: "1px solid #f5c6cb",
            zIndex: 1002,
            textAlign: "center"
          }}
        >
          📱 You're offline. Some features may not work.
        </div>
      )}
    </div>
  );
}
