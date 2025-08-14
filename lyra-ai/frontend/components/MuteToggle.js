export default function MuteToggle({ muted, setMuted }) {
  return (
    <button type="button" onClick={() => setMuted(!muted)}>
      {muted ? 'Unmute' : 'Mute'}
    </button>
  );
}
