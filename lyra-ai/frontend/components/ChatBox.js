import { useState } from 'react';
import MicButton from './MicButton';

export default function ChatBox({ muted }) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  async function sendMessage(e) {
    e.preventDefault();
    const userMessage = input.trim();
    if (!userMessage) return;
    setMessages(prev => [...prev, { sender: 'user', text: userMessage }]);
    setInput('');
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { sender: 'lyra', text: data.response }]);
      if (!muted && typeof window !== 'undefined') {
        const utter = new SpeechSynthesisUtterance(data.response);
        window.speechSynthesis.speak(utter);
      }
    } catch (err) {
      console.error('Chat error', err);
    }
  }

  function handleVoice(text) {
    setInput(text);
  }

  return (
    <div>
      <div className="chat-window">
        {messages.map((m, idx) => (
          <div key={idx} className={m.sender}>
            {m.text}
          </div>
        ))}
      </div>
      <form onSubmit={sendMessage} className="chat-form">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type your message"
        />
        <button type="submit">Send</button>
        <MicButton onResult={handleVoice} />
      </form>
    </div>
  );
}
