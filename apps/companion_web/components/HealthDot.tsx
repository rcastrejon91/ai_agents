'use client';
import { useEffect, useState } from 'react';

export default function HealthDot() {
  const [status, setStatus] = useState<'checking' | 'up' | 'down'>('checking');

  useEffect(() => {
    fetch('/api/selftest')
      .then(r => r.json())
      .then(d => setStatus(d.ok ? 'up' : 'down'))
      .catch(() => setStatus('down'));
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
