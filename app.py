import os
import datetime
import smtplib
import sqlite3
import subprocess
import secrets
import io
from email.mime.text import MIMEText
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from gtts import gTTS
import speech_recognition as sr

# ==== CONFIG ====
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(16))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
OWNER_NAME = "Ricky"
OWNER_EMAIL = "ricardomcastrejon@gmail.com"

# ==== APP INIT ====
app = Flask(__name__)
app.secret_key = SECRET_KEY

# ==== DB INIT ====
def init_db():
    conn = sqlite3.connect("lyra.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )''')
    conn.commit()
    conn.close()
init_db()

# ==== LLM SELECTOR ====
def select_llm(prompt):
    """
    Chooses the best LLM available.
    Checks env vars for premium keys, else falls back to free APIs/local models.
    """
    if os.getenv("OPENAI_API_KEY"):
        return f"[GPT-4 RESPONSE to: {prompt}]"
    elif os.getenv("ANTHROPIC_API_KEY"):
        return f"[Claude RESPONSE to: {prompt}]"
    else:
        return f"[Local/Free LLM RESPONSE to: {prompt}]"

# ==== LYRA CORE ====
class LyraAI:
    def __init__(self):
        self.self_learning_log = []

    def learn(self):
        insights = {
            "insights": ["Identified common requests", "Improved LLM routing"],
            "actions": ["Optimized speed", "Updated responses"]
        }
        self.self_learning_log.append(insights)

    def daily_report(self):
        return f"LYRA DAILY REPORT – {datetime.date.today().isoformat()}"

    def email_report(self):
        msg = MIMEText(self.daily_report())
        msg['Subject'] = "Lyra AI Daily Update"
        msg['From'] = GMAIL_USER
        msg['To'] = OWNER_EMAIL
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(msg['From'], [msg['To']], msg.as_string())

lyra = LyraAI()

# ==== AUTH DECORATOR ====
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("admin_logged_in"):
            return f(*args, **kwargs)
        return redirect(url_for("login"))
    return wrapper

# ==== ROUTES ====
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email == OWNER_EMAIL and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_panel"))
    return render_template("login.html")

@app.route("/admin")
@admin_required
def admin_panel():
    return render_template("admin.html")

@app.route("/admin/terminal", methods=["POST"])
@admin_required
def admin_terminal():
    cmd = request.json.get("command")
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    return jsonify({"output": output})

@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.json.get("message", "")
    conn = sqlite3.connect("lyra.db")
    c = conn.cursor()
    c.execute("INSERT INTO chats (role, message) VALUES (?, ?)", ("user", prompt))
    conn.commit()

    response = select_llm(prompt)

    c.execute("INSERT INTO chats (role, message) VALUES (?, ?)", ("lyra", response))
    conn.commit()
    conn.close()

    return jsonify({"response": response})

@app.route("/history", methods=["GET"])
def history():
    conn = sqlite3.connect("lyra.db")
    c = conn.cursor()
    c.execute("SELECT role, message, timestamp FROM chats ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

@app.route("/speak", methods=["POST"])
def speak():
    text = request.json.get("text", "")
    tts = gTTS(text=text, lang="en")
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

@app.route("/daily_report", methods=["GET"])
@admin_required
def daily_report():
    return jsonify({"report": lyra.daily_report()})

if __name__ == "__main__":
    app.run(debug=True)
