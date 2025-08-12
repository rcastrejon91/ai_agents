'use client';
import { useState } from 'react';

export default function CommandButtons({ device, onDone }: { device: { id: string; public_name: string }, onDone: () => void }) {
  const [busy, setBusy] = useState<'shutdown'|'reboot'|null>(null);

  async function send(action: 'shutdown' | 'reboot') {
    setBusy(action);
    try {
      const r = await fetch('/api/devices/command/initiate', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ device_id: device.id, action })
      });
      const j = await r.json();
      if (!j.ok) throw new Error(j.error || 'failed');
      onDone();
    } catch (e:any) {
      alert(e.message || 'Failed');
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="rounded-lg border border-zinc-800 p-4">
      <div className="text-sm font-medium mb-2">Power controls</div>
      <div className="flex gap-2">
        <button onClick={() => send('shutdown')} disabled={!!busy}
                className="px-3 py-2 rounded bg-rose-600 text-white text-sm disabled:opacity-50">
          {busy==='shutdown' ? 'Sending…' : 'Send shutdown'}
        </button>
        <button onClick={() => send('reboot')} disabled={!!busy}
                className="px-3 py-2 rounded bg-amber-600 text-white text-sm disabled:opacity-50">
          {busy==='reboot' ? 'Sending…' : 'Send reboot'}
        </button>
      </div>
      <div className="text-xs text-zinc-400 mt-2">
        Owner receives a 6‑digit code by email to confirm.
      </div>
    </div>
  );
}

