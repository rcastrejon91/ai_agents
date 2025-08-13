'use client';
import { useEffect, useState } from 'react';

export default function HealthDot() {
  const [status, setStatus] = useState<'checking' | 'up' | 'down'>('checking');

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch('/api/selftest');
        const d = await r.json();
        setStatus(d.ok ? 'up' : 'down');
      } catch (err) {
        console.error('Self-test request failed', err);
        setStatus('down');
      }
    })();
  }, []);

  const emoji = status === 'checking' ? '⏳' : status === 'up' ? '✅' : '❌';
  const label = status === 'checking' ? 'Checking' : status === 'up' ? 'Online' : 'Offline';

  return (
    <div className="flex items-center gap-2 text-xs text-zinc-400">
      <span>{emoji}</span>
      <span>{label}</span>
    </div>
  );
}
