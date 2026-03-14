"""
core/lyra_orchestrator.py - Multi-Perspective Intelligence Engine

This is the MISSING PIECE that lyra_app/app.py needs!
Connects all Lyra components with 6-perspective analysis.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional


class Perspective:
    """Individual perspective analyzer"""
    
    def __init__(self, name: str, weight: float, traits: Dict[str, Any]):
        self.name = name
        self.weight = weight
        self.traits = traits
        self.activation_count = 0
    
    async def analyze(self, message: str, context: Dict) -> Dict[str, Any]:
        """Analyze message from this perspective"""
        self.activation_count += 1
        
        # Perspective-specific analysis
        analysis = {
            "perspective": self.name,
            "weight": self.weight,
            "confidence": 0.5,  # Base confidence
            "insights": [],
            "recommendations": []
        }
        
        msg_lower = message.lower()
        
        # Pragmatist - Focus on practical, actionable steps
        if self.name == "Pragmatist":
            if any(word in msg_lower for word in ["how", "what", "when", "steps"]):
                analysis["confidence"] = 0.8
                analysis["insights"].append("User seeks practical guidance")
                analysis["recommendations"].append("Provide clear, actionable steps")
        
        # Visionary - Big picture, future-focused
        elif self.name == "Visionary":
            if any(word in msg_lower for word in ["future", "goal", "dream", "vision", "potential"]):
                analysis["confidence"] = 0.9
                analysis["insights"].append("User thinking long-term")
                analysis["recommendations"].append("Inspire with possibilities")
        
        # Analyst - Data-driven, logical
        elif self.name == "Analyst":
            if any(word in msg_lower for word in ["why", "data", "analyze", "compare", "statistics"]):
                analysis["confidence"] = 0.85
                analysis["insights"].append("User wants logical analysis")
                analysis["recommendations"].append("Provide data and reasoning")
        
        # Creator - Innovative, creative solutions
        elif self.name == "Creator":
            if any(word in msg_lower for word in ["create", "design", "build", "innovative", "new"]):
                analysis["confidence"] = 0.8
                analysis["insights"].append("User seeks creative solutions")
                analysis["recommendations"].append("Suggest innovative approaches")
        
        # Rebel - Challenge assumptions, unconventional
        elif self.name == "Rebel":
            if any(word in msg_lower for word in ["different", "alternative", "unconventional", "challenge"]):
                analysis["confidence"] = 0.75
                analysis["insights"].append("User open to unconventional ideas")
                analysis["recommendations"].append("Challenge the status quo")
        
        # Empath - Emotional intelligence, support
        elif self.name == "Empath":
            if any(word in msg_lower for word in ["feel", "worried", "excited", "scared", "happy", "sad"]):
                analysis["confidence"] = 0.9
                analysis["insights"].append("User expressing emotions")
                analysis["recommendations"].append("Provide emotional support")
        
        return analysis


class LyraOrchestrator:
    """
    Multi-Perspective AI Orchestrator
    Synthesizes insights from 6 different perspectives
    """
    
    def __init__(self, config: Optional[Dict] = None):
        config = config or {}
        
        self.owner_name = config.get("owner_name", "User")
        self.interactions_processed = 0
        self.start_time = datetime.utcnow()
        
        # Initialize perspectives with default weights
        default_weights = {
            "Pragmatist": 0.20,
            "Visionary": 0.15,
            "Analyst": 0.20,
            "Creator": 0.15,
            "Rebel": 0.15,
            "Empath": 0.15,
        }
        
        weights = config.get("perspective_weights", default_weights)
        
        self.perspectives = {
            "Pragmatist": Perspective("Pragmatist", weights["Pragmatist"], {
                "focus": "practical_action",
                "style": "direct"
            }),
            "Visionary": Perspective("Visionary", weights["Visionary"], {
                "focus": "future_potential",
                "style": "inspirational"
            }),
            "Analyst": Perspective("Analyst", weights["Analyst"], {
                "focus": "logical_reasoning",
                "style": "methodical"
            }),
            "Creator": Perspective("Creator", weights["Creator"], {
                "focus": "innovation",
                "style": "imaginative"
            }),
            "Rebel": Perspective("Rebel", weights["Rebel"], {
                "focus": "unconventional",
                "style": "challenging"
            }),
            "Empath": Perspective("Empath", weights["Empath"], {
                "focus": "emotional_support",
                "style": "compassionate"
            }),
        }
        
        self.perspective_weights = weights
    
    async def process(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process message through all perspectives and synthesize response
        """
        context = context or {}
        self.interactions_processed += 1
        
        # Run all perspectives in parallel
        analyses = await asyncio.gather(*[
            perspective.analyze(message, context)
            for perspective in self.perspectives.values()
        ])
        
        # Synthesize results
        synthesis = self._synthesize(analyses, message, context)
        
        return synthesis
    
    def _synthesize(self, analyses: List[Dict], message: str, context: Dict) -> Dict[str, Any]:
        """Synthesize all perspective analyses into unified response"""
        
        # Calculate weighted scores
        weighted_scores = {}
        for analysis in analyses:
            name = analysis["perspective"]
            score = analysis["confidence"] * self.perspectives[name].weight
            weighted_scores[name] = score
        
        # Find dominant perspective
        dominant = max(weighted_scores, key=weighted_scores.get)
        
        # Determine intent
        intent = self._determine_intent(message)
        
        # Determine approach
        approach = self._determine_approach(analyses, dominant)
        
        return {
            "intent": intent,
            "dominant_perspective": dominant,
            "confidence": weighted_scores[dominant],
            "approach": approach,
            "all_perspectives": {
                name: {
                    "confidence": analysis["confidence"],
                    "insights": analysis["insights"],
                    "recommendations": analysis["recommendations"]
                }
                for name, analysis in zip(weighted_scores.keys(), analyses)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _determine_intent(self, message: str) -> str:
        """Determine user's intent from message"""
        msg_lower = message.lower()
        
        if any(word in msg_lower for word in ["help", "how", "what", "guide"]):
            return "seeking_guidance"
        elif any(word in msg_lower for word in ["feel", "worried", "scared", "anxious"]):
            return "emotional_support"
        elif any(word in msg_lower for word in ["create", "build", "make", "design"]):
            return "creative_task"
        elif any(word in msg_lower for word in ["analyze", "compare", "evaluate"]):
            return "analytical_task"
        elif any(word in msg_lower for word in ["future", "goal", "plan", "vision"]):
            return "planning"
        else:
            return "general_conversation"
    
    def _determine_approach(self, analyses: List[Dict], dominant: str) -> str:
        """Determine best approach based on analyses"""
        
        # Map dominant perspective to approach
        approach_map = {
            "Pragmatist": "action_oriented",
            "Visionary": "inspirational",
            "Analyst": "data_driven",
            "Creator": "innovative",
            "Rebel": "unconventional",
            "Empath": "supportive"
        }
        
        return approach_map.get(dominant, "balanced")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "active": True,
            "owner": self.owner_name,
            "perspectives": list(self.perspectives.keys()),
            "interactions_processed": self.interactions_processed,
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "perspective_weights": self.perspective_weights,
            "perspective_activations": {
                name: p.activation_count
                for name, p in self.perspectives.items()
            }
        }
    
    def adjust_perspective_weights(self, adjustment: Dict[str, Any]) -> None:
        """Adjust perspective weights dynamically"""
        perspective = adjustment.get("perspective")
        change = adjustment.get("adjustment", 0)
        
        if perspective in self.perspectives:
            new_weight = max(0.05, min(0.50, self.perspective_weights[perspective] + change))
            self.perspective_weights[perspective] = new_weight
            self.perspectives[perspective].weight = new_weight
