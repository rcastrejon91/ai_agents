export default function ModeBubble({ mode }) {
  return (
    <div className="mode-bubble">
      {mode === "medical" && "🩺 Medical Mode"}
      {mode === "security" && "🛡 Security Mode"}
      {mode === "default" && "💬 Default Mode"}
    </div>
  );
}
