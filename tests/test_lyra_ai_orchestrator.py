import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lyra_core.lyra_ai import LyraAI, llm_answer


def test_lyra_ai_instantiation():
    """Test that LyraAI can be instantiated successfully."""
    lyra = LyraAI("test_owner", "test@example.com")
    assert lyra.owner_name == "test_owner"
    assert lyra.owner_email == "test@example.com"
    assert lyra.manager is not None
    assert lyra.world is not None
    assert lyra.scene is not None
    assert lyra.focus is not None
    assert lyra.guardian is not None
    assert lyra.shield is not None


def test_llm_answer_fallback():
    """Test that llm_answer function works with fallback mechanism."""
    # Test basic functionality
    response = llm_answer("test message")
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Since GPT4All model isn't downloaded, should use stub
    assert response.startswith("Lyra(stub):")


def test_lyra_ai_routing():
    """Test that LyraAI routes messages correctly."""
    lyra = LyraAI("test_owner", "test@example.com")
    
    # Test finance routing
    response = lyra.respond("What is Tesla stock price?")
    assert "finance" in response.lower() or "Finance" in response
    
    # Test legal routing  
    response = lyra.respond("I need legal advice about a contract")
    assert "legal" in response.lower() or "Legal" in response
    
    # Test healthcare routing
    response = lyra.respond("I have a health symptom")
    assert "healthcare" in response.lower() or "Healthcare" in response


def test_lyra_ai_safety_features():
    """Test that LyraAI safety features are working."""
    lyra = LyraAI("test_owner", "test@example.com")
    
    # Test normal message (should work)
    response = lyra.respond("Hello, how are you?")
    assert isinstance(response, str)
    assert len(response) > 0


if __name__ == "__main__":
    test_lyra_ai_instantiation()
    test_llm_answer_fallback()
    test_lyra_ai_routing()
    test_lyra_ai_safety_features()
    print("✅ All LyraAI orchestrator tests passed!")