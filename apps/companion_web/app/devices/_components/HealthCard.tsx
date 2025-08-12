'use client';
import { useState } from 'react';

export default function HealthCard({ device }: { device: { id: string } }) {
  const [url, setUrl] = useState('http://localhost:3000/health');
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      await fetch('/api/devices/health-config', {
        method: 'POST',
        headers: { 'content-type':'application/json' },
        body: JSON.stringify({ device_id: device.id, health_url: url })
      });
      alert('Saved');
    } finally { setSaving(false); }
  }

  return (
    <div className="rounded-lg border border-zinc-800 p-4">
      <div className="text-sm font-medium mb-2">Health checks</div>
      <input className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-sm"
             value={url} onChange={e=>setUrl(e.target.value)} placeholder="http://host:port/health" />
      <button onClick={save} disabled={saving}
              className="mt-2 px-3 py-2 rounded bg-zinc-800 text-sm">
        {saving ? 'Saving…' : 'Save'}
      </button>
      <div className="text-xs text-zinc-400 mt-2">Agent pings this; auto‑reboots after 10 min down (if enabled).</div>
    </div>
  );
}

