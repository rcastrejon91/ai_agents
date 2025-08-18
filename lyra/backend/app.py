import contextlib
import io
import os
import traceback
from typing import Optional

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from gtts import gTTS

# Initialize Flask app
app = Flask(__name__)

# Configure CORS with environment-specific settings
def configure_cors():
    """Configure CORS based on environment variables"""
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
    
    # Default origins for development
    if not allowed_origins:
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8080", 
            "https://*.vercel.app",
            "https://*.railway.app"
        ]
    
    CORS(app, 
         origins=allowed_origins,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True)

configure_cors()

# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for deployment platforms"""
    return jsonify({
        "status": "healthy",
        "service": "lyra-backend",
        "version": "1.0.0"
    })

@app.route("/", methods=["GET"])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Lyra Backend API",
        "version": "1.0.0",
        "endpoints": ["/speak", "/listen", "/learn", "/daily_report", "/run_code", "/health"]
    })


@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json(force=True)
    text = data.get("text", "")
    mood = data.get("mood", "neutral")
    tts = gTTS(text)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return send_file(audio_bytes, mimetype="audio/mpeg")


@app.route("/listen", methods=["GET"])
def listen():
    # Placeholder implementation
    return jsonify({"transcript": "Listening not implemented."})


@app.route("/learn", methods=["POST"])
def learn():
    return jsonify({"status": "Learning complete."})


@app.route("/daily_report", methods=["GET"])
def daily_report():
    return jsonify({"report": "All systems operational."})


@app.route("/run_code", methods=["POST"])
def run_code():
    data = request.get_json(force=True)
    code = data.get("code", "")
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {})
        result = output.getvalue()
        return jsonify({"result": result})
    except Exception:
        return jsonify({"error": traceback.format_exc()}), 400


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
