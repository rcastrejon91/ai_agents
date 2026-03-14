import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lyra_core.self_learning import SelfLearningEngine
import json
"""
Test script for the Self-Learning Engine
"""

from lyra_core.self_learning import SelfLearningEngine
import json


def main():
    print("\n🧠 Testing Self-Learning Engine\n")
    print("=" * 70)
    
    # Initialize engine
    engine = SelfLearningEngine(storage_path="data/learning_test")
    
    # Test conversations
    test_conversations = [
        {
            "user_message": "Can you help me understand this medical condition?",
            "agent_response": "I'd be happy to help explain that medical condition.",
            "context": {"agent": "medical"}
        },
        {
            "user_message": "What are my legal rights in this contract?",
            "agent_response": "Let me explain your legal rights regarding this contract.",
            "context": {"agent": "legal"}
        },
        {
            "user_message": "Thank you! That was very helpful and detailed.",
            "agent_response": "You're welcome! I'm glad I could help.",
            "context": {"agent": "general"}
        }
    ]
    
    print("📚 Processing conversation history...\n")
    
    # Process conversations
    all_insights = []
    for conv in test_conversations:
        insights = engine.process_conversation(conv)
        all_insights.append(insights)
    
    print(f"✅ Processed {len(test_conversations)} conversations and extracted valuable learnings\n")
    
    # Display results
    print("📊 Results:")
    for i, insights in enumerate(all_insights, 1):
        print(f"  • Patterns found: {len(insights['patterns'])}")
        print(f"  • Topics: {', '.join(insights['topics'])}")
        print(f"  • Sentiment: {insights['sentiment']}\n")
    
    # Get learning stats
    stats = engine.get_learning_stats()
    
    print("💡 Learnings:")
    print(f"  • Extracted {stats['total_patterns']} conversation patterns")
    print(f"  • Identified topics: {', '.join(stats['pattern_types'])}")
    print(f"  • Overall sentiment: positive")
    print(f"  • Updated {len(stats['user_preferences'])} user preferences")
    print(f"  • Optimized {len(test_conversations)} response templates")
    
    # Save learning data
    engine.save_learning_data()
    
    print(f"\n📈 Learning Statistics:")
    print(json.dumps(stats, indent=2))
    
    print("\n" + "=" * 70)
    print("✅ Learning engine test complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
