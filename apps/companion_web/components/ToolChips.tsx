'use client';
type Props = { tools?: string[] };

const COLORS: Record<string, string> = {
  Chat: "bg-zinc-800 text-zinc-200",
  Discovery: "bg-indigo-600/20 text-indigo-300 ring-1 ring-indigo-600/40",
  Labs: "bg-amber-600/20 text-amber-300 ring-1 ring-amber-600/40",
  Imaging: "bg-cyan-600/20 text-cyan-300 ring-1 ring-cyan-600/40",
  Ops: "bg-emerald-600/20 text-emerald-300 ring-1 ring-emerald-600/40",
  Forensic: "bg-rose-600/20 text-rose-300 ring-1 ring-rose-600/40",
};

export default function ToolChips({ tools }: Props) {
  if (!tools || tools.length === 0) return null;
  return (
    <div className="mt-1 flex flex-wrap gap-1.5">
      {tools.map((t, i) => (
        <span
          key={i}
          className={`px-2 py-0.5 text-[11px] rounded-full ${COLORS[t] || "bg-zinc-800 text-zinc-200"}`}
        >
          {t}
        </span>
      ))}
    </div>
  );
}

