#!/usr/bin/env python3
# scripts/test_learning.py

"""
Test the self-learning system
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lyra_core.self_learning import SelfLearningEngine


def test_learning():
    """Test learning engine"""
    print("\n🧠 Testing Self-Learning Engine\n")
    print("=" * 70)

    # Create engine
    engine = SelfLearningEngine(data_dir="data/test_learning")

    # Sample conversation history
    history = [
        {
            "message": "What is NAD+ supplementation?",
            "response": "NAD+ is a coenzyme found in all living cells...",
            "emotion": {"dominant": "curious"},
        },
        {
            "message": "How do I create a legal contract?",
            "response": "To create a legal contract, you need...",
            "emotion": {"dominant": "neutral"},
        },
        {
            "message": "Thanks, that was helpful!",
            "response": "You're welcome! I'm glad I could help.",
            "emotion": {"dominant": "happy"},
        },
    ]

    # Process history
    print("\n📚 Processing conversation history...")
    result = engine.process_conversation_history(history)

    print(f"\n✅ {result['summary']}")
    print("\n📊 Results:")
    print(f"  • Patterns found: {result['patterns_found']}")
    print(f"  • Topics: {', '.join(result['topics_identified'])}")
    print(f"  • Sentiment: {result['sentiment']['dominant']}")
    print("\n💡 Learnings:")
    for learning in result["learnings"]:
        print(f"  • {learning}")

    # Get stats
    print("\n📈 Learning Statistics:")
    stats = engine.get_learning_stats()
    for key, value in stats.items():
        print(f"  • {key}: {value}")

    # Test pattern suggestion
    print("\n🔍 Testing Pattern Suggestions:")
    test_messages = ["What is NAD+?", "How do I create a contract?", "Hello!"]

    for msg in test_messages:
        suggestion = engine.get_pattern_suggestion(msg)
        if suggestion:
            print(
                f"  • '{msg}' → Pattern found (confidence: {suggestion.confidence:.2f})"
            )
        else:
            print(f"  • '{msg}' → No pattern found")

    print(f"\n{'='*70}")
    print("✅ Learning engine test complete!\n")


if __name__ == "__main__":
    test_learning()
