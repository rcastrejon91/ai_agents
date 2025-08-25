from flask import Flask, jsonify, request
from flask_cors import CORS

from lyra_core.lyra_ai import LyraAI

app = Flask(__name__)
CORS(app)
lyra = LyraAI(owner_name="Ricky", owner_email="ricardomcastrejon@gmail.com")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    msg = data.get("message", "")
    emotion = data.get("emotion")
    env = data.get("env") or {}
    reply = lyra.respond(msg, emotion=emotion, env=env)
    return jsonify(
        {
            "response": reply,
            "world": lyra.world.summary(),
            "scene": lyra.scene.current,
            "focus": lyra.focus.top(),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
