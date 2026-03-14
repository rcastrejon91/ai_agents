# app.py

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

# ✨ NEW: Import Lyra Orchestrator
from core.lyra_orchestrator import LyraOrchestrator
import asyncio

# ====== Config ======
OWNER_NAME = "Ricky"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Lazy import so the app still boots without the key (health page works)
OPENAI = None
if OPENAI_API_KEY:
    from openai import OpenAI
    OPENAI = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Configure security settings
secure_session_config(app)

# Register error handlers and logging
register_error_handlers(app)
setup_logging(app)
log_request_info(app)

# ✨ NEW: Initialize Lyra with multi-perspective intelligence
print("🧠 Initializing Lyra Orchestrator...")
lyra = LyraOrchestrator(config={
    "perspective_weights": {
        "Pragmatist": 0.20,
        "Visionary": 0.15,
        "Analyst": 0.20,
        "Creator": 0.15,
        "Rebel": 0.15,
        "Empath": 0.15
    },
    "owner_name": OWNER_NAME
})
print("✅ Lyra ready with 6-perspective intelligence")


# Add CSRF token to template context
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token)


# ====== Enhanced UI with Lyra branding ======
HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>🧠 Lyra - Multi-Perspective AI</title>
  <style>
    body { background:#0b1220; color:#e6ecff; font-family: Inter, system-ui, sans-serif; margin:0; }
    header { 
      padding:16px 20px; 
      border-bottom:1px solid #1d2742; 
      display:flex; 
      gap:8px; 
      align-items:center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .ok { width:8px; height:8px; border-radius:50%; background:#4ade80; display:inline-block; }
    .perspectives {
      display: flex;
      gap: 4px;
      margin-left: auto;
      font-size: 11px;
      opacity: 0.8;
    }
    .perspective-badge {
      background: rgba(255,255,255,0.2);
      padding: 4px 8px;
      border-radius: 12px;
    }
    main { max-width:720px; margin:0 auto; padding:24px; }
    .msg { padding:12px 14px; border-radius:10px; margin:10px 0; max-width:85%; white-space:pre-wrap; }
    .user { background:#1d2742; margin-left:auto; }
    .bot  { 
      background:#10192e; 
      margin-right:auto;
      border-left: 3px solid #667eea;
    }
    .thinking {
      background: #10192e;
      padding: 8px 12px;
      border-radius: 8px;
      margin: 10px 0;
      font-size: 12px;
      color: #8fa1d8;
      font-style: italic;
    }
    form { display:flex; gap:8px; position:sticky; bottom:0; background:#0b1220; padding:12px 0; }
    input, button, textarea { font-size:16px; }
    textarea { 
      flex:1; 
      resize:vertical; 
      min-height:48px; 
      max-height:140px; 
      color:#e6ecff;
      background:#0f172a; 
      border:1px solid #1d2742; 
      border-radius:10px; 
      padding:12px; 
    }
    button { 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color:white; 
      border:none; 
      border-radius:10px; 
      padding:12px 16px;
      cursor: pointer;
      font-weight: 600;
    }
    button:hover { opacity: 0.9; }
    .small { color:#8fa1d8; font-size:12px; }
    .mode-indicator {
      background: rgba(102, 126, 234, 0.2);
      padding: 8px 12px;
      border-radius: 8px;
      margin-bottom: 16px;
      font-size: 13px;
      border-left: 3px solid #667eea;
    }
  </style>
</head>
<body>
  <header>
    <span class="ok" id="health"></span>
    <strong style="margin-left:6px">🧠 Lyra</strong>
    <span class="small">— Multi-Perspective AI</span>
    <div class="perspectives">
      <span class="perspective-badge" title="Pragmatist">🎯</span>
      <span class="perspective-badge" title="Visionary">🚀</span>
      <span class="perspective-badge" title="Analyst">📊</span>
      <span class="perspective-badge" title="Creator">🎨</span>
      <span class="perspective-badge" title="Rebel">⚡</span>
      <span class="perspective-badge" title="Empath">💚</span>
    </div>
  </header>
  <main>
    <div class="mode-indicator">
      💭 <strong>Multi-Perspective Mode Active</strong> — Every response is synthesized from 6 different perspectives
    </div>
    <div id="chat"></div>
    <form id="f">
      <input type="hidden" name="csrf_token" id="csrf_token" value="{{ csrf_token() }}">
      <textarea id="t" placeholder="Ask me anything... I'll consider it from multiple angles"></textarea>
      <button type="submit">Send</button>
    </form>
    <p class="small">🧠 Powered by Lyra's multi-perspective intelligence + OpenAI</p>
  </main>
<script>
const chat = document.getElementById('chat');
const t = document.getElementById('t');
const f = document.getElementById('f');

const push = (role, text, metadata) => {
  const d = document.createElement('div');
  d.className = 'msg ' + (role === 'user' ? 'user':'bot');
  d.textContent = text;
  
  // Add metadata if available
  if (metadata && role === 'assistant') {
    const meta = document.createElement('div');
    meta.className = 'small';
    meta.style.marginTop = '8px';
    meta.style.opacity = '0.7';
    meta.innerHTML = `
      ${metadata.dominant_perspective ? `<strong>Lead:</strong> ${metadata.dominant_perspective}` : ''}
      ${metadata.intent ? ` | <strong>Intent:</strong> ${metadata.intent}` : ''}
    `;
    d.appendChild(meta);
  }
  
  chat.appendChild(d);
  window.scrollTo(0, document.body.scrollHeight);
};

const showThinking = () => {
  const d = document.createElement('div');
  d.className = 'thinking';
  d.id = 'thinking';
  d.textContent = '💭 Consulting all perspectives...';
  chat.appendChild(d);
  window.scrollTo(0, document.body.scrollHeight);
};

const hideThinking = () => {
  const el = document.getElementById('thinking');
  if (el) el.remove();
};

const history = [];
f.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = t.value.trim();
  if (!text) return;
  
  push('user', text);
  history.push({role:'user', content:text});
  t.value = ''; 
  t.focus();

  showThinking();

  // Get CSRF token
  const csrfToken = document.getElementById('csrf_token').value;

  try {
    const res = await fetch('/api/lyra', {
      method:'POST',
      headers:{
        'Content-Type':'application/json',
        'X-CSRF-Token': csrfToken
      },
      body: JSON.stringify({ message:text, history })
    });
    
    hideThinking();
    
    const data = await res.json();
    if (data.reply) {
      push('assistant', data.reply, data.lyra_metadata);
      history.push({role:'assistant', content:data.reply});
    } else {
      push('assistant', '⚠️ ' + (data.detail || data.error || 'Upstream error'));
    }
  } catch (err) {
    hideThinking();
    push('assistant', '⚠️ Network error. Please try again.');
  }
});

(async () => {
  try {
    const r = await fetch('/ping');
    const j = await r.json();
    if (!j.ok) document.getElementById('health').style.background = '#f59e0b';
  } catch { 
    document.getElementById('health').style.background = '#ef4444'; 
  }
})();
</script>
</body>
</html>
"""


@app.route("/")
def ui():
    return render_template_string(HTML)


# ====== Health check (enhanced with Lyra status) ======
@app.route("/ping")
def ping():
    lyra_status = lyra.get_status()
    return jsonify(
        ok=True,
        service="Lyra Flask + Multi-Perspective AI",
        time=datetime.utcnow().isoformat() + "Z",
        openai=bool(OPENAI is not None),
        lyra={
            "active": True,
            "perspectives": len(lyra_status["perspectives"]),
            "interactions": lyra_status["interactions_processed"]
        }
    )


# ====== Enhanced Chat endpoint with Lyra orchestration ======
@app.route("/api/lyra", methods=["POST"])
@require_csrf
@rate_limited(max_requests=20, window_seconds=60)
def lyra_chat():
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

    try:
        # ✨ NEW: Run Lyra's multi-perspective analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        lyra_analysis = loop.run_until_complete(
            lyra.process(msg, context={"history": sanitized_history})
        )
        loop.close()

        # Build enhanced system prompt based on Lyra's analysis
        system = (
            f"You are Lyra, a warm, supportive AI companion with multi-perspective intelligence. "
            f"Keep replies concise, kind, and practical. No explicit content. "
            f"\n\n"
            f"🧠 INTERNAL ANALYSIS:\n"
            f"Intent: {lyra_analysis.get('intent', 'general')}\n"
            f"Approach: {lyra_analysis.get('approach', 'balanced')}\n"
            f"Lead Perspective: {lyra_analysis.get('dominant_perspective', 'Balanced')}\n"
            f"\n"
            f"Synthesize your response considering all perspectives while leading with {lyra_analysis.get('dominant_perspective', 'balance')}. "
            f"Encourage small next steps and reflect user details empathetically."
        )

        # Call OpenAI with enhanced context
        r = OPENAI.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}]
            + sanitized_history
            + [{"role": "user", "content": msg}],
        )
        reply = r.choices[0].message.content

        # Log successful interaction
        app.logger.info(
            f"Successful chat interaction - message length: {len(msg)}, "
            f"intent: {lyra_analysis.get('intent')}, "
            f"dominant: {lyra_analysis.get('dominant_perspective')}"
        )

        return jsonify(
            reply=reply,
            lyra_metadata={
                "intent": lyra_analysis.get("intent"),
                "dominant_perspective": lyra_analysis.get("dominant_perspective"),
                "confidence": lyra_analysis.get("confidence"),
                "approach": lyra_analysis.get("approach")
            }
        )
        
    except Exception as e:
        # Log error without exposing sensitive details
        app.logger.error(f"Chat API error: {str(e)}")
        log_security_event(
            "api_error", {"endpoint": "/api/lyra", "error_type": type(e).__name__}
        )
        return jsonify(error="upstream", detail="Unable to process request"), 500


# ✨ NEW: Lyra status endpoint
@app.route("/api/lyra/status")
def lyra_status():
    """Get Lyra's current multi-perspective status"""
    status = lyra.get_status()
    return jsonify(status)


# ✨ NEW: Adjust perspective weights
@app.route("/api/lyra/perspectives", methods=["POST"])
@require_csrf
@rate_limited(max_requests=5, window_seconds=60)
def adjust_perspectives():
    """Adjust Lyra's perspective weights"""
    data = request.get_json(silent=True) or {}
    
    perspective = sanitize_input(data.get("perspective", ""), max_length=50)
    adjustment = float(data.get("adjustment", 0))
    
    if not perspective or abs(adjustment) > 0.2:
        return jsonify(error="Invalid perspective or adjustment"), 400
    
    try:
        lyra.adjust_perspective_weights({
            "perspective": perspective,
            "adjustment": adjustment
        })
        
        app.logger.info(f"Perspective adjusted: {perspective} by {adjustment}")
        
        return jsonify(
            ok=True,
            message=f"Adjusted {perspective} by {adjustment}",
            new_weights=lyra.perspective_weights
        )
    except Exception as e:
        app.logger.error(f"Perspective adjustment error: {str(e)}")
        return jsonify(error="Failed to adjust perspective"), 500


# ====== Memory endpoints (keep your existing ones) ======
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

    from datetime import datetime, timezone

    _MEM.setdefault(uid, []).append(
        {"fact": fact, "ts": datetime.now(timezone.utc).isoformat()}
    )

    app.logger.info(f"Memory stored for user {uid}")
    return jsonify(ok=True, count=len(_MEM[uid]))


@app.route("/memories/<uid>")
@rate_limited(max_requests=20, window_seconds=60)
def memories(uid):
    uid = sanitize_input(str(uid), max_length=100)
    if not uid:
        return jsonify(error="Invalid user ID"), 400

    return jsonify(memories=_MEM.get(uid, []))


if __name__ == "__main__":
    # Local dev run: python app.py
    port = int(os.getenv("PORT", "8080"))
    print(f"\n{'='*60}")
    print(f"🧠 LYRA AI - Multi-Perspective Orchestrator")
    print(f"{'='*60}")
    print(f"🚀 Server starting on port {port}")
    print(f"💭 6 perspectives active: Pragmatist, Visionary, Analyst, Creator, Rebel, Empath")
    print(f"🔒 Security middleware: Active")
    print(f"📡 API: http://localhost:{port}")
    print(f"{'='*60}\n")
    
    app.run(host="0.0.0.0", port=port, debug=True)
