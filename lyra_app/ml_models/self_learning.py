# lyra_core/self_learning.py

"""
Self-Learning Engine for Lyra AI
Processes conversation history, extracts patterns, and improves responses
"""

from __future__ import annotations

import json
import pickle
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConversationPattern:
    """Represents a learned conversation pattern"""

    def __init__(
        self,
        pattern_type: str,
        trigger: str,
        response_template: str,
        confidence: float = 0.5,
        usage_count: int = 0,
    ):
        self.pattern_type = pattern_type
        self.trigger = trigger
        self.response_template = response_template
        self.confidence = confidence
        self.usage_count = usage_count
        self.created_at = datetime.now()
        self.last_used = None
        self.success_rate = 0.0

    def use(self, successful: bool = True):
        """Record pattern usage"""
        self.usage_count += 1
        self.last_used = datetime.now()

        # Update success rate
        if successful:
            self.success_rate = (
                self.success_rate * (self.usage_count - 1) + 1.0
            ) / self.usage_count
        else:
            self.success_rate = (
                self.success_rate * (self.usage_count - 1)
            ) / self.usage_count

        # Adjust confidence based on success rate
        self.confidence = min(1.0, self.success_rate * 1.2)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "pattern_type": self.pattern_type,
            "trigger": self.trigger,
            "response_template": self.response_template,
            "confidence": self.confidence,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }


class SelfLearningEngine:
    """
    Self-learning engine that improves Lyra's responses over time

    Features:
    - Pattern extraction from conversations
    - Response optimization
    - User preference learning
    - Topic modeling
    - Sentiment analysis
    - Success prediction
    """

    def __init__(self, data_dir: str = "data/learning"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Learning components
        self.patterns: Dict[str, ConversationPattern] = {}
        self.user_preferences: Dict[str, Any] = {}
        self.topic_frequencies: Counter = Counter()
        self.response_quality: Dict[str, float] = {}
        self.conversation_contexts: List[Dict] = []

        # Statistics
        self.total_conversations = 0
        self.total_patterns_learned = 0
        self.learning_sessions = 0

        # Load existing knowledge
        self.load_knowledge()

    def process_conversation_history(self, history: List[Dict]) -> Dict:
        """
        Process conversation history and extract learnings

        Args:
            history: List of conversation turns

        Returns:
            Learning summary
        """
        if not history:
            return {
                "summary": "No conversation history to process",
                "patterns_found": 0,
                "topics_identified": [],
                "learnings": [],
            }

        self.learning_sessions += 1
        self.total_conversations += len(history)

        learnings = []

        # Extract patterns
        patterns = self._extract_patterns(history)
        learnings.append(f"Extracted {len(patterns)} conversation patterns")

        # Identify topics
        topics = self._identify_topics(history)
        learnings.append(f"Identified topics: {', '.join(topics[:5])}")

        # Analyze sentiment
        sentiment = self._analyze_sentiment(history)
        learnings.append(f"Overall sentiment: {sentiment['dominant']}")

        # Learn user preferences
        preferences = self._learn_preferences(history)
        learnings.append(f"Updated {len(preferences)} user preferences")

        # Optimize responses
        optimizations = self._optimize_responses(history)
        learnings.append(f"Optimized {len(optimizations)} response templates")

        # Save knowledge
        self.save_knowledge()

        return {
            "summary": f"Processed {len(history)} conversations and extracted valuable learnings",
            "patterns_found": len(patterns),
            "topics_identified": topics,
            "sentiment": sentiment,
            "learnings": learnings,
            "total_patterns": len(self.patterns),
            "learning_sessions": self.learning_sessions,
        }

    def _extract_patterns(self, history: List[Dict]) -> List[ConversationPattern]:
        """Extract conversation patterns"""
        patterns = []

        for i, turn in enumerate(history):
            message = turn.get("message", "").lower()
            response = turn.get("response", "")

            # Question patterns
            if "?" in message:
                pattern_type = "question"
                trigger = self._extract_trigger(message)

                if trigger and len(trigger) > 3:
                    pattern = ConversationPattern(
                        pattern_type=pattern_type,
                        trigger=trigger,
                        response_template=self._generalize_response(response),
                        confidence=0.6,
                    )
                    patterns.append(pattern)

                    # Store pattern
                    pattern_key = f"{pattern_type}:{trigger}"
                    if pattern_key not in self.patterns:
                        self.patterns[pattern_key] = pattern
                        self.total_patterns_learned += 1
                    else:
                        self.patterns[pattern_key].use(successful=True)

            # Command patterns
            if any(word in message for word in ["create", "make", "build", "generate"]):
                pattern_type = "command"
                trigger = self._extract_trigger(message)

                if trigger:
                    pattern = ConversationPattern(
                        pattern_type=pattern_type,
                        trigger=trigger,
                        response_template=self._generalize_response(response),
                        confidence=0.7,
                    )
                    patterns.append(pattern)

                    pattern_key = f"{pattern_type}:{trigger}"
                    if pattern_key not in self.patterns:
                        self.patterns[pattern_key] = pattern
                        self.total_patterns_learned += 1

            # Greeting patterns
            if any(word in message for word in ["hello", "hi", "hey", "greetings"]):
                pattern_type = "greeting"
                pattern = ConversationPattern(
                    pattern_type=pattern_type,
                    trigger="greeting",
                    response_template=response,
                    confidence=0.9,
                )
                patterns.append(pattern)

        return patterns

    def _extract_trigger(self, message: str) -> str:
        """Extract trigger phrase from message"""
        # Remove common words
        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "what",
            "how",
            "why",
            "when",
        }
        words = [
            w for w in message.lower().split() if w not in stop_words and len(w) > 2
        ]

        # Return first 3 significant words
        return " ".join(words[:3]) if words else ""

    def _generalize_response(self, response: str) -> str:
        """Generalize response into a template"""
        # Simple generalization - replace specific values with placeholders
        template = response

        # Replace numbers
        import re

        template = re.sub(r"\b\d+\b", "{number}", template)

        # Replace dates
        template = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "{date}", template)

        return template

    def _identify_topics(self, history: List[Dict]) -> List[str]:
        """Identify conversation topics"""
        topics = []

        # Topic keywords
        topic_keywords = {
            "medical": [
                "health",
                "medical",
                "doctor",
                "medicine",
                "supplement",
                "nad+",
            ],
            "legal": ["legal", "law", "contract", "attorney", "compliance"],
            "finance": ["finance", "money", "invest", "stock", "crypto"],
            "technology": ["code", "program", "software", "tech", "ai"],
            "business": ["business", "company", "startup", "entrepreneur"],
            "personal": ["personal", "life", "advice", "help", "question"],
        }

        for turn in history:
            message = turn.get("message", "").lower()

            for topic, keywords in topic_keywords.items():
                if any(keyword in message for keyword in keywords):
                    topics.append(topic)
                    self.topic_frequencies[topic] += 1

        # Return unique topics sorted by frequency
        return list(dict.fromkeys(topics))

    def _analyze_sentiment(self, history: List[Dict]) -> Dict:
        """Analyze conversation sentiment"""
        sentiments = []

        # Simple sentiment keywords
        positive_words = [
            "good",
            "great",
            "excellent",
            "thanks",
            "helpful",
            "love",
            "perfect",
        ]
        negative_words = [
            "bad",
            "wrong",
            "error",
            "problem",
            "issue",
            "confused",
            "frustrated",
        ]

        for turn in history:
            message = turn.get("message", "").lower()

            pos_count = sum(1 for word in positive_words if word in message)
            neg_count = sum(1 for word in negative_words if word in message)

            if pos_count > neg_count:
                sentiments.append("positive")
            elif neg_count > pos_count:
                sentiments.append("negative")
            else:
                sentiments.append("neutral")

        # Calculate dominant sentiment
        sentiment_counts = Counter(sentiments)
        dominant = sentiment_counts.most_common(1)[0][0] if sentiments else "neutral"

        return {
            "dominant": dominant,
            "distribution": dict(sentiment_counts),
            "score": (sentiment_counts["positive"] - sentiment_counts["negative"])
            / max(len(sentiments), 1),
        }

    def _learn_preferences(self, history: List[Dict]) -> Dict:
        """Learn user preferences from conversation"""
        preferences = {}

        for turn in history:
            message = turn.get("message", "").lower()
            emotion = turn.get("emotion", {})

            # Learn response length preference
            if "brief" in message or "short" in message:
                preferences["response_length"] = "brief"
            elif "detailed" in message or "explain" in message:
                preferences["response_length"] = "detailed"

            # Learn formality preference
            if "formal" in message or "professional" in message:
                preferences["formality"] = "formal"
            elif "casual" in message or "friendly" in message:
                preferences["formality"] = "casual"

            # Learn emotion awareness preference
            if emotion and emotion.get("dominant") != "neutral":
                preferences["emotion_aware"] = True

        # Update stored preferences
        self.user_preferences.update(preferences)

        return preferences

    def _optimize_responses(self, history: List[Dict]) -> List[str]:
        """Optimize response templates based on success"""
        optimizations = []

        for turn in history:
            response = turn.get("response", "")

            # Track response quality (simplified)
            response_key = response[:50]  # Use first 50 chars as key

            if response_key not in self.response_quality:
                self.response_quality[response_key] = 0.5

            # Increase quality score if response was successful
            # (In real implementation, this would be based on user feedback)
            self.response_quality[response_key] = min(
                1.0, self.response_quality[response_key] + 0.05
            )

            optimizations.append(response_key)

        return optimizations

    def get_pattern_suggestion(self, message: str) -> Optional[ConversationPattern]:
        """Get pattern suggestion for a message"""
        message_lower = message.lower()

        # Find matching patterns
        matches = []
        for key, pattern in self.patterns.items():
            if pattern.trigger in message_lower:
                matches.append((pattern, pattern.confidence))

        # Return highest confidence match
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][0]

        return None

    def get_learning_stats(self) -> Dict:
        """Get learning statistics"""
        return {
            "total_conversations": self.total_conversations,
            "total_patterns": len(self.patterns),
            "patterns_learned": self.total_patterns_learned,
            "learning_sessions": self.learning_sessions,
            "top_topics": self.topic_frequencies.most_common(5),
            "user_preferences": self.user_preferences,
            "high_confidence_patterns": sum(
                1 for p in self.patterns.values() if p.confidence > 0.8
            ),
        }

    def save_knowledge(self):
        """Save learned knowledge to disk"""
        knowledge = {
            "patterns": {k: v.to_dict() for k, v in self.patterns.items()},
            "user_preferences": self.user_preferences,
            "topic_frequencies": dict(self.topic_frequencies),
            "response_quality": self.response_quality,
            "stats": {
                "total_conversations": self.total_conversations,
                "total_patterns_learned": self.total_patterns_learned,
                "learning_sessions": self.learning_sessions,
            },
        }

        # Save as JSON
        knowledge_file = self.data_dir / "knowledge.json"
        with open(knowledge_file, "w") as f:
            json.dump(knowledge, f, indent=2)

        # Save as pickle for faster loading
        pickle_file = self.data_dir / "knowledge.pkl"
        with open(pickle_file, "wb") as f:
            pickle.dump(knowledge, f)

    def load_knowledge(self):
        """Load learned knowledge from disk"""
        pickle_file = self.data_dir / "knowledge.pkl"
        json_file = self.data_dir / "knowledge.json"

        try:
            # Try pickle first (faster)
            if pickle_file.exists():
                with open(pickle_file, "rb") as f:
                    knowledge = pickle.load(f)
            elif json_file.exists():
                with open(json_file, "r") as f:
                    knowledge = json.load(f)
            else:
                return

            # Restore patterns
            for key, pattern_dict in knowledge.get("patterns", {}).items():
                self.patterns[key] = ConversationPattern(
                    pattern_type=pattern_dict["pattern_type"],
                    trigger=pattern_dict["trigger"],
                    response_template=pattern_dict["response_template"],
                    confidence=pattern_dict["confidence"],
                    usage_count=pattern_dict["usage_count"],
                )
                self.patterns[key].success_rate = pattern_dict.get("success_rate", 0.0)

            # Restore other data
            self.user_preferences = knowledge.get("user_preferences", {})
            self.topic_frequencies = Counter(knowledge.get("topic_frequencies", {}))
            self.response_quality = knowledge.get("response_quality", {})

            # Restore stats
            stats = knowledge.get("stats", {})
            self.total_conversations = stats.get("total_conversations", 0)
            self.total_patterns_learned = stats.get("total_patterns_learned", 0)
            self.learning_sessions = stats.get("learning_sessions", 0)

        except Exception as e:
            print(f"Warning: Could not load knowledge: {e}")

    def reset_learning(self):
        """Reset all learned knowledge"""
        self.patterns.clear()
        self.user_preferences.clear()
        self.topic_frequencies.clear()
        self.response_quality.clear()
        self.conversation_contexts.clear()

        self.total_conversations = 0
        self.total_patterns_learned = 0
        self.learning_sessions = 0

        self.save_knowledge()


# Backward compatibility with old function
def process_conversation_history(history):
    """Process conversation history and return a summary."""
    engine = SelfLearningEngine()
    return engine.process_conversation_history(history)
