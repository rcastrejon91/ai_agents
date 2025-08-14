import { useState } from 'react';
import ChatBox from '../components/ChatBox';
import ModeBubble from '../components/ModeBubble';
import MuteToggle from '../components/MuteToggle';

export default function Home() {
  const [muted, setMuted] = useState(false);
  return (
    <div className="container">
      <ModeBubble />
      <ChatBox muted={muted} />
      <MuteToggle muted={muted} setMuted={setMuted} />
    </div>
  );
}
