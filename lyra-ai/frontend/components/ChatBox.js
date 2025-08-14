import { useState } from 'react';
import MicButton from './MicButton';
import ModeBubble from './ModeBubble';
import MuteToggle from './MuteToggle';

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [muted, setMuted] = useState(false);
  const [mode, setMode] = useState('default');

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    setMessages((msgs) => [...msgs, { sender: 'user', text }]);
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    const reply = data.response || '';
    setMessages((msgs) => [...msgs, { sender: 'lyra', text: reply }]);
    if (!muted && typeof window !== 'undefined') {
      const utter = new SpeechSynthesisUtterance(reply);
      window.speechSynthesis.speak(utter);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
    setInput('');
  };

  const handleTranscript = (transcript) => {
    setInput(transcript);
    sendMessage(transcript);
  };

  return (
    <div>
      <ModeBubble mode={mode} />
      <div className="chat-log">
        {messages.map((m, i) => (
          <div key={i} className={m.sender}>{m.text}</div>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={(e) => setInput(e.target.value)} />
        <button type="submit">Send</button>
      </form>
      <MicButton onTranscript={handleTranscript} />
      <MuteToggle muted={muted} onToggle={() => setMuted(!muted)} />
    </div>
  );
}
