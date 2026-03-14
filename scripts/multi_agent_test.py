"""
Multi-Agent Learning System Test
"""

from lyra_core.smart_agent import SmartAgent
import json


def test_multi_agents():
    # Create specialized agents
    agents = {
        'medical': SmartAgent("MedicalBot", "data/medical_learning"),
        'legal': SmartAgent("LegalBot", "data/legal_learning"),
        'tech': SmartAgent("TechBot", "data/tech_learning")
    }
    
    # Test conversations
    conversations = {
        'medical': [
            "What are the symptoms of flu?",
            "Please explain in detail",
            "Thank you for the thorough explanation"
        ],
        'legal': [
            "What is a contract?",
            "Can you give me more details?",
            "That's very helpful"
        ],
        'tech': [
            "How do I fix my WiFi?",
            "I need step-by-step instructions",
            "Perfect, thanks!"
        ]
    }
    
    print("\n🤖 Multi-Agent Learning System Test")
    print("="*70)
    
    for agent_type, agent in agents.items():
        print(f"\n\n📱 Testing {agent.name}")
        print("-"*70)
        
        for msg in conversations[agent_type]:
            result = agent.process_message(msg)
            print(f"\n👤 User: {msg}")
            print(f"🤖 {agent.name}: {result['response']}")
            print(f"📚 Patterns learned: {len(result['learned']['patterns'])}")
        
        agent.save_learnings()
        stats = agent.learning_engine.get_learning_stats()
        print(f"\n✅ {agent.name} total patterns: {stats['total_patterns']}")
    
    print("\n" + "="*70)
    print("✅ All agents trained and saved!")
    print("="*70)


if __name__ == "__main__":
    test_multi_agents()
