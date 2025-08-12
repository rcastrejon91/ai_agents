import { useRouter } from 'next/router';
import { useState } from 'react';

const ADMIN_KEY = process.env.NEXT_PUBLIC_ADMIN_UI_KEY;

export default function CheckupsAdmin() {
  const router = useRouter();
  const { key } = router.query;
  const [tone, setTone] = useState('kind');
  const [preview, setPreview] = useState('');

  if (ADMIN_KEY && key !== ADMIN_KEY) {
    return <div>Forbidden</div>;
  }

  async function doPreview() {
    const resp = await fetch(`/api/companion/checkups?preview=1`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'x-user-id': 'demo', 'x-jurisdiction': 'US' },
      body: JSON.stringify({ tone })
    });
    const data = await resp.json();
    setPreview(data.message);
  }

  async function trigger() {
    await fetch(`/api/companion/checkups`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'x-user-id': 'demo', 'x-jurisdiction': 'US' },
      body: JSON.stringify({ tone })
    });
  }

  return (
    <div style={{padding:20}}>
      <h1>Companion Checkups</h1>
      <label>Tone: </label>
      <select value={tone} onChange={e=>setTone(e.target.value)}>
        <option value="kind">kind</option>
        <option value="playful">playful</option>
        <option value="professional">professional</option>
      </select>
      <div style={{marginTop:12}}>
        <button onClick={doPreview}>Preview message</button>
        <button onClick={trigger} style={{marginLeft:8}}>Send now</button>
      </div>
      {preview && <pre style={{marginTop:16,whiteSpace:'pre-wrap'}}>{preview}</pre>}
    </div>
  );
}
