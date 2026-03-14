"""
AI Agent Learning Dashboard
Real-time visualization of agent learnings
"""

from flask import Flask, render_template, jsonify
import json
import os
from pathlib import Path

app = Flask(__name__)

def get_agent_stats():
    """Collect stats from all agents"""
    agents_data = []
    data_dir = Path("data")
    
    for agent_dir in data_dir.glob("*_learning"):
        agent_name = agent_dir.name.replace("_learning", "")
        
        stats = {
            "name": agent_name,
            "total_patterns": 0,
            "topics": [],
            "preferences": {}
        }
        
        # Load patterns
        patterns_file = agent_dir / "patterns.json"
        if patterns_file.exists():
            with open(patterns_file) as f:
                patterns = json.load(f)
                stats["total_patterns"] = len(patterns)
        
        # Load preferences
        prefs_file = agent_dir / "user_preferences.json"
        if prefs_file.exists():
            with open(prefs_file) as f:
                stats["preferences"] = json.load(f)
        
        # Load topics
        topics_file = agent_dir / "topics.json"
        if topics_file.exists():
            with open(topics_file) as f:
                stats["topics"] = json.load(f)
        
        agents_data.append(stats)
    
    return agents_data

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Agent Learning Dashboard</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                margin: 0;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                text-align: center;
                font-size: 3em;
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                opacity: 0.9;
                margin-bottom: 40px;
            }
            .agents-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .agent-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            .agent-card:hover {
                transform: translateY(-5px);
            }
            .agent-name {
                font-size: 1.8em;
                font-weight: bold;
                margin-bottom: 15px;
                text-transform: capitalize;
            }
            .stat {
                margin: 10px 0;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
            .stat-label {
                font-weight: bold;
                opacity: 0.8;
            }
            .stat-value {
                font-size: 1.2em;
                margin-top: 5px;
            }
            .refresh-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: #4CAF50;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 50px;
                font-size: 1.1em;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
                transition: all 0.3s ease;
            }
            .refresh-btn:hover {
                background: #45a049;
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 AI Agent Learning Dashboard</h1>
            <p class="subtitle">Real-time monitoring of agent intelligence</p>
            
            <div id="agents-container" class="agents-grid"></div>
        </div>
        
        <button class="refresh-btn" onclick="loadAgents()">🔄 Refresh</button>
        
        <script>
            function loadAgents() {
                fetch('/api/agents')
                    .then(response => response.json())
                    .then(data => {
                        const container = document.getElementById('agents-container');
                        container.innerHTML = '';
                        
                        data.agents.forEach(agent => {
                            const card = document.createElement('div');
                            card.className = 'agent-card';
                            
                            card.innerHTML = `
                                <div class="agent-name">🤖 ${agent.name}Bot</div>
                                
                                <div class="stat">
                                    <div class="stat-label">📚 Total Patterns Learned</div>
                                    <div class="stat-value">${agent.total_patterns}</div>
                                </div>
                                
                                <div class="stat">
                                    <div class="stat-label">🎯 Topics</div>
                                    <div class="stat-value">${agent.topics.length || 0}</div>
                                </div>
                                
                                <div class="stat">
                                    <div class="stat-label">⚙️ User Preferences</div>
                                    <div class="stat-value">${Object.keys(agent.preferences).length}</div>
                                </div>
                            `;
                            
                            container.appendChild(card);
                        });
                    });
            }
            
            // Load on page load
            loadAgents();
            
            // Auto-refresh every 5 seconds
            setInterval(loadAgents, 5000);
        </script>
    </body>
    </html>
    """

@app.route('/api/agents')
def api_agents():
    """API endpoint for agent stats"""
    return jsonify({
        "agents": get_agent_stats()
    })

if __name__ == "__main__":
    print("\n🚀 Starting AI Agent Dashboard...")
    print("📊 Open your browser to: http://localhost:5000")
    print("="*60)
    app.run(debug=True, port=5000)

s