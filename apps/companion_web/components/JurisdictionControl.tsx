import { useState } from "react";

export default function JurisdictionControl({ userId }:{ userId:string }){
  const [jur, setJur] = useState("");
  async function save(){
    if(!jur) return;
    await fetch("/api/profile/jurisdiction",{
      method:"POST",
      headers:{ "Content-Type":"application/json", "x-user-id": userId },
      body: JSON.stringify({ jurisdiction: jur })
    });
    alert("Region saved. Compliance rules updated.");
    location.reload();
  }
  return (
    <div style={{marginTop:12}}>
      <div style={{fontSize:12, opacity:.8}}>Region (for legal compliance)</div>
      <input placeholder="e.g. US-IL" value={jur} onChange={e=>setJur(e.target.value)} />
      <button onClick={save} style={{marginLeft:8}}>Save</button>
      <div style={{fontSize:12, opacity:.6, marginTop:4}}>
        Auto-detected from your IP on Vercel. You can override if needed.
      </div>
    </div>
  );
}
