"""
Self-Learning Engine for Lyra AI
Enables continuous improvement through conversation analysis and pattern recognition.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class SelfLearningEngine:
    """
    Engine that learns from conversations and improves over time.
    """
    
    def __init__(self, storage_path: str = "data/learning"):
        self.storage_path = storage_path
        self.patterns = defaultdict(list)
        self.user_preferences = {}
        self.response_templates = {}
        self.topic_insights = defaultdict(dict)
        
        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing learning data
        self._load_learning_data()
    
    def process_conversation(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a conversation and extract learnings.
        
        Args:
            conversation: Dict containing user_message, agent_response, context
            
        Returns:
            Dict with extracted insights
        """
        insights = {
            "patterns": [],
            "topics": [],
            "sentiment": None,
            "preferences": {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Extract patterns
            patterns = self._extract_patterns(conversation)
            insights["patterns"] = patterns
            
            # Identify topics
            topics = self._identify_topics(conversation)
            insights["topics"] = topics
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(conversation)
            insights["sentiment"] = sentiment
            
            # Update user preferences
            preferences = self._update_preferences(conversation)
            insights["preferences"] = preferences
            
            # Store insights
            self._store_insights(insights)
            
            logger.info(f"Processed conversation, extracted {len(patterns)} patterns")
            
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
        
        return insights
    
    def _extract_patterns(self, conversation: Dict[str, Any]) -> List[str]:
        """Extract recurring patterns from conversation."""
        patterns = []
        
        user_msg = conversation.get("user_message", "").lower()
        
        # Common question patterns
        if any(word in user_msg for word in ["how", "what", "why", "when", "where"]):
            patterns.append("question")
        
        # Request patterns
        if any(word in user_msg for word in ["please", "can you", "could you", "help"]):
            patterns.append("polite_request")
        
        # Technical patterns
        if any(word in user_msg for word in ["code", "function", "api", "error", "bug"]):
            patterns.append("technical")
        
        # Store patterns
        for pattern in patterns:
            self.patterns[pattern].append({
                "message": user_msg[:100],
                "timestamp": datetime.now().isoformat()
            })
        
        return patterns
    
    def _identify_topics(self, conversation: Dict[str, Any]) -> List[str]:
        """Identify main topics in conversation."""
        topics = []
        
        text = (conversation.get("user_message", "") + " " + 
                conversation.get("agent_response", "")).lower()
        
        # Topic keywords
        topic_keywords = {
            "medical": ["health", "medical", "doctor", "symptom", "treatment"],
            "legal": ["law", "legal", "contract", "rights", "attorney"],
            "finance": ["money", "finance", "investment", "budget", "loan"],
            "technical": ["code", "programming", "software", "api", "database"],
            "general": []
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        if not topics:
            topics.append("general")
        
        return topics
    
    def _analyze_sentiment(self, conversation: Dict[str, Any]) -> str:
        """Analyze sentiment of conversation."""
        user_msg = conversation.get("user_message", "").lower()
        
        positive_words = ["thank", "great", "good", "excellent", "perfect", "love"]
        negative_words = ["bad", "wrong", "error", "problem", "issue", "hate"]
        
        positive_count = sum(1 for word in positive_words if word in user_msg)
        negative_count = sum(1 for word in negative_words if word in user_msg)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _update_preferences(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences based on conversation."""
        preferences = {}
        
        user_msg = conversation.get("user_message", "").lower()
        
        # Communication style preference
        if any(word in user_msg for word in ["brief", "short", "quick"]):
            preferences["response_length"] = "brief"
        elif any(word in user_msg for word in ["detailed", "explain", "elaborate"]):
            preferences["response_length"] = "detailed"
        
        # Formality preference
        if any(word in user_msg for word in ["formal", "professional"]):
            preferences["tone"] = "formal"
        elif any(word in user_msg for word in ["casual", "friendly"]):
            preferences["tone"] = "casual"
        
        # Update stored preferences
        self.user_preferences.update(preferences)
        
        return preferences
    
    def _store_insights(self, insights: Dict[str, Any]):
        """Store insights to disk."""
        filename = os.path.join(
            self.storage_path,
            f"insights_{datetime.now().strftime('%Y%m%d')}.json"
        )
        
        # Load existing insights for today
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                daily_insights = json.load(f)
        else:
            daily_insights = []
        
        daily_insights.append(insights)
        
        # Save updated insights
        with open(filename, 'w') as f:
            json.dump(daily_insights, f, indent=2)
    
    def _load_learning_data(self):
        """Load existing learning data from disk."""
        try:
            # Load patterns
            patterns_file = os.path.join(self.storage_path, "patterns.json")
            if os.path.exists(patterns_file):
                with open(patterns_file, 'r') as f:
                    self.patterns = defaultdict(list, json.load(f))
            
            # Load preferences
            prefs_file = os.path.join(self.storage_path, "preferences.json")
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r') as f:
                    self.user_preferences = json.load(f)
            
            logger.info("Loaded existing learning data")
            
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")
    
    def save_learning_data(self):
        """Save current learning data to disk."""
        try:
            # Save patterns
            with open(os.path.join(self.storage_path, "patterns.json"), 'w') as f:
                json.dump(dict(self.patterns), f, indent=2)
            
            # Save preferences
            with open(os.path.join(self.storage_path, "preferences.json"), 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
            
            logger.info("Saved learning data")
            
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about what has been learned."""
        return {
            "total_patterns": sum(len(p) for p in self.patterns.values()),
            "pattern_types": list(self.patterns.keys()),
            "user_preferences": self.user_preferences,
            "topics_analyzed": list(self.topic_insights.keys()),
            "storage_path": self.storage_path
        }
    
    def get_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """Get recommendations based on learned patterns."""
        recommendations = []
        
        # Based on user preferences
        if self.user_preferences.get("response_length") == "brief":
            recommendations.append("Keep response concise")
        
        if self.user_preferences.get("tone") == "formal":
            recommendations.append("Use formal language")
        
        # Based on patterns
        if "technical" in self.patterns and len(self.patterns["technical"]) > 5:
            recommendations.append("User frequently asks technical questions")
        
        return recommendations
    
    def reset_learning(self):
        """Reset all learning data (use with caution)."""
        self.patterns = defaultdict(list)
        self.user_preferences = {}
        self.response_templates = {}
        self.topic_insights = defaultdict(dict)
        
        # Clear storage files
        for filename in os.listdir(self.storage_path):
            filepath = os.path.join(self.storage_path, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        
        logger.warning("Learning data has been reset")
