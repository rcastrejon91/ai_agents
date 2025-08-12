'use client';
import { useEffect, useState } from 'react';

type Stat = { env:{OPENAI_API_KEY:boolean,DEBUG:boolean}, openai:{ok:boolean, note:string} };

export default function HealthDot(){
  const [s,setS] = useState<Stat|null>(null);
  useEffect(()=>{ fetch('/api/debug/status').then(r=>r.json()).then(setS).catch(()=>{}); },[]);
  const mode = !s ? 'loading'
    : s.env.DEBUG ? 'debug'
    : s.env.OPENAI_API_KEY && s.openai.ok ? 'live'
    : 'demo';
  const color = mode==='live'?'bg-emerald-500':mode==='debug'?'bg-amber-500':mode==='demo'?'bg-sky-500':'bg-zinc-500';
  const label = mode.toUpperCase();
  return (
    <div className="flex items-center gap-2 text-xs text-zinc-400">
      <span className={`h-2.5 w-2.5 rounded-full ${color} shadow`}></span>
      <span>{label}{s?.openai?.note ? ` • ${s.openai.note}`:''}</span>
    </div>
  );
}
