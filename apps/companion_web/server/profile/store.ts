import fs from "fs"; import path from "path";
const FILE = path.join(process.cwd(), ".data_profiles.json");
type Row = { userId: string; jurisdiction?: string };
function load(): Row[]{ try{return JSON.parse(fs.readFileSync(FILE,"utf8"));}catch{return[];} }
function save(a: Row[]){ fs.writeFileSync(FILE, JSON.stringify(a,null,2)); }
export function setJur(userId: string, jurisdiction: string){
  const a = load(); const i = a.findIndex(x=>x.userId===userId);
  if (i>=0) a[i].jurisdiction = jurisdiction; else a.unshift({ userId, jurisdiction });
  save(a); return a[i>=0?i:0];
}
export function getJur(userId: string): string | undefined {
  const a = load(); return a.find(x=>x.userId===userId)?.jurisdiction;
}
