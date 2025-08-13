import type { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';
import { safeFetchJSON, riskGate } from '../../../app/lib/research/utils';

export const config = { api: { bodyParser: false } };

const sb = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!);

async function log(task_id: string, phase: string, payload: any) {
  await sb.from('research_logs').insert({ task_id, phase, payload });
}

async function searchBundle(query: string) {
  // Wiki + arXiv + HN as a minimal trio; Tavily if key exists
  const [wiki, arxiv, hn] = await Promise.all([
    safeFetchJSON(`/api/free/wiki?q=${encodeURIComponent(query)}`),
    safeFetchJSON(`/api/free/arxiv?q=${encodeURIComponent(query)}`).catch(()=>({items:[]})),
    safeFetchJSON(`/api/free/hn`).catch(()=>([])),
  ]);
  return { wiki, arxiv, hn };
}

async function llmSummarize(objective: string, bundle: any) {
  const key = process.env.OPENAI_API_KEY;
  if (!key) {
    const note = `No OPENAI_API_KEY; heuristic summary: ${bundle?.wiki?.title||'—'}`;
    return { summary: note, proposals: [] as any[] };
  }
  const context = [
    `Wiki: ${bundle?.wiki?.summary?.extract || ''}`,
    `arXiv: ${(bundle?.arxiv?.items||[]).map((i:any)=>`${i.title}: ${i.summary}`).join('\n\n')}`,
    `HN: ${(bundle?.hn||[]).slice(0,5).map((i:any)=>i.title).join('; ')}`
  ].join('\n\n');

  const prompt = [
    `Objective: ${objective}`,
    `Given the context below, produce:`,
    `1) A concise research summary (<= 180 words).`,
    `2) Up to 5 safe improvement proposals in JSON: [{type: "prompt|config|code", file?: string, key?: string, value?: any, rationale: string}].`,
    `Only propose "code" if trivial and safe. Prefer "prompt" or "config" changes.`,
    `Context:\n${context}`
  ].join('\n\n');

  const r = await fetch('https://api.openai.com/v1/chat/completions',{
    method:'POST',
    headers:{'content-type':'application/json', authorization:`Bearer ${key}`},
    body: JSON.stringify({ model:'gpt-4o-mini', temperature:0.2, messages:[{role:'user', content:prompt}] })
  });
  const j = await r.json();
  const txt = j?.choices?.[0]?.message?.content || '';
  const propsMatch = txt.match(/\[([\s\S]*?)\]\s*$/); // last JSON array
  let proposals:any[] = [];
  try { proposals = propsMatch ? JSON.parse(propsMatch[0]) : []; } catch {}
  const summary = txt.replace(/\[([\s\S]*?)\]\s*$/,'').trim();
  return { summary, proposals };
}

async function applySafeChanges(task_id: string, proposals: any[]) {
  const applied:any[] = [], openedPRs:any[] = [], skipped:any[] = [];
  for (const p of proposals) {
    const gate = riskGate(JSON.stringify(p));
    if (!gate.allowed) { skipped.push({ p, reason: gate.reason }); continue; }

    if (p.type === 'config' && p.file && p.key) {
      // update a JSON config in repo via PR (safer than direct write in prod)
      const pr = await openPrWithPatch(p.file, async (json:any)=> {
        json[p.key] = p.value;
        return json;
      }, `config: set ${p.key}`);
      openedPRs.push(pr);
    } else if (p.type === 'prompt' && p.file) {
      const pr = await openPrReplaceText(p.file, p.value, `prompt: refresh ${p.file}`);
      openedPRs.push(pr);
    } else {
      skipped.push({ p, reason: 'unsupported or missing fields' });
    }
  }
  await log(task_id,'apply', { applied, openedPRs, skipped });
  return { applied, openedPRs, skipped };
}

async function openPrWithPatch(path:string, patcher:(json:any)=>any, title:string) {
  const gh = (u:string, init:any={}) => fetch(`https://api.github.com${u}`, {
    ...init,
    headers:{
      'authorization': `Bearer ${process.env.GITHUB_TOKEN}`,
      'accept':'application/vnd.github+json',
      ...(init.headers||{})
    }
  });

  const repo = process.env.REPO_FULL_NAME!;
  // read current
  const f = await gh(`/repos/${repo}/contents/${encodeURIComponent(path)}`).then(r=>r.json());
  const content = Buffer.from(f.content, 'base64').toString('utf8');
  const json = JSON.parse(content);
  const updated = patcher(json);
  const branch = `research/${Date.now()}`;
  // create branch from default
  const base = await gh(`/repos/${repo}`).then(r=>r.json());
  const ref = await gh(`/repos/${repo}/git/ref/heads/${base.default_branch}`).then(r=>r.json());
  await gh(`/repos/${repo}/git/refs`, { method:'POST', body: JSON.stringify({ ref:`refs/heads/${branch}`, sha: ref.object.sha }) });
  // commit new file
  await gh(`/repos/${repo}/contents/${encodeURIComponent(path)}?ref=${branch}`, {
    method:'PUT',
    body: JSON.stringify({
      message: title,
      content: Buffer.from(JSON.stringify(updated,null,2)).toString('base64'),
      sha: f.sha,
      branch
    })
  });
  // open PR
  const pr = await gh(`/repos/${repo}/pulls`, {
    method:'POST',
    body: JSON.stringify({ title, head: branch, base: base.default_branch, body: 'Automated proposal via Research Loop (human review required).' })
  }).then(r=>r.json());
  return { number: pr.number, url: pr.html_url };
}

async function openPrReplaceText(path:string, newText:string, title:string) {
  const gh = (u:string, init:any={}) => fetch(`https://api.github.com${u}`, {
    ...init,
    headers:{
      'authorization': `Bearer ${process.env.GITHUB_TOKEN}`,
      'accept':'application/vnd.github+json',
      ...(init.headers||{})
    }
  });

  const repo = process.env.REPO_FULL_NAME!;
  const f = await gh(`/repos/${repo}/contents/${encodeURIComponent(path)}`).then(r=>r.json());
  const content = Buffer.from(f.content, 'base64').toString('utf8');
  const branch = `research/${Date.now()}`;
  const base = await gh(`/repos/${repo}`).then(r=>r.json());
  const ref = await gh(`/repos/${repo}/git/ref/heads/${base.default_branch}`).then(r=>r.json());
  await gh(`/repos/${repo}/git/refs`, { method:'POST', body: JSON.stringify({ ref:`refs/heads/${branch}`, sha: ref.object.sha }) });
  await gh(`/repos/${repo}/contents/${encodeURIComponent(path)}?ref=${branch}`, {
    method:'PUT',
    body: JSON.stringify({
      message: title,
      content: Buffer.from(newText).toString('base64'),
      sha: f.sha,
      branch
    })
  });
  const pr = await gh(`/repos/${repo}/pulls`, {
    method:'POST',
    body: JSON.stringify({ title, head: branch, base: base.default_branch, body: 'Automated proposal via Research Loop (human review required).' })
  }).then(r=>r.json());
  return { number: pr.number, url: pr.html_url };
}

export default async function handler(req:NextApiRequest, res:NextApiResponse) {
  try {
    if (req.headers['x-cron-key'] !== process.env.RESEARCH_CRON_SECRET) return res.status(401).json({ error:'unauthorized' });

    // 1) Pull next task
    const { data: task } = await sb.from('research_tasks').select('*').eq('status','queued').order('priority',{ascending:false}).limit(1).single();
    if (!task) return res.status(200).json({ ok:true, note:'no queued tasks' });

    await sb.from('research_tasks').update({ status:'running', started_at: new Date().toISOString() }).eq('id', task.id);

    // 2) Search bundle
    const bundle = await searchBundle(task.objective);
    await log(task.id, 'search', bundle);

    // 3) Summarize + proposals
    const { summary, proposals } = await llmSummarize(task.objective, bundle);
    await log(task.id, 'synthesize', { summary, proposals });

    // 4) Guardrails
    const gate = riskGate(JSON.stringify({ summary, proposals }));
    if (!gate.allowed) {
      await log(task.id,'guard',{ denied:true, reason: gate.reason });
      await sb.from('research_tasks').update({ status:'failed', finished_at: new Date().toISOString() }).eq('id', task.id);
      return res.status(200).json({ ok:false, reason:'blocked by guardrails' });
    }

    // 5) Apply safe changes (via PRs for code; direct for configs only if trivial—in this sample we PR both)
    const applied = await applySafeChanges(task.id, proposals);

    // 6) Mark done
    await sb.from('research_tasks').update({ status:'done', finished_at: new Date().toISOString() }).eq('id', task.id);

    res.status(200).json({ ok:true, task, summary, proposals, applied });
  } catch(e:any) {
    console.error(e);
    res.status(500).json({ error: e?.message || 'loop_failed' });
  }
}
