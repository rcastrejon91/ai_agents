import fs from "fs"; import path from "path";
const FILE = path.join(process.cwd(), ".data_reg_rules.json");
type RuleRec = { jur:string; domain:string; status:string; summary:string; sources:any[]; effective_date?:string; hash:string; ts:string };
function load():RuleRec[]{ try{return JSON.parse(fs.readFileSync(FILE,"utf8"));}catch{return[];} }
function save(a:RuleRec[]){ fs.writeFileSync(FILE, JSON.stringify(a,null,2)); }
export function put(rec:RuleRec){ const a=load(); const i=a.findIndex(x=>x.jur===rec.jur && x.domain===rec.domain); if(i>=0) a[i]=rec; else a.unshift(rec); save(a); }
export function all(){ return load().slice(0,500); }
