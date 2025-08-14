export default function MuteToggle({ muted, setMuted }) {
  return (
    <button className="mute-toggle" onClick={() => setMuted(!muted)}>
      {muted ? "🔇" : "🔊"}
    </button>
  );
}
