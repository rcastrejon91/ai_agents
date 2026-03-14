# lyra_core/learning_engine.py

"""
Learning Engine - Integrates self-learning with Lyra Core
"""

from typing import Dict, Optional

from lyra_core.self_learning import SelfLearningEngine


class LearningEngine:
    """
    High-level learning engine for Lyra AI
    Integrates self-learning with the main system
    """

    def __init__(self):
        self.self_learning = SelfLearningEngine()
        self.learning_enabled = True
        self.auto_learn = True

    async def process_learning(self, learning_data: Dict):
        """Process a learning event"""
        if not self.learning_enabled:
            return

        # Store learning event
        history = [
            {
                "message": learning_data.get("input", ""),
                "response": learning_data.get("output", ""),
                "emotion": learning_data.get("emotion", {}),
                "timestamp": learning_data.get("timestamp", ""),
            }
        ]

        # Process if auto-learn is enabled
        if self.auto_learn:
            self.self_learning.process_conversation_history(history)

    def get_suggestion(self, message: str) -> Optional[str]:
        """Get response suggestion based on learned patterns"""
        pattern = self.self_learning.get_pattern_suggestion(message)
        if pattern and pattern.confidence > 0.7:
            return pattern.response_template
        return None

    def get_stats(self) -> Dict:
        """Get learning statistics"""
        return self.self_learning.get_learning_stats()

    def enable_learning(self):
        """Enable learning"""
        self.learning_enabled = True

    def disable_learning(self):
        """Disable learning"""
        self.learning_enabled = False

    def reset(self):
        """Reset all learning"""
        self.self_learning.reset_learning()
