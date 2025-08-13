'use client';
import { useEffect, useState } from "react";

type Robot = {
  id:string; type:string; pose:{x:number;y:number;zone:string};
  battery:number; status:string; health:{motors:string;cpu:string;tempC:number};
  lastSeen:number;
};

export default function AdminHealthPanel() {
  const [robots, setRobots] = useState<Robot[]>([]);
  const [log, setLog] = useState<string[]>([]);

  async function refresh() {
    // fetch two known robots
    const ids = ["RTU-1", "IVU-1"];
    const rs: Robot[] = [];
    for (const id of ids) {
      let j: any = null;
      try {
        j = await fetch(`/api/robots/${id}/health`).then(r => r.json());
      } catch (err) {
        console.error('Failed to fetch robot health', err);
        j = null;
      }
      if (j?.robot) rs.push(j.robot);
    }
    setRobots(rs);
  }

  async function dispatchRunner() {
    const r = await fetch("/api/ops/task", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ type:"runner.deliver", to:"RAD-3", payload:{ item:"lab_kit", priority:"urgent" } })
    }).then(r=>r.json());
    setLog(l=>[`Dispatched: ${JSON.stringify(r?.task||r)}`, ...l].slice(0,20));
    refresh();
  }

  async function selfTest(id:string) {
    const j = await fetch(`/api/robots/${id}/selftest`).then(r=>r.json());
    setLog(l=>[`Selftest ${id}: ${JSON.stringify(j)}`, ...l].slice(0,20));
    refresh();
  }

  useEffect(()=>{ refresh(); const t=setInterval(refresh, 1500); return ()=>clearInterval(t); }, []);

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Lyra Ops Console</h2>
        <button onClick={dispatchRunner} className="px-3 py-1 rounded bg-indigo-600 text-white">Dispatch Runner → RAD-3</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {robots.map(r=>(
          <div key={r.id} className="rounded border border-zinc-800 p-3">
            <div className="flex items-center justify-between">
              <div className="font-medium">{r.id} • {r.type}</div>
              <div className={`text-xs ${r.status==="error"?"text-rose-400":"text-emerald-400"}`}>{r.status}</div>
            </div>
            <div className="text-sm text-zinc-400">
              Zone <b>{r.pose.zone}</b> • Pos ({r.pose.x.toFixed(1)},{r.pose.y.toFixed(1)})<br/>
              Battery <b>{r.battery.toFixed(0)}%</b> • Temp <b>{r.health.tempC.toFixed(1)}°C</b>
            </div>
            <div className="mt-2 flex gap-2">
              <button onClick={()=>selfTest(r.id)} className="px-2 py-1 rounded border border-zinc-700 text-xs">Self-test</button>
              <button onClick={()=>fetch(`/api/robots/${r.id}/command`, {
                method:"POST", headers:{ "Content-Type":"application/json" },
                body: JSON.stringify({ cmd:"goto", args:{ waypoint:"LOBBY" }})
              })} className="px-2 py-1 rounded border border-zinc-700 text-xs">Send → LOBBY</button>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded border border-zinc-800 p-3">
        <div className="text-sm text-zinc-400 mb-1">Event log</div>
        <ul className="text-xs space-y-1 max-h-44 overflow-auto">
          {log.map((line,i)=>(<li key={i} className="text-zinc-500">• {line}</li>))}
        </ul>
      </div>
    </div>
  );
}
