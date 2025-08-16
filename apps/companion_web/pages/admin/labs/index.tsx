export default function Labs() {
  const trigger = async () => {
    await fetch("/api/learn/pull", { method: "POST" });
    await fetch("/api/learn/process", { method: "POST" });
  };
  return (
    <div>
      <h1>Labs</h1>
      <button
        onClick={trigger}
        className="px-3 py-2 rounded bg-zinc-800 text-sm"
      >
        Learn now
      </button>
    </div>
  );
}
