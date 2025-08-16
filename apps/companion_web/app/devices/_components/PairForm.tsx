"use client";
import { useState } from "react";

export default function PairForm({ onPaired }: { onPaired: () => void }) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("My Device");
  const [model, setModel] = useState("generic");
  const [result, setResult] = useState<{ id: string; secret: string } | null>(
    null,
  );
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    try {
      const r = await fetch("/api/devices/register", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ owner_email: email, public_name: name, model }),
      });
      const j = await r.json();
      if (!j.ok) throw new Error(j.error || "failed");
      setResult({ id: j.id, secret: j.secret });
      onPaired();
    } catch (e: any) {
      alert(e.message || "Failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="rounded-lg border border-zinc-800 p-4 space-y-3">
      <div className="font-medium">Pair new device</div>
      <input
        className="w-full bg-zinc-900 border border-zinc-700 rounded px-3 py-2 text-sm"
        placeholder="Owner email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <div className="grid grid-cols-2 gap-2">
        <input
          className="bg-zinc-900 border border-zinc-700 rounded px-3 py-2 text-sm"
          placeholder="Public name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          className="bg-zinc-900 border border-zinc-700 rounded px-3 py-2 text-sm"
          placeholder="Model (generic)"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        />
      </div>
      <button
        onClick={submit}
        disabled={busy}
        className="px-3 py-2 rounded bg-emerald-600 text-white text-sm disabled:opacity-50"
      >
        {busy ? "Pairing…" : "Pair device"}
      </button>

      {result && (
        <div className="text-xs bg-zinc-900 border border-zinc-800 rounded p-2">
          <div>
            DEVICE_ID: <b>{result.id}</b>
          </div>
          <div>
            DEVICE_SECRET: <b>{result.secret}</b>
          </div>
          <div className="opacity-70 mt-1">
            Save these into your Docker agent env.
          </div>
        </div>
      )}
    </div>
  );
}
