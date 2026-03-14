import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from lyra_core.ml_agent import MLAgent

app = Flask(__name__)

agents = {
    'medical': MLAgent("Medical", "data/medical_learning"),
    'legal': MLAgent("Legal", "data/legal_learning"),
    'tech': MLAgent("Tech", "data/tech_learning"),
    'wealth': MLAgent("Wealth", "data/wealth_learning")
}

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI ML Chat</title>
        <style>
            body { font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); margin: 0; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; padding: 20px; height: 90vh; display: flex; flex-direction: column; }
            h1 { text-align: center; color: #667eea; margin-bottom: 5px; }
            .subtitle { text-align: center; color: #999; font-size: 14px; margin-bottom: 15px; }
            .agent-buttons { display: flex; gap: 10px; margin-bottom: 20px; }
            .agent-btn { flex: 1; padding: 10px; border: 2px solid #667eea; background: white; border-radius: 8px; cursor: pointer; transition: all 0.3s; }
            .agent-btn:hover, .agent-btn.active { background: #667eea; color: white; }
            .messages { flex: 1; overflow-y: auto; border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 8px; animation: fadeIn 0.3s; }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            .user-msg { background: #667eea; color: white; text-align: right; }
            .agent-msg { background: #f0f0f0; }
            .input-area { display: flex; gap: 10px; }
            input { flex: 1; padding: 10px; border: 2px solid #667eea; border-radius: 8px; font-size: 16px; }
            button { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; transition: all 0.3s; }
            button:hover { background: #5568d3; }
            .badge { background: #4CAF50; color: white; padding: 2px 8px; border-radius: 5px; font-size: 12px; margin-left: 10px; }
            .ml-badge { background: #FF9800; color: white; padding: 2px 8px; border-radius: 5px; font-size: 11px; margin-left: 5px; }
            .stats { text-align: center; font-size: 12px; color: #999; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI ML Agent Chat</h1>
            <div class="subtitle">🧠 Powered by Machine Learning - Learns from every conversation</div>
            <div class="agent-buttons">
                <button class="agent-btn active" onclick="selectAgent('medical')">🏥 Medical</button>
                <button class="agent-btn" onclick="selectAgent('legal')">⚖️ Legal</button>
                <button class="agent-btn" onclick="selectAgent('tech')">💻 Tech</button>
                <button class="agent-btn" onclick="selectAgent('wealth')">💰 Wealth</button>
            </div>
            <div class="messages" id="messages">
                <div style="text-align: center; color: #999;">Start chatting! The AI learns from each interaction 🚀</div>
            </div>
            <div class="stats" id="stats">Total Learned Patterns: 0</div>
            <div class="input-area">
                <input type="text" id="input" placeholder="Type message..." onkeypress="if(event.key==='Enter') send()">
                <button onclick="send()">Send</button>
            </div>
        </div>
        <script>
            let agent = 'medical';
            let totalLearned = 0;
            
            function selectAgent(a) {
                agent = a;
                document.querySelectorAll('.agent-btn').forEach(b => b.classList.remove('active'));
                event.target.classList.add('active');
                document.getElementById('messages').innerHTML = '<div style="text-align:center;color:#999;">Chat with ' + a + ' ML Agent! 🤖🧠</div>';
                loadStats();
            }
            
            function send() {
                const input = document.getElementById('input');
                const msg = input.value.trim();
                if (!msg) return;
                addMsg(msg, 'user');
                input.value = '';
                
                fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({agent: agent, message: msg})
                }).then(r => r.json()).then(d => {
                    let response = d.response;
                    if (d.learned > 0) {
                        response += '<span class="badge">+' + d.learned + ' learned</span>';
                        totalLearned += d.learned;
                    }
                    if (d.confidence) {
                        const conf = Math.round(d.confidence * 100);
                        response += '<span class="ml-badge">ML: ' + conf + '%</span>';
                    }
                    addMsg(response, 'agent');
                    updateStats();
                });
            }
            
            function addMsg(text, type) {
                const div = document.createElement('div');
                div.className = 'message ' + type + '-msg';
                div.innerHTML = text;
                document.getElementById('messages').appendChild(div);
                div.scrollIntoView();
            }
            
            function updateStats() {
                document.getElementById('stats').innerHTML = 'Total Learned Patterns: ' + totalLearned;
            }
            
            function loadStats() {
                fetch('/stats?agent=' + agent)
                    .then(r => r.json())
                    .then(d => {
                        totalLearned = d.total_patterns;
                        updateStats();
                    });
            }
            
            loadStats();
        </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    agent = agents[data['agent']]
    result = agent.process_message(data['message'])
    agent.save_learnings()
    return jsonify({
        'response': result['response'],
        'learned': len(result['learned']['patterns']),
        'confidence': result['learned'].get('confidence', 0.5)
    })

@app.route('/stats')
def stats():
    agent_name = request.args.get('agent', 'medical')
    agent = agents[agent_name]
    patterns = agent.knowledge.get('patterns', {})
    return jsonify({
        'total_patterns': len(patterns),
        'agent': agent_name
    })

if __name__ == "__main__":
    print("\n🚀 ML-Powered Chat Dashboard Starting...")
    print("🧠 Machine Learning: ACTIVE")
    print("📱 Open: http://localhost:5001\n")
    app.run(debug=True, port=5001)
