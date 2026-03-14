import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lyra AI Dashboard</title>
        <style>
            body { font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); 
                   margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; 
                   min-height: 100vh; }
            .container { background: white; border-radius: 15px; padding: 40px; 
                        max-width: 600px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
            h1 { color: #667eea; margin-bottom: 20px; }
            .status { background: #4CAF50; color: white; padding: 15px; border-radius: 8px; 
                     margin: 20px 0; font-size: 18px; }
            .info { color: #666; line-height: 1.8; }
            .badge { background: #FF9800; color: white; padding: 5px 15px; border-radius: 20px; 
                    display: inline-block; margin: 10px 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 Lyra AI System</h1>
            <div class="status">✅ System Online</div>
            <div class="info">
                <h3>Available Agents:</h3>
                <div class="badge">🏥 Medical</div>
                <div class="badge">⚖️ Legal</div>
                <div class="badge">💻 Tech</div>
                <div class="badge">💰 Wealth</div>
                <p style="margin-top: 30px;">
                    <strong>API Endpoint:</strong><br>
                    POST /api/chat<br>
                    <small>Send messages to interact with AI agents</small>
                </p>
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    return jsonify(
        {"response": f"Lyra received: {message}", "agent": "tech", "status": "success"}
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧠 LYRA AI DASHBOARD STARTING...")
    print("=" * 60)
    print("📱 Dashboard: http://localhost:5001")
    print("🌐 API: http://localhost:5001/api/chat")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=5001, debug=True)
