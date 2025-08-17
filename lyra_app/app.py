import os
from datetime import datetime

from flask import Flask, jsonify, render_template_string, request

# Import enhanced error handling
from error_handling import (
    error_handler,
    validate_lyra_request,
    rate_limit_check,
    make_request_with_retry,
    ValidationError,
    UpstreamError,
    RateLimitError,
    check_openai_health,
    TIMEOUT_CONFIG,
)

# ====== Config ======
OWNER_NAME = "Ricky"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Lazy import so the app still boots without the key (health page works)
OPENAI = None
if OPENAI_API_KEY:
    from openai import OpenAI
    OPENAI = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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


# ====== Enhanced Health check ======
@app.route("/ping")
@error_handler
def ping():
    """Enhanced health check endpoint."""
    openai_health = check_openai_health()
    
    overall_status = "healthy"
    if openai_health["status"] == "unhealthy":
        overall_status = "unhealthy"
    elif openai_health["status"] == "degraded":
        overall_status = "degraded"
    
    health_data = {
        "status": overall_status,
        "service": "Lyra Flask",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "openai": openai_health,
        },
        "version": "1.0.0",
    }
    
    status_code = 200 if overall_status != "unhealthy" else 503
    response = jsonify(health_data)
    response.status_code = status_code
    return response


# ====== Enhanced Chat endpoint ======
@app.route("/api/lyra", methods=["POST"])
@error_handler
def lyra():
    """Enhanced Lyra chat endpoint with comprehensive error handling."""
    # Check OpenAI configuration
    if OPENAI is None:
        raise UpstreamError(
            "OpenAI not configured", 
            {"detail": "Set OPENAI_API_KEY environment variable"}
        )
    
    # Rate limiting
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    if not rate_limit_check(client_ip, 30):  # 30 requests per minute
        raise RateLimitError("Too many requests. Please try again later.")
    
    # Get and validate request data
    data = request.get_json(silent=True) or {}
    validated_data = validate_lyra_request(data)
    
    message = validated_data["message"]
    history = validated_data["history"]
    
    # System prompt
    system_prompt = (
        "You are Lyra, a warm, supportive AI companion. Keep replies concise, kind, and practical. "
        "No explicit content. Encourage small next steps and reflect user details empathetically. "
        "Limit responses to 500 words or less."
    )
    
    # Prepare messages
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})
    
    try:
        # Call OpenAI with timeout and error handling
        response = OPENAI.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            timeout=TIMEOUT_CONFIG["OPENAI"],
        )
        
        reply = response.choices[0].message.content
        if not reply:
            raise UpstreamError("Empty response from OpenAI API")
        
        return jsonify({
            "reply": reply.strip(),
            "model": "gpt-4o-mini",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": getattr(request, 'request_id', None),
        })
        
    except Exception as e:
        # Convert OpenAI exceptions to our error types
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            raise TimeoutError(f"OpenAI request timed out: {error_msg}")
        elif "rate" in error_msg.lower() and "limit" in error_msg.lower():
            raise RateLimitError(f"OpenAI rate limit exceeded: {error_msg}")
        else:
            raise UpstreamError(f"OpenAI API error: {error_msg}")


# ====== Optional tiny memory demo ======
_MEM = {}


@app.route("/remember", methods=["POST"])
def remember():
    d = request.get_json(silent=True) or {}
    uid, fact = d.get("user_id"), d.get("fact")
    if not uid or not fact:
        return jsonify(error="user_id and fact required"), 400
    _MEM.setdefault(uid, []).append(
        {"fact": fact, "ts": datetime.utcnow().isoformat() + "Z"}
    )
    return jsonify(ok=True, count=len(_MEM[uid]))


@app.route("/memories/<uid>")
def memories(uid):
    return jsonify(memories=_MEM.get(uid, []))


if __name__ == "__main__":
    # Local dev run: python lyra_app/app.py
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
