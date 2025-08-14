from flask import Flask, request, jsonify
from flask_cors import CORS
from lyra_core import LyraAI

app = Flask(__name__)
CORS(app)

lyra = LyraAI(owner_name="Ricky", owner_email="ricardomcastrejon@gmail.com")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    response_text = lyra.respond(user_message)
    return jsonify({"response": response_text})

@app.route("/learn", methods=["POST"])
def learn():
    lyra.learn_security()
    lyra.learn_medicine()
    lyra.email_report()
    return jsonify({"status": "Learning & report sent"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
