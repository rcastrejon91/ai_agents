'use client';
import { useEffect, useState } from 'react';
import { tools } from '@/lib/agent/tools';
import { speak } from '@/lib/speak';

type Step = { id:string; tool:string; args:Record<string,string>; note?:string; result?:any };
type RunReport = { plan: Step[]; outputs: {id:string; ok:boolean; title?:string; text?:string; cite?:string}[]; summary:string };

export default function ActionRunner({ query }:{ query:string }) {
  const [plan,setPlan] = useState<Step[]|null>(null);
  const [out,setOut] = useState<any[]>([]);
  const [running,setRunning] = useState(false);
  const [done,setDone] = useState(false);

  useEffect(()=>{ (async ()=>{
    const r = await fetch('/api/agent/run',{method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({ query })});
    const j:RunReport = await r.json();
    setPlan(j.plan);
  })(); },[query]);

  async function run(){
    if(!plan) return;
    setRunning(true); setOut([]);
    const ctx:any = { plan:{} as any }; // for template fills
    const acc:any[] = [];

    for(const step of plan){
      // Fill arg templates using prior results
      const argsFilled = Object.fromEntries(Object.entries(step.args||{}).map(([k,v])=>[k, String(v).replace(/\{\{([^}]+)\}\}/g,(_,p)=> {
        const parts = p.split('.'); let v:any = { plan: ctx.plan };
        for(const part of parts) v = v?.[part];
        return v ?? '';
      })]));

      const tool = tools[step.tool];
      let res = { ok:false, text:`Unknown tool: ${step.tool}` } as any;
      try { res = tool ? await tool(argsFilled) : res; }
      catch(e:any){ res = { ok:false, text: e?.message||'tool error' }; }

      // Keep in context
      ctx.plan[step.id] = { ...step, result: res, data: (res as any).data };
      acc.push({ id: step.id, ...res });
      setOut([...acc]);
      await new Promise(r=>setTimeout(r, 150)); // tiny pacing
    }
    setRunning(false); setDone(true);

    // quick natural summary (client-side, heuristic)
    const text = acc.map(o=> (o.title?`${o.title}: `:'') + (o.text||'')).join('\n');
    speak(text.slice(0,240)); // speak first chunk
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm font-medium">Action Plan</div>
        <div className="text-xs text-zinc-400">{query}</div>
      </div>
      {!plan && <div className="text-sm text-zinc-400">Planning…</div>}
      {plan && (
        <>
          <ol className="text-sm space-y-2">
            {plan.map(s=>(
              <li key={s.id} className="border border-zinc-800 rounded-lg p-2">
                <div className="flex items-center justify-between">
                  <div><span className="badge mr-2">#{s.id}</span><b>{s.tool}</b> {s.note && <span className="text-zinc-400">— {s.note}</span>}</div>
                </div>
                <div className="text-xs text-zinc-400 mt-1">args: {JSON.stringify(s.args)}</div>
                {out.find(o=>o.id===s.id) && (
                  <div className="mt-2 text-sm">
                    <div className="text-zinc-200">{out.find(o=>o.id===s.id)?.title}</div>
                    <div className="text-zinc-300 whitespace-pre-wrap">{out.find(o=>o.id===s.id)?.text}</div>
                    {out.find(o=>o.id===s.id)?.cite && <a className="text-xs underline text-zinc-400" href={out.find(o=>o.id===s.id)?.cite} target="_blank">source</a>}
                  </div>
                )}
              </li>
            ))}
          </ol>
          <div className="mt-3 flex gap-2">
            <button className="btn" onClick={run} disabled={running}>{running?'Running…':'Run plan'}</button>
            {done && <button className="btn" onClick={()=>{setPlan(null);setOut([]);setDone(false);}}>New plan</button>}
          </div>
        </>
      )}
    </div>
  );
}
