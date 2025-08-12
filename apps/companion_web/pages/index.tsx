import { useState } from 'react';
import JurisdictionControl from '../components/JurisdictionControl';

const MODES = ['chill','sassy','sage','gremlin'] as const;
type Mode = typeof MODES[number];

export default function Home() {
  const [mode, setMode] = useState<Mode>('chill');
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<{role:'you'|'lyra';text:string}[]>([]);

  async function send() {
    const text = input.trim();
    if (!text || busy) return;
    setInput(''); setBusy(true);
    setMessages(m => [...m, { role:'you', text }]);
    try {
      const resp = await fetch('/api/lyra', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, mode }),
      });
      const data = (await resp.json()) as { reply?: string; error?: string };
      const textReply = data.reply ?? data.error ?? 'I had trouble replying.';
      setMessages(m => [...m, { role: 'lyra', text: textReply }]);
    } catch (e) {
      console.error('send error', e);
      setMessages(m => [...m, { role: 'lyra', text: '(error sending message)' }]);
    } finally { setBusy(false); }
  }

  return (
    <div style={{minHeight:'100vh',background:'#0b0f16',color:'#e6f1ff',padding:'24px',maxWidth:780,margin:'0 auto'}}>
      <h1 style={{fontSize:28,marginBottom:6}}>AITaskFlo</h1>
      <div style={{opacity:.7,marginBottom:16}}>Your personality-driven AI console.</div>

      <div style={{display:'flex',gap:8,flexWrap:'wrap',marginBottom:16}}>
        {MODES.map(m => (
          <button key={m} onClick={()=>setMode(m)}
            style={{ padding:'8px 12px', borderRadius:10, border:'1px solid #223',
                     background: m===mode ? 'linear-gradient(90deg,#6ee7,#8af)' : '#121826',
                     color: m===mode ? '#001' : '#e6f1ff' }}>
            {m}
          </button>
        ))}
      </div>

      <div style={{border:'1px solid #223',borderRadius:12,padding:12,minHeight:320,background:'#0e1422'}}>
        {messages.length===0 && <div style={{opacity:.6}}>Say hi and I’ll reply…</div>}
        {messages.map((m,i)=>(
          <div key={i} style={{margin:'10px 0'}}>
            <b style={{color:m.role==='you'?'#9ff':'#9f9'}}>{m.role==='you'?'You':'Lyra'}</b>: {m.text}
          </div>
        ))}
        {busy && <div style={{opacity:.6,marginTop:8}}>Lyra is typing…</div>}
      </div>

      <div style={{display:'flex',gap:8,marginTop:12}}>
        <input
          value={input}
          onChange={e=>setInput(e.target.value)}
          onKeyDown={e=>e.key==='Enter' && send()}
          placeholder="Type a message…"
          style={{flex:1,padding:'10px 12px',borderRadius:10,border:'1px solid #223',background:'#0e1422',color:'#e6f1ff'}}
        />
        <button onClick={send} disabled={busy}
          style={{padding:'10px 16px',borderRadius:10,background:'linear-gradient(90deg,#6ee7,#8af)',border:'none',color:'#001'}}>
          Send
        </button>
      </div>
      <JurisdictionControl userId="anon" />
    </div>
  );
}
