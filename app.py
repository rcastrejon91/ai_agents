import logging
import os
import secrets
import sys
from datetime import datetime, timezone

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.middleware.auth import generate_csrf_token, require_auth

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.config["SECRET_KEY"] = secrets.token_hex(32)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Template context
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token())


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not found"), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify(error="Internal server error"), 500


# Routes
@app.route("/")
def index():
    return render_template("pages/index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Verify CSRF token for POST requests
        token = request.form.get("csrf_token")
        if not token or not secrets.compare_digest(
            token, session.get("csrf_token", "")
        ):
            return render_template("pages/login.html", error="Invalid security token")

        password = request.form.get("password")
        # Simple password check for demo - in production use proper auth
        if password == os.getenv("ADMIN_PASSWORD", "admin123"):
            session["authenticated"] = True
            return redirect(url_for("admin"))
        return render_template("pages/login.html", error="Invalid credentials")
    return render_template("pages/login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# Secure routes
@app.route("/admin")
@require_auth
def admin():
    return render_template("pages/admin.html")


# UTC datetime handling
def get_current_time():
    return datetime.now(timezone.utc)


# Health check
@app.route("/health")
def health():
    return jsonify(
        status="ok",
        timestamp=get_current_time().isoformat(),
        service="AI Agents Flask App",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")), debug=True)
