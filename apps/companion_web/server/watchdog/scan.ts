import crypto from "crypto";

async function tavily(q:string){
  const r = await fetch("https://api.tavily.com/search",{ method:"POST", headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({ api_key: process.env.TAVILY_API_KEY, query:q, include_answer:true, max_results:6 })});
  const j = await r.json(); return (j.results||[]).map((x:any)=>({ title:x.title, url:x.url, snippet:x.snippet||"" }));
}
async function llmSumm(text:string){
  const r = await fetch("https://api.openai.com/v1/chat/completions",{
    method:"POST", headers:{ "Authorization":`Bearer ${process.env.OPENAI_API_KEY}`,"Content-Type":"application/json"},
    body: JSON.stringify({ model:"gpt-4o-mini", temperature:0.1, messages:[
      {role:"system", content:"Classify law updates: output JSON only with keys: domain(therapy_ai|privacy|crisis|ai_disclosure), status(allowed|restricted|prohibited), summary, effective_date(YYYY-MM-DD), sources[{title,url}]}"},
      {role:"user", content:text}
    ]})
  });
  const j = await r.json(); return j.choices?.[0]?.message?.content?.trim() || "{}";
}
export async function scanJurisdiction(jur:string){
  const qs = [
    `site:gov ("artificial intelligence" OR chatbot) mental health law ${jur}`,
    `AI therapy restriction ${jur} 2025`,
    `state licensing board AI counseling ${jur}`
  ];
  const hits = (await Promise.all(qs.map(tavily))).flat();
  const bundle = hits.map(h=>`• ${h.title}\n${h.url}\n${h.snippet}`).join("\n\n");
  const out = await llmSumm(`Items:\n${bundle}\n\nJurisdiction:${jur}`);
  const hash = crypto.createHash("sha256").update(out).digest("hex");
  return { jur, raw: out, hash };
}
