"""
Lyra AI System - Unified Launcher
"""

import os


def start_lyra_core():
    print("🧠 Starting Lyra Core...")
    os.system("python lyra_core/chat_dashboard.py")


def main():
    print("=" * 60)
    print("🧠 LYRA AI SYSTEM - UNIFIED LAUNCHER")
    print("=" * 60)
    print("\nSelect launch mode:")
    print("1. Lyra Core Only (Recommended)")
    print("2. API Gateway Only")

    choice = input("\nEnter choice (1-2): ").strip()

    if choice == "1":
        start_lyra_core()
    elif choice == "2":
        os.system("python api_gateway.py")
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
