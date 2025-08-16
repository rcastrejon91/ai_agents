import { useEffect, useState } from "react";

type Item = {
  id: string;
  rel: string;
  confidence: number;
  src_name: string;
  src_kind: string;
  dst_name: string;
  dst_kind: string;
  ev_name?: string;
  ev_url?: string;
};

export default function CuratePage() {
  const [items, setItems] = useState<Item[]>([]);
  const [token, setToken] = useState<string>("");

  async function load() {
    const r = await fetch("/api/med/curate/list", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const j = await r.json();
    setItems(j.items ?? []);
  }
  useEffect(() => {
    if (token) load();
  }, [token]);

  async function act(id: string, path: "approve" | "reject") {
    await fetch(`/api/med/curate/${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ id }),
    });
    await load();
  }

  return (
    <div className="max-w-3xl mx-auto p-6 text-zinc-100">
      <h1 className="text-2xl font-semibold mb-2">
        Knowledge Graph — Curation
      </h1>
      <p className="mb-4 text-sm text-zinc-400">
        Paste admin token to manage pending relations.
      </p>
      <input
        className="w-full mb-4 bg-zinc-800 border border-zinc-700 rounded px-3 py-2"
        placeholder="Admin token"
        value={token}
        onChange={(e) => setToken(e.target.value)}
      />
      <button
        onClick={load}
        className="mb-6 px-3 py-2 rounded bg-sky-600 hover:bg-sky-500"
      >
        Refresh
      </button>
      <div className="space-y-3">
        {items.map((it) => (
          <div key={it.id} className="rounded border border-zinc-700 p-3">
            <div className="text-sm">
              <b>{it.src_kind}</b>: {it.src_name}
              <span className="mx-2">
                — <i className="text-sky-400">{it.rel}</i> (
                {it.confidence.toFixed(2)}) —
              </span>
              <b>{it.dst_kind}</b>: {it.dst_name}
            </div>
            {it.ev_url && (
              <a
                className="text-xs text-sky-400"
                href={it.ev_url}
                target="_blank"
                rel="noreferrer"
              >
                evidence
              </a>
            )}
            <div className="mt-2 space-x-2">
              <button
                onClick={() => act(it.id, "approve")}
                className="px-2 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-sm"
              >
                Approve
              </button>
              <button
                onClick={() => act(it.id, "reject")}
                className="px-2 py-1 rounded bg-rose-600 hover:bg-rose-500 text-sm"
              >
                Reject
              </button>
            </div>
          </div>
        ))}
        {!items.length && (
          <div className="text-zinc-400 text-sm">No pending edges.</div>
        )}
      </div>
    </div>
  );
}
