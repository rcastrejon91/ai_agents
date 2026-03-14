#!/usr/bin/env python3
"""
run_lyra.py - Unified Lyra Launcher
Starts the advanced multi-perspective Lyra system
"""

import os
import sys

# Add root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
if __name__ == "__main__":
    from lyra_app.app import app
    
    port = int(os.getenv("PORT", "8080"))
    print(f"\n{'='*60}")
    print("🧠 LYRA AI - Multi-Perspective Orchestrator")
    print(f"{'='*60}")
    print(f"🚀 Server: http://localhost:{port}")
    print(f"💭 6 perspectives active")
    print(f"🔒 Security: Active")
    print(f"{'='*60}\n")
    
    app.run(host="0.0.0.0", port=port, debug=True)
