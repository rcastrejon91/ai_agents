import { useEffect, useState } from 'react';

export default function CompanionCheckupsPanel() {
  const [tone, setTone] = useState('kind');
  const [daily, setDaily] = useState(false);
  const [email, setEmail] = useState('');
  const [last, setLast] = useState('');

  useEffect(() => {
    fetch('/api/companion/checkups', { headers: { 'x-user-id': 'demo' } })
      .then(r => r.json())
      .then(d => {
        if (d.tone) setTone(d.tone);
        if (d.daily) setDaily(d.daily);
        if (d.email) setEmail(d.email);
      });
  }, []);

  async function save() {
    await fetch('/api/companion/checkups', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-user-id': 'demo' },
      body: JSON.stringify({ tone, daily, email })
    });
  }

  async function sendNow() {
    const resp = await fetch('/api/companion/checkups?preview=1', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'x-user-id': 'demo', 'x-jurisdiction': 'US-CA' },
      body: JSON.stringify({ tone })
    });
    const data = await resp.json();
    setLast(data.message);
  }

  return (
    <div style={{border:'1px solid #223',padding:12,borderRadius:8}}>
      <h3 style={{marginTop:0}}>Companion Checkups</h3>
      <div style={{marginBottom:8}}>
        <label>Tone:</label>
        <select value={tone} onChange={e=>setTone(e.target.value)} style={{marginLeft:4}}>
          <option value="kind">kind</option>
          <option value="playful">playful</option>
          <option value="professional">professional</option>
        </select>
      </div>
      <div style={{marginBottom:8}}>
        <label>
          <input type="checkbox" checked={daily} onChange={e=>setDaily(e.target.checked)} /> Daily check-in
        </label>
      </div>
      <div style={{marginBottom:8}}>
        <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" style={{width:'100%'}} />
      </div>
      <div style={{display:'flex',gap:8}}>
        <button onClick={save}>Save</button>
        <button onClick={sendNow}>Send now</button>
      </div>
      {last && <div style={{marginTop:8,opacity:.7,whiteSpace:'pre-wrap'}}>{last}</div>}
    </div>
  );
}
