import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

# ====== Config ======
OWNER_NAME = "Ricky"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Lazy import so the app still boots without the key (health page works)
OPENAI = None
if OPENAI_API_KEY:
    from openai import OpenAI
    OPENAI = OpenAI(apiKey=OPENAI_API_KEY)

app = Flask(__name__)

# ====== Minimal in-browser chat UI at "/" ======
HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Lyra Chat</title>
  <style>
    body { background:#0b1220; color:#e6ecff; font-family: Inter, system-ui, sans-serif; margin:0; }
    header { padding:16px 20px; border-bottom:1px solid #1d2742; display:flex; gap:8px; align-items:center; }
    .ok { width:8px; height:8px; border-radius:50%; background:#4ade80; display:inline-block; }
    main { max-width:720px; margin:0 auto; padding:24px; }
    .msg { padding:12px 14px; border-radius:10px; margin:10px 0; max-width:85%; white-space:pre-wrap; }
    .user { background:#1d2742; margin-left:auto; }
    .bot  { background:#10192e; margin-right:auto; }
    form { display:flex; gap:8px; position:sticky; bottom:0; background:#0b1220; padding:12px 0; }
    input, button, textarea { font-size:16px; }
    textarea { flex:1; resize:vertical; min-height:48px; max-height:140px; color:#e6ecff;
      background:#0f172a; border:1px solid #1d2742; border-radius:10px; padding:12px; }
    button { background:#3246ff; color:white; border:none; border-radius:10px; padding:12px 16px; }
    .small { color:#8fa1d8; font-size:12px; }
  </style>
</head>
<body>
  <header>
    <span class="ok" id="health"></span>
    <strong style="margin-left:6px">Lyra</strong>
    <span class="small">— your companion is live</span>
  </header>
  <main>
    <div id="chat"></div>
    <form id="f">
      <textarea id="t" placeholder="Type a message…"></textarea>
      <button type="submit">Send</button>
    </form>
    <p class="small">Tip: this is a demo. No explicit content. Powered by OpenAI.</p>
  </main>
<script>
const chat = document.getElementById('chat');
const t = document.getElementById('t');
const f = document.getElementById('f');

const push = (role, text) => {
  const d = document.createElement('div');
  d.className = 'msg ' + (role === 'user' ? 'user':'bot');
  d.textContent = text;
  chat.appendChild(d);
  window.scrollTo(0, document.body.scrollHeight);
};

const history = [];
f.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = t.value.trim();
  if (!text) return;
  push('user', text);
  history.push({role:'user', content:text});
  t.value = ''; t.focus();

  const res = await fetch('/api/lyra', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ message:text, history })
  });
  const data = await res.json();
  if (data.reply) {
    push('assistant', data.reply);
    history.push({role:'assistant', content:data.reply});
  } else {
    push('assistant', '⚠️ ' + (data.detail || data.error || 'Upstream error'));
  }
});

(async () => {
  try {
    const r = await fetch('/ping');
    const j = await r.json();
    if (!j.ok) document.getElementById('health').style.background = '#f59e0b';
  } catch { document.getElementById('health').style.background = '#ef4444'; }
})();
</script>
</body>
</html>
"""

@app.route("/")
def ui():
    return render_template_string(HTML)

# ====== Health check ======
@app.route("/ping")
def ping():
    return jsonify(ok=True, service="Lyra Flask", time=datetime.utcnow().isoformat()+"Z",
                   openai=bool(OPENAI is not None))

# ====== Chat endpoint ======
@app.route("/api/lyra", methods=["POST"])
def lyra():
    if OPENAI is None:
        return jsonify(error="OpenAI not configured", detail="Set OPENAI_API_KEY"), 500

    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    history = data.get("history") or []
    if not msg:
        return jsonify(error="Missing 'message'"), 400

    system = ("You are Lyra, a warm, supportive AI companion. Keep replies concise, kind, and practical. "
              "No explicit content. Encourage small next steps and reflect user details empathetically.")

    try:
        r = OPENAI.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":system}] + history + [{"role":"user","content":msg}],
        )
        reply = r.choices[0].message.content
        return jsonify(reply=reply)
    except Exception as e:
        return jsonify(error="upstream", detail=str(e)), 500

# ====== Optional tiny memory demo ======
_MEM = {}
@app.route("/remember", methods=["POST"])
def remember():
    d = request.get_json(silent=True) or {}
    uid, fact = d.get("user_id"), d.get("fact")
    if not uid or not fact:
        return jsonify(error="user_id and fact required"), 400
    _MEM.setdefault(uid, []).append({"fact": fact, "ts": datetime.utcnow().isoformat()+"Z"})
    return jsonify(ok=True, count=len(_MEM[uid]))

@app.route("/memories/<uid>")
def memories(uid):
    return jsonify(memories=_MEM.get(uid, []))

if __name__ == "__main__":
    # Local dev run: python lyra_app/app.py
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
