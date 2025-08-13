'use client';
import { useState } from 'react';

export default function ActionConsentCard({ intent, consent }:{ intent:string; consent:any }) {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<any>(null);

  async function approve(){
    setBusy(true);
    try{
      const r = await fetch('/api/actions', {
        method:'POST',
        headers:{'content-type':'application/json'},
        body: JSON.stringify({ intent, params:{ confirm:true } })
      });
      const j = await r.json();
      setResult(j.result || j.error || j);
    }catch(e){
      setResult({ error:'network_error' });
    }finally{
      setBusy(false);
    }
  }

  if(result){
    return (
      <div className="card" style={{margin:'10px 0'}}>
        <div className="text-sm font-medium mb-1">Action Result</div>
        <pre className="text-xs overflow-auto" style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(result, null, 2)}</pre>
      </div>
    );
  }

  return (
    <div className="card" style={{margin:'10px 0'}}>
      <div className="text-sm font-medium mb-1">{consent.title}</div>
      <div className="text-sm mb-2">{consent.summary}</div>
      <ul className="text-xs mb-2" style={{paddingLeft:'20px',listStyle:'disc'}}>
        {consent.steps.map((s:any)=>(<li key={s.id}>{s.preview}</li>))}
      </ul>
      <div className="text-xs mb-2">Est. cost: ${consent.estCostUSD}</div>
      <button className="btn" onClick={approve} disabled={busy}>{busy?'Working…':'Approve'}</button>
    </div>
  );
}
