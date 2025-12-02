import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from lyra_core.lyra_ai import LyraAI

app = Flask(__name__)
CORS(app)
lyra = LyraAI(owner_name="Ricky", owner_email="ricardomcastrejon@gmail.com")


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "message": "LyraAI API is running"})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    msg = data.get("message", "")
    emotion = data.get("emotion")
    env = data.get("env") or {}
    try:
        reply = lyra.respond(msg, emotion=emotion, env=env)
        return jsonify(
            {
                "response": reply,
                "world": lyra.world.summary(),
                "scene": lyra.scene.current,
                "focus": lyra.focus.top(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
