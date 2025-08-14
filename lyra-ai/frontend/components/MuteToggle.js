export default function MuteToggle({ muted, onToggle }) {
  return (
    <button type="button" onClick={onToggle}>
      {muted ? 'Unmute' : 'Mute'}
    </button>
  );
}
