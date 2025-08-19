import contextlib
import io
import traceback

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from gtts import gTTS

app = Flask(__name__)
CORS(app)


@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json(force=True)
    text = data.get("text", "")
    data.get("mood", "neutral")
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
    app.run(host="0.0.0.0", port=5000)
