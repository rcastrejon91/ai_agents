'use client';
type Device = { id: string; public_name: string; owner_email: string; model?: string; last_seen?: number };

export default function DeviceList({
  devices, selectedId, onSelect, loading, onRefresh
}: {
  devices: Device[]; selectedId: string | null;
  onSelect: (d: Device) => void;
  loading: boolean; onRefresh: () => void;
}) {
  return (
    <div className="rounded-lg border border-zinc-800">
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <div className="font-medium">Registered devices</div>
        <button onClick={onRefresh} className="text-xs px-2 py-1 rounded bg-zinc-800">Refresh</button>
      </div>
      {loading ? (
        <div className="p-4 text-sm text-zinc-400">Loading…</div>
      ) : devices.length === 0 ? (
        <div className="p-4 text-sm text-zinc-400">No devices yet. Pair one →</div>
      ) : (
        <ul className="divide-y divide-zinc-800">
          {devices.map(d => (
            <li key={d.id}
                className={`px-4 py-3 cursor-pointer ${selectedId===d.id ? 'bg-zinc-900' : ''}`}
                onClick={() => onSelect(d)}>
              <div className="text-sm font-medium">{d.public_name} <span className="text-xs opacity-60">({d.model||'generic'})</span></div>
              <div className="text-xs opacity-70">{d.owner_email}</div>
              {d.last_seen && <div className="text-xs opacity-60">last seen: {new Date(d.last_seen).toLocaleString()}</div>}
              <div className="text-[10px] opacity-50 break-all mt-1">{d.id}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

