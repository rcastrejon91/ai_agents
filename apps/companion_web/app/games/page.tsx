'use client';
import ModuleBattle from './_components/ModuleBattle';
import { useEffect, useState } from 'react';

function TwitchPanel() {
  const [st, setSt] = useState<any>(null);

  useEffect(() => {
    const tick = async () => {
      const r = await fetch('/api/streams/status', { cache: 'no-store' });
      setSt(await r.json());
    };
    tick();
    const id = setInterval(tick, 15000);
    return () => clearInterval(id);
  }, []);

  if (!st) return <div className="text-xs text-zinc-500">Checking Twitch…</div>;

  if (!st.connected) {
    return (
      <div className="rounded border border-zinc-800 p-3">
        <div className="mb-2 text-sm">Link your Twitch to auto‑embed streams.</div>
        <a className="btn" href="/api/auth/twitch/start">Connect Twitch</a>
      </div>
    );
  }

  return (
    <div className="rounded border border-zinc-800 p-3">
      <div className="text-sm mb-2">
        Connected as <b>{st.login}</b> — {st.live ? 'Live now' : 'Offline'}
      </div>
      {st.live && (
        <div className="aspect-video border border-zinc-800 rounded overflow-hidden">
          <iframe
            src={`https://player.twitch.tv/?channel=${st.login}&parent=${process.env.NEXT_PUBLIC_APP_DOMAIN}`}
            allowFullScreen
            frameBorder="0"
            width="100%"
            height="100%"
          />
        </div>
      )}
    </div>
  );
}

export default function GamesPage() {
  return (
    <div className="p-4 text-zinc-200">
      {/* Game canvas */}
      <div className="mt-4">
        <ModuleBattle />
      </div>

      {/* Streaming links/status */}
      <div className="mt-6">
        <TwitchPanel />
      </div>

      <div className="mt-6 text-xs text-zinc-400">
        Consoles (PS4/5, Xbox):
        Use your console’s Share / Go Live to stream to Twitch or YouTube. After you connect here, we auto‑detect when you go live and embed your stream in the Games tab. No console passwords are ever requested.
      </div>
    </div>
  );
}
