import os
import datetime
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, send_file, render_template
import io
from gtts import gTTS
import speech_recognition as sr

OWNER_NAME = "Ricky"
OWNER_EMAIL = "ricardomcastrejon@gmail.com"
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

app = Flask(__name__)

class LyraAI:
    def __init__(self):
        self.security_protocols = []
        self.medical_knowledge_base = {}
        self.security_knowledge_base = {}
        self.self_learning_log = []

    def learn_security(self):
        learned_data = {
            "date": datetime.date.today().isoformat(),
            "new_threats": ["Example Threat"],
            "new_protections": ["Firewall AI patch"]
        }
        self.security_knowledge_base[learned_data["date"]] = learned_data
        self.security_protocols.extend(learned_data["new_protections"])

    def learn_medicine(self):
        learned_data = {
            "date": datetime.date.today().isoformat(),
            "new_studies": ["Breakthrough in medicine"],
            "new_treatments": ["AI-assisted diagnosis"]
        }
        self.medical_knowledge_base[learned_data["date"]] = learned_data

    def daily_report(self):
        return f"LYRA DAILY REPORT – {datetime.date.today().isoformat()}"

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

@app.route("/")
def index():
    return render_template("index.html")

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
def daily_report_api():
    lyra.learn_security()
    lyra.learn_medicine()
    try:
        lyra.email_report()
        status = "Report sent via email."
    except Exception as e:
        status = f"Report generated, email failed: {e}"
    return jsonify({"status": status, "report": lyra.daily_report()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
