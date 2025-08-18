import datetime
from datetime import datetime as dt, timezone
import io
import os
import smtplib
import subprocess
from email.mime.text import MIMEText

import psutil
import speech_recognition as sr
from flask import Flask, jsonify, request, send_file, session

# Import security middleware
from middleware.auth import (
    require_auth, require_csrf, generate_csrf_token, 
    sanitize_input, sanitize_terminal_command, secure_session_config, 
    rate_limited, log_security_event
)
from middleware.error_handlers import register_error_handlers, setup_logging, log_request_info

# --- CONFIG ---
OWNER_NAME = "Ricky"
OWNER_EMAIL = "ricardomcastrejon@gmail.com"
GMAIL_USER = os.getenv("GMAIL_USER", "")  # Set in env vars
GMAIL_PASS = os.getenv("GMAIL_PASS", "")  # Set in env vars
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "supersecret")  # Change this
ADMIN_KEY = os.getenv("LYRA_ADMIN_KEY", "YOUR_SECRET_KEY")

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


# Helper function for admin auth
def check_admin_session():
    """Check if admin is properly authenticated."""
    return session.get('admin_authenticated') == True

# Custom admin auth decorator
def admin_auth_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_admin_session():
            log_security_event('admin_access_denied', {'endpoint': request.endpoint}, 'WARNING')
            if request.is_json:
                return jsonify({'error': 'Admin authentication required'}), 401
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Update require_auth to use admin session
def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_admin_session():
            log_security_event('admin_access_denied', {'endpoint': request.endpoint}, 'WARNING')
            if request.is_json:
                return jsonify({'error': 'Admin authentication required'}), 401
            return jsonify({'error': 'Admin authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin_login", methods=["GET"])
def admin_login():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lyra Admin Login</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; }
            .login-form { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
            button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="login-form">
            <h2>Lyra Admin Login</h2>
            <form method="POST" action="/verify_admin">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <input type="password" name="password" placeholder="Admin Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    """
class LyraAI:
    def __init__(self):
        self.security_protocols = []
        self.medical_knowledge_base = {}
        self.security_knowledge_base = {}
        self.self_learning_log = []
        self.muted = False
        self.current_mood = "neutral"

    def learn_security(self):
        current_date = dt.now(timezone.utc).date().isoformat()
        learned_data = {
            "date": current_date,
            "timestamp": dt.now(timezone.utc).isoformat(),
            "new_threats": [
                "Ransomware variant X",
                "Zero-day in medical device firmware",
            ],
            "new_protections": ["Firewall AI patch", "Updated encryption protocol"],
        }
        self.security_knowledge_base[learned_data["date"]] = learned_data
        self.security_protocols.extend(learned_data["new_protections"])
        self.log_learning("Security", learned_data)

    def learn_medicine(self):
        current_date = dt.now(timezone.utc).date().isoformat()
        learned_data = {
            "date": current_date,
            "timestamp": dt.now(timezone.utc).isoformat(),
            "new_studies": [
                "Breakthrough in cancer immunotherapy",
                "Faster stroke detection AI",
            ],
            "new_treatments": [
                "Custom CRISPR gene repair",
                "AI-assisted MRI diagnosis",
            ],
        }
        self.medical_knowledge_base[learned_data["date"]] = learned_data
        self.log_learning("Medical", learned_data)

    def log_learning(self, category, data):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "category": category,
            "data": data,
        }
        self.self_learning_log.append(entry)

    def daily_report(self):
        report = f"LYRA DAILY REPORT – {datetime.date.today().isoformat()}\n\n"
        if self.security_knowledge_base.get(datetime.date.today().isoformat()):
            sec = self.security_knowledge_base[datetime.date.today().isoformat()]
            report += f"Security Threats: {', '.join(sec['new_threats'])}\n"
            report += f"Protections: {', '.join(sec['new_protections'])}\n\n"
        if self.medical_knowledge_base.get(datetime.date.today().isoformat()):
            med = self.medical_knowledge_base[datetime.date.today().isoformat()]
            report += f"Medical Studies: {', '.join(med['new_studies'])}\n"
            report += f"New Treatments: {', '.join(med['new_treatments'])}\n\n"
        report += f"Self-Learning Entries Today: {len(self.self_learning_log)}\n"
        return report

    def email_report(self):
        msg = MIMEText(self.daily_report())
        msg["Subject"] = f"Lyra AI Update – {datetime.date.today().isoformat()}"
        msg["From"] = GMAIL_USER
        msg["To"] = OWNER_EMAIL

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())


lyra = LyraAI()

# --- ROUTES ---


@app.route("/verify_admin", methods=["POST"])
@require_csrf
@rate_limited(max_requests=5, window_seconds=300)  # Very restrictive rate limiting
def verify_admin():
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json() or {}
        password = data.get("password", "")
    else:
        password = request.form.get("password", "")
    
    password = sanitize_input(str(password), max_length=100)
    
    if not password:
        log_security_event('admin_auth_attempt', {'reason': 'no_password'}, 'WARNING')
        if request.is_json:
            return jsonify({"access": False}), 400
        return redirect(url_for('admin_login'))
    
    if password == ADMIN_PASSWORD:
        session['admin_authenticated'] = True
        session['admin_login_time'] = dt.now(timezone.utc).isoformat()
        log_security_event('admin_auth_success', {'timestamp': session['admin_login_time']}, 'INFO')
        
        if request.is_json:
            return jsonify({"access": True})
        return jsonify({"status": "Login successful", "redirect": "/admin_dashboard"})
    else:
        log_security_event('admin_auth_failed', {'password_hash': hash(password)}, 'WARNING')
        if request.is_json:
            return jsonify({"access": False}), 401
        return redirect(url_for('admin_login'))


@app.route("/learn", methods=["POST"])
@require_auth
@require_csrf
@rate_limited(max_requests=3, window_seconds=3600)  # Max 3 per hour
def learn():
    try:
        log_security_event('learning_initiated', {'user': 'admin'}, 'INFO')
        lyra.learn_security()
        lyra.learn_medicine()
        lyra.email_report()
        return jsonify({"status": "Learning complete, email sent"})
    except Exception as e:
        app.logger.error(f"Learning process failed: {str(e)}")
        return jsonify({"error": "Learning process failed"}), 500


@app.route("/daily_report", methods=["GET"])
@require_auth
@rate_limited(max_requests=10, window_seconds=3600)
def daily_report_api():
    try:
        report_text = lyra.daily_report()
        return jsonify({"report": report_text})
    except Exception as e:
        app.logger.error(f"Report generation failed: {str(e)}")
        return jsonify({"error": "Report generation failed"}), 500
    report_text = lyra.daily_report()
    try:
        msg = MIMEText(report_text)
        msg["Subject"] = f"Lyra AI Update – {datetime.date.today().isoformat()}"
        msg["From"] = GMAIL_USER
        msg["To"] = OWNER_EMAIL

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        status = "Report sent via email."
    except Exception as e:
        status = f"Email failed: {e}"

    return jsonify({"status": status, "report": report_text})


@app.route("/speak", methods=["POST"])
@require_auth
@require_csrf
@rate_limited(max_requests=20, window_seconds=60)
def speak():
    data = request.get_json() or {}
    text = sanitize_input(str(data.get("text", "")), max_length=500)
    mood = sanitize_input(str(data.get("mood", "neutral")), max_length=50)
    
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    try:
        from gtts import gTTS
        tts = gTTS(text=f"[{mood}] {text}", lang="en")
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return send_file(audio_buffer, mimetype="audio/mpeg")
    except Exception as e:
        app.logger.error(f"TTS failed: {str(e)}")
        return jsonify({"error": "Text-to-speech failed"}), 500


@app.route("/listen", methods=["GET"])
@require_auth
@rate_limited(max_requests=10, window_seconds=60)
def listen():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source, timeout=5)
        transcript = recognizer.recognize_google(audio)
        transcript = sanitize_input(transcript, max_length=1000)
    except Exception as e:
        app.logger.warning(f"Speech recognition failed: {str(e)}")
        transcript = ""
    return jsonify({"transcript": transcript})


@app.route("/terminal", methods=["POST"])
@require_auth
@require_csrf
@rate_limited(max_requests=5, window_seconds=300)  # Very restrictive
def terminal():
    # Double authentication check
    key = request.headers.get("Admin-Key") or ""
    if key != ADMIN_KEY:
        log_security_event('terminal_unauthorized', {'ip': request.environ.get('REMOTE_ADDR')}, 'CRITICAL')
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or {}
    cmd = str(data.get("command", "")).strip()
    
    if not cmd:
        return jsonify({"error": "Command is required"}), 400
    
    try:
        # Sanitize the command with strict validation
        sanitized_cmd = sanitize_terminal_command(cmd)
        
        log_security_event('terminal_command', {
            'command': sanitized_cmd, 
            'original_length': len(cmd),
            'sanitized_length': len(sanitized_cmd)
        }, 'WARNING')
        
        result = subprocess.check_output(
            sanitized_cmd, shell=True, stderr=subprocess.STDOUT, 
            text=True, timeout=10
        )
        
        # Sanitize output before returning
        result = sanitize_input(result, max_length=5000)
        
    except ValueError as e:
        # Command was blocked by sanitization
        log_security_event('terminal_blocked', {'command': cmd, 'reason': str(e)}, 'CRITICAL')
        return jsonify({"error": f"Command not allowed: {str(e)}"}), 403
    except subprocess.CalledProcessError as e:
        result = sanitize_input(str(e.output), max_length=5000)
    except subprocess.TimeoutExpired:
        log_security_event('terminal_timeout', {'command': sanitized_cmd}, 'WARNING')
        result = "Command timed out"
    except Exception as e:
        app.logger.error(f"Terminal command failed: {str(e)}")
        result = "Command execution failed"
    
    return jsonify({"output": result})


@app.route("/system_stats")
@require_auth
@rate_limited(max_requests=30, window_seconds=60)
def system_stats():
    try:
        stats = {
            "cpu": psutil.cpu_percent(interval=0.5),
            "memory": psutil.virtual_memory().percent,
            "timestamp": dt.now(timezone.utc).isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        app.logger.error(f"System stats failed: {str(e)}")
        return jsonify({"error": "Unable to retrieve system stats"}), 500


if __name__ == "__main__":
    lyra.learn_security()
    lyra.learn_medicine()
    lyra.email_report()
    app.run(host="0.0.0.0", port=5000)
