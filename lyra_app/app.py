import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from config import SECRET_KEY, ADMIN_PASSWORD, GMAIL_USER, GMAIL_PASS, OWNER_EMAIL, OWNER_NAME
from ml_models.self_learning import process_conversation_history

app = Flask(__name__)
app.secret_key = SECRET_KEY

conversation_history = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        return render_template("login.html", error="Invalid password")
    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))
    return render_template("admin.html")

@app.route("/conversation", methods=["POST"])
def conversation():
    data = request.get_json(force=True)
    conversation_history.append(data.get("message", ""))
    result = process_conversation_history(conversation_history)
    return jsonify(result)

@app.route("/learn", methods=["POST"])
def learn():
    result = process_conversation_history(conversation_history)
    return jsonify({"status": "learning complete", "result": result})

@app.route("/daily_report")
def daily_report():
    return jsonify({"report": f"Owner: {OWNER_NAME} <{OWNER_EMAIL}>", "status": "ok"})

@app.route("/terminal", methods=["POST"])
def terminal():
    cmd = request.get_json(force=True).get("command", "")
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5, text=True)
    except Exception as e:
        output = str(e)
    return jsonify({"output": output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
