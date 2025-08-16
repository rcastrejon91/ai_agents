"use client";
import { useEffect, useState } from "react";
export default function AdminToggle() {
  const [state, setState] = useState<any>(null);
  const [pin, setPin] = useState("");
  async function load() {
    const r = await fetch("/api/admin/mode");
    setState(await r.json());
  }
  useEffect(() => {
    load();
  }, []);
  async function flip(on: boolean) {
    const r = await fetch("/api/admin/mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin, admin: on }),
    });
    setState(await r.json());
  }
  async function setPersona(p: string) {
    const r = await fetch("/api/admin/mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin, personality: p }),
    });
    setState(await r.json());
  }
  if (!state) return null;
  return (
    <div className="rounded border border-zinc-800 p-3">
      <div className="mb-2 text-sm">
        Admin Mode: <b>{state.admin ? "ON" : "OFF"}</b>
      </div>
      <input
        className="input mb-2"
        placeholder="Enter Admin PIN"
        value={pin}
        onChange={(e) => setPin(e.target.value)}
      />
      <div className="flex gap-2">
        <button className="btn" onClick={() => flip(true)}>
          Enable
        </button>
        <button className="btn" onClick={() => flip(false)}>
          Disable
        </button>
      </div>
      <div className="mt-3 text-sm">Personality:</div>
      <div className="flex flex-wrap gap-2 mt-1">
        {["chill", "sassy", "sage", "gremlin", "guardian", "gamer"].map((p) => (
          <button
            key={p}
            className={`btn ${state.personality === p ? "ring-2 ring-emerald-500" : ""}`}
            onClick={() => setPersona(p)}
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  );
}
