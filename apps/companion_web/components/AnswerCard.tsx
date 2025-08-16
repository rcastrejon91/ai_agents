"use client";
export function AnswerCard({
  text,
  sources,
  onSpeak,
}: {
  text: string;
  sources: { title: string; url: string }[];
  onSpeak?: () => void;
}) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium">Answer</h3>
        {onSpeak && (
          <button className="btn-ghost text-xs" onClick={onSpeak}>
            🔊 Speak
          </button>
        )}
      </div>
      <div className="prose prose-invert text-zinc-100 max-w-none whitespace-pre-wrap">
        {text}
      </div>
      <div className="mt-3">
        <h4 className="text-xs text-zinc-400 mb-1">Sources</h4>
        <ul className="space-y-1">
          {sources?.map((s, i) => (
            <li key={i} className="text-xs text-zinc-300">
              <span className="badge mr-2">[{i + 1}]</span>
              <a
                className="underline hover:no-underline"
                href={s.url}
                target="_blank"
                rel="noreferrer"
              >
                {s.title}
              </a>
            </li>
          ))}
        </ul>
      </div>
      <div className="mt-3 text-[11px] text-zinc-500">
        Transparent mode: answers include citations and may say “don’t know”
        when info isn’t in sources.
      </div>
    </div>
  );
}
