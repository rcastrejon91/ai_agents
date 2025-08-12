export const runtime = 'nodejs';
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const DATA_DIR = process.env.DATA_PATH || '/tmp/data';
function r<T>(f:string, fb:T):T{ try{ return JSON.parse(fs.readFileSync(path.join(DATA_DIR,f),'utf8')); }catch{ return fb; } }
function w(f:string,d:any){ fs.mkdirSync(DATA_DIR,{recursive:true}); fs.writeFileSync(path.join(DATA_DIR,f), JSON.stringify(d,null,2),'utf8'); }

async function fetchClean(url:string){
  const res = await fetch(url, { headers:{'user-agent':'LyraBot/1.0'} });
  if (!res.ok) throw new Error(`fetch ${url} ${res.status}`);
  let html = await res.text();
  const text = html.replace(/<script[\s\S]*?<\/script>/g,'').replace(/<style[\s\S]*?<\/style>/g,'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').slice(0, 8000);
  return text;
}

async function summarize(text:string, url:string){
  const prompt = `Summarize the key ideas (bullets, concise). Extract concrete tips/constraints. Then write 1 actionable suggestion for Lyra or the device fleet.\nSource: ${url}\nText:\n${text}`;
  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method:'POST', headers:{'content-type':'application/json','authorization':`Bearer ${process.env.OPENAI_API_KEY}`},
    body: JSON.stringify({ model: 'gpt-4o-mini', messages:[{role:'user', content: prompt}], temperature: 0.2 })
  }).then(r=>r.json());
  const out = res.choices?.[0]?.message?.content || '';
  return out.slice(0, 4000);
}

export async function POST(){
  const raw = r<any>('learn_raw.json', { items: [] });
  const proc = r<any>('learn_knowledge.json', { entries: [] });
  const seen = new Set(proc.entries.map((e:any)=>e.url));
  const toProc = raw.items.filter((i:any)=>!seen.has(i.url)).slice(0, 8);

  for (const item of toProc) {
    try{
      const txt = await fetchClean(item.url);
      const sum = await summarize(txt, item.url);
      proc.entries.push({ url: item.url, source: item.source, summary: sum, ts: Date.now() });
    }catch(e){}
  }

  proc.entries = proc.entries.slice(-200);
  w('learn_knowledge.json', proc);
  return NextResponse.json({ ok:true, processed: toProc.length, total: proc.entries.length });
}
