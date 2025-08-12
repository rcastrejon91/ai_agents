import { useState } from 'react';
import AdminVoiceGate from "../app/(components)/AdminVoiceGate";
import { unlockAudio, speak } from "../app/lib/speech";
import { AnswerCard } from "../components/AnswerCard";

export default function Home() {
  const [mode, setMode] = useState<'credible'|'creative'>('credible');
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<{role:'you'|'lyra';type:'answer'|'plain';text:string;sources?:{title:string;url:string}[]}[]>([]);
  const [opsLog, setOpsLog] = useState<{t:number;msg:string}[]>([]);

  async function ask(question: string) {
    try {
      const r = await fetch('/api/answer', {
        method:'POST',
        headers:{'content-type':'application/json'},
        body: JSON.stringify({ question })
      });
      if (!r.ok) return false;
      const data = await r.json();
      setMessages(m => [...m, { role:'lyra', type:'answer', text: data.answer, sources: data.sources }]);
      setOpsLog(l => [
        { t: Date.now(), msg: `Answer via /api/answer • sources:${data.sources?.length||0} • model:gpt-4o-mini` },
        ...l
      ].slice(0,50));
      return true;
    } catch (e) {
      console.error('ask error', e);
      return false;
    }
  }

  async function sendPlain(question: string) {
    try {
      const resp = await fetch('/api/lyra', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: question })
      });
      const data = (await resp.json()) as { reply?: string; error?: string };
      const textReply = data.reply ?? data.error ?? 'I had trouble replying.';
      setMessages(m => [...m, { role: 'lyra', type:'plain', text: textReply }]);
      setOpsLog(l => [
        { t: Date.now(), msg: 'Answer via /api/lyra' },
        ...l
      ].slice(0,50));
    } catch (e) {
      console.error('sendPlain error', e);
      setMessages(m => [...m, { role:'lyra', type:'plain', text: '(error sending message)' }]);
    }
  }

  async function send() {
    const text = input.trim();
    if (!text || busy) return;
    setInput(''); setBusy(true);
    setMessages(m => [...m, { role:'you', type:'plain', text }]);
    try {
      let handled = false;
      if (mode === 'credible') {
        handled = await ask(text);
      }
      if (!handled) {
        await sendPlain(text);
      }
    } catch (e) {
      console.error('send error', e);
      setMessages(m => [...m, { role: 'lyra', type:'plain', text: '(error sending message)' }]);
    } finally { setBusy(false); }
  }

  return (
    <div style={{minHeight:'100vh',background:'#0b0f16',color:'#e6f1ff',padding:'24px',maxWidth:780,margin:'0 auto'}}>
      <h1 style={{fontSize:28,marginBottom:6}}>AITaskFlo</h1>
      <div style={{opacity:.7,marginBottom:16}}>Your personality-driven AI console.</div>
      <button
        onClick={() => unlockAudio()}
        style={{
          padding: '4px 8px',
          borderRadius: 6,
          background: '#121826',
          border: '1px solid #223',
          fontSize: 12,
          marginBottom: 16
        }}
      >
        Enable sound 🔊
      </button>

      <div className="card" style={{marginBottom:12,display:'flex',alignItems:'center',justifyContent:'space-between'}}>
        <div className="text-sm">Mode</div>
        <div className="flex gap-2" style={{display:'flex',gap:8}}>
          <button className={`badge ${mode==='credible'?'glow':''}`} onClick={()=>setMode('credible')}>Evidence</button>
          <button className={`badge ${mode==='creative'?'glow':''}`} onClick={()=>setMode('creative')}>Creative</button>
        </div>
      </div>

      <div style={{border:'1px solid #223',borderRadius:12,padding:12,minHeight:320,background:'#0e1422'}}>
        {messages.length===0 && <div style={{opacity:.6}}>Say hi and I’ll reply…</div>}
        {messages.map((m,i)=>(
          m.role==='lyra' && m.type==='answer'
            ? <AnswerCard key={i} text={m.text} sources={m.sources||[]} onSpeak={()=>speak(m.text)} />
            : <div key={i} style={{margin:'10px 0'}}>
                <b style={{color:m.role==='you'?'#9ff':'#9f9'}}>{m.role==='you'?'You':'Lyra'}</b>: {m.text}
                {m.role==='lyra' && (
                  <button
                    onClick={() => speak(m.text)}
                    style={{ marginLeft: 8, fontSize: '0.8em', opacity: 0.7 }}
                  >
                    🔊
                  </button>
                )}
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
          style={{padding:'10px 16px',borderRadius:10,background:'linear-gradient(90deg,#6ee7,#8af)',border:'none',color:'#001'}}
        >
          Send
        </button>
      </div>

      <div className="card mt-3" style={{marginTop:12}}>
        <div className="text-sm font-medium mb-2">Activity</div>
        <ul className="text-xs text-zinc-400 space-y-1">
          {opsLog.map((e,i)=> <li key={i}>• {new Date(e.t).toLocaleTimeString()} — {e.msg}</li>)}
        </ul>
      </div>

      <div style={{marginTop:12,fontSize:'11px',color:'#71717a'}}>
        Lyra provides AI-generated assistance with linked sources. Not professional advice.
      </div>

      <AdminVoiceGate />
    </div>
  );
}
