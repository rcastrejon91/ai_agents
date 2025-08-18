import os
from datetime import datetime

from flask import Flask, jsonify, render_template_string, request

# Import security middleware
from middleware.auth import (
    generate_csrf_token,
    log_security_event,
    rate_limited,
    require_csrf,
    sanitize_input,
    secure_session_config,
)
from middleware.error_handlers import (
    log_request_info,
    register_error_handlers,
    setup_logging,
)

# ====== Config ======
OWNER_NAME = "Ricky"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Lazy import so the app still boots without the key (health page works)
OPENAI = None
if OPENAI_API_KEY:
    from openai import OpenAI

    OPENAI = OpenAI(apiKey=OPENAI_API_KEY)

app = Flask(__name__)

# Configure security settings
secure_session_config(app)

# Register error handlers and logging
register_error_handlers(app)
setup_logging(app)
log_request_info(app)


# Add CSRF token to template context
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token)


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
      <input type="hidden" name="csrf_token" id="csrf_token" value="{{ csrf_token() }}">
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

  // Get CSRF token
  const csrfToken = document.getElementById('csrf_token').value;

  const res = await fetch('/api/lyra', {
    method:'POST',
    headers:{
      'Content-Type':'application/json',
      'X-CSRF-Token': csrfToken
    },
    body: JSON.stringify({ message:text, history })
  });
  const data = await res.json();
  if (data.reply) {
    push('assistant', data.reply);
    history.push({role:'assistant', content:data.reply});
  } else {
    push('assistant', '⚠️ ' + (data.detail || data.error || 'Upstream error'));
  }
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
    return jsonify(
        ok=True,
        service="Lyra Flask",
        time=datetime.utcnow().isoformat() + "Z",
        openai=bool(OPENAI is not None),
    )


# ====== Chat endpoint ======
@app.route("/api/lyra", methods=["POST"])
@require_csrf
@rate_limited(max_requests=20, window_seconds=60)
def lyra():
    if OPENAI is None:
        log_security_event("openai_not_configured", {"endpoint": "/api/lyra"})
        return jsonify(error="OpenAI not configured", detail="Set OPENAI_API_KEY"), 500

    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    history = data.get("history") or []

    # Sanitize input
    msg = sanitize_input(msg, max_length=2000)

    if not msg:
        log_security_event(
            "invalid_input", {"endpoint": "/api/lyra", "reason": "empty_message"}
        )
        return jsonify(error="Missing 'message'"), 400

    # Sanitize history
    sanitized_history = []
    for item in history[-10:]:  # Limit history to last 10 messages
        if isinstance(item, dict) and "role" in item and "content" in item:
            sanitized_history.append(
                {
                    "role": (
                        item["role"]
                        if item["role"] in ["user", "assistant"]
                        else "user"
                    ),
                    "content": sanitize_input(str(item["content"]), max_length=1000),
                }
            )

    system = (
        "You are Lyra, a warm, supportive AI companion. Keep replies concise, kind, and practical. "
        "No explicit content. Encourage small next steps and reflect user details empathetically."
    )

    try:
        r = OPENAI.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}]
            + sanitized_history
            + [{"role": "user", "content": msg}],
        )
        reply = r.choices[0].message.content

        # Log successful interaction
        app.logger.info(f"Successful chat interaction - message length: {len(msg)}")

        return jsonify(reply=reply)
    except Exception as e:
        # Log error without exposing sensitive details
        app.logger.error(f"Chat API error: {str(e)}")
        log_security_event(
            "api_error", {"endpoint": "/api/lyra", "error_type": type(e).__name__}
        )
        return jsonify(error="upstream", detail="Unable to process request"), 500


# ====== Optional tiny memory demo ======
_MEM = {}


@app.route("/remember", methods=["POST"])
@require_csrf
@rate_limited(max_requests=10, window_seconds=60)
def remember():
    d = request.get_json(silent=True) or {}
    uid, fact = d.get("user_id"), d.get("fact")

    # Sanitize inputs
    uid = sanitize_input(str(uid) if uid else "", max_length=100)
    fact = sanitize_input(str(fact) if fact else "", max_length=500)

    if not uid or not fact:
        log_security_event(
            "invalid_input",
            {"endpoint": "/remember", "reason": "missing_required_fields"},
        )
        return jsonify(error="user_id and fact required"), 400

    # Use UTC datetime
    from datetime import datetime, timezone

    _MEM.setdefault(uid, []).append(
        {"fact": fact, "ts": datetime.now(timezone.utc).isoformat()}
    )

    app.logger.info(f"Memory stored for user {uid}")
    return jsonify(ok=True, count=len(_MEM[uid]))


@app.route("/memories/<uid>")
@rate_limited(max_requests=20, window_seconds=60)
def memories(uid):
    # Sanitize user ID
    uid = sanitize_input(str(uid), max_length=100)
    if not uid:
        return jsonify(error="Invalid user ID"), 400

    return jsonify(memories=_MEM.get(uid, []))


if __name__ == "__main__":
    # Local dev run: python lyra_app/app.py
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
