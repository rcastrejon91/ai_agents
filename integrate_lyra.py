"""
Lyra AI System - Master Integration Script
"""
import os
import json
from pathlib import Path

def check_structure():
    print("🔍 Checking repository structure...")
    required_dirs = ['lyra_core', 'agents', 'data', 'lyra_app', 'config']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"📁 Creating: {dir_name}")
            os.makedirs(dir_name, exist_ok=True)
        else:
            print(f"✅ Found: {dir_name}")
    return True

def create_master_config():
    print("\n⚙️ Creating master configuration...")
    config = {
        "system": {"name": "Lyra AI System", "version": "1.0.0"},
        "lyra_core": {"enabled": True, "port": 5001},
        "agents": {
            "medical": {"enabled": True, "learning_path": "data/medical_learning"},
            "legal": {"enabled": True, "learning_path": "data/legal_learning"},
            "tech": {"enabled": True, "learning_path": "data/tech_learning"},
            "wealth": {"enabled": True, "learning_path": "data/wealth_learning"}
        }
    }
    os.makedirs('config', exist_ok=True)
    with open('config/master_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print("✅ Master configuration created")

def integrate_components():
    print("\n🔗 Integrating system components...")
    init_files = ['lyra_core/__init__.py', 'agents/__init__.py', 'lyra_app/__init__.py']
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✅ Created: {init_file}")

def main():
    print("="*60)
    print("🔧 LYRA AI SYSTEM - INTEGRATION WIZARD")
    print("="*60)
    check_structure()
    create_master_config()
    integrate_components()
    print("\n✅ INTEGRATION COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()
