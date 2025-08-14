import os
import datetime
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, session
import io
from gtts import gTTS
import speech_recognition as sr
from functools import wraps
import subprocess
import secrets

# --- CONFIG ---
OWNER_NAME = "Ricky"
OWNER_EMAIL = "ricardomcastrejon@gmail.com"
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))

# --- CORE CLASS ---
class LyraAI:
    def __init__(self):
        self.security_protocols = []
        self.medical_knowledge_base = {}
        self.security_knowledge_base = {}
        self.self_learning_log = []
        self.muted = False
        self.current_mood = "neutral"

    def learn_security(self):
        learned_data = {
            "date": datetime.date.today().isoformat(),
            "new_threats": ["Ransomware variant X", "Zero-day in medical device firmware"],
            "new_protections": ["Firewall AI patch", "Updated encryption protocol"]
        }
        self.security_knowledge_base[learned_data["date"]] = learned_data
        self.security_protocols.extend(learned_data["new_protections"])
        self.log_learning("Security", learned_data)

    def learn_medicine(self):
        learned_data = {
            "date": datetime.date.today().isoformat(),
            "new_studies": ["Breakthrough in cancer immunotherapy", "Faster stroke detection AI"],
            "new_treatments": ["Custom CRISPR gene repair", "AI-assisted MRI diagnosis"]
        }
        self.medical_knowledge_base[learned_data["date"]] = learned_data
        self.log_learning("Medical", learned_data)

    def log_learning(self, category, data):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "category": category,
            "data": data
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
        msg['Subject'] = f"Lyra AI Update – {datetime.date.today().isoformat()}"
        msg['From'] = GMAIL_USER
        msg['To'] = OWNER_EMAIL
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(msg['From'], [msg['To']], msg.as_string())

lyra = LyraAI()

# --- AUTH DECORATOR ---
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("admin_logged_in"):
            return f(*args, **kwargs)
        return redirect(url_for("admin_login"))
    return wrapper

# --- ROUTES ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/speak", methods=["POST"])
def speak():
    text = request.json.get("text", "")
    mood = request.json.get("mood", "neutral")
    tts = gTTS(text=f"[{mood}] {text}", lang="en")
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return send_file(audio_buffer, mimetype="audio/mpeg")

@app.route("/listen", methods=["GET"])
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    try:
        transcript = recognizer.recognize_google(audio)
    except:
        transcript = ""
    return jsonify({"transcript": transcript})

@app.route("/learn", methods=["POST"])
def learn():
    lyra.learn_security()
    lyra.learn_medicine()
    lyra.email_report()
    return jsonify({"status": "Learning complete, email sent"})

@app.route("/daily_report", methods=["GET"])
def daily_report_api():
    report_text = lyra.daily_report()
    try:
        lyra.email_report()
        status = "Report sent via email."
    except Exception as e:
        status = f"Report generated, email failed: {e}"
    return jsonify({"status": status, "report": report_text})

# --- ADMIN PANEL ---
@app.route("/admin", methods=["GET"])
@admin_required
def admin_panel():
    return render_template("admin.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_panel"))
    return render_template("login.html")

@app.route("/admin/terminal", methods=["POST"])
@admin_required
def admin_terminal():
    cmd = request.json.get("command")
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    return jsonify({"output": output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
