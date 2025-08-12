'use client';
import { useState } from 'react';

export default function SourcesForm() {
  const [wiki, setWiki] = useState('');
  const [gutenberg, setGutenberg] = useState('');
  const [youtube, setYoutube] = useState('');
  const [status, setStatus] = useState('');

  async function submit(type: string, idOrUrl: string) {
    if (!idOrUrl) return;
    setStatus('Loading...');
    try {
      const resp = await fetch('/api/learn/queue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, idOrUrl }),
      });
      const data = await resp.json();
      setStatus(resp.ok ? `Inserted ${data.inserted} chunks` : data.error || 'Error');
    } catch {
      setStatus('Error');
    }
  }

  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <input
          value={wiki}
          onChange={(e) => setWiki(e.target.value)}
          placeholder="Wikipedia title or URL"
          style={{ flex: 1, padding: 6 }}
        />
        <button onClick={() => submit('wikipedia', wiki)}>Add</button>
      </div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <input
          value={gutenberg}
          onChange={(e) => setGutenberg(e.target.value)}
          placeholder="Gutenberg ID or URL"
          style={{ flex: 1, padding: 6 }}
        />
        <button onClick={() => submit('gutenberg', gutenberg)}>Add</button>
      </div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <input
          value={youtube}
          onChange={(e) => setYoutube(e.target.value)}
          placeholder="YouTube URL"
          style={{ flex: 1, padding: 6 }}
        />
        <button onClick={() => submit('youtube', youtube)}>Add</button>
      </div>
      {status && <div>{status}</div>}
    </div>
  );
}
