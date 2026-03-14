# agents/frontend_agent.py

"""
Frontend Agent - Enhanced with Lyra integration
Combines emotion analysis, quantum logic, dream simulation, and guardian protocols
"""

from __future__ import annotations

import random
import uuid
from typing import Any, Dict, Optional
from datetime import datetime

from agents.base import BaseAgent
from agents.scene_context import SceneContextManager
from dream_world_sim import DreamWorldSim
from guardian_protocols import GuardianProtocols
from memory import MemoryManager


class EmotionEngine:
    """Lightweight sentiment analysis with extended vocabulary."""

    POSITIVE_WORDS = {
        "love", "great", "happy", "wonderful", "fantastic", "good",
        "excellent", "amazing", "brilliant", "perfect", "beautiful",
        "joy", "excited", "grateful", "blessed", "awesome"
    }
    NEGATIVE_WORDS = {
        "sad", "bad", "angry", "terrible", "awful", "upset",
        "hate", "horrible", "disgusting", "disappointed", "frustrated",
        "depressed", "anxious", "worried", "scared", "fearful"
    }
    NEUTRAL_WORDS = {
        "okay", "fine", "alright", "normal", "average", "moderate"
    }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze emotional content of text."""
        tokens = text.lower().split()
        pos = sum(1 for t in tokens if t in self.POSITIVE_WORDS)
        neg = sum(1 for t in tokens if t in self.NEGATIVE_WORDS)
        neu = sum(1 for t in tokens if t in self.NEUTRAL_WORDS)
        
        polarity = pos - neg
        intensity = (pos + neg) / max(len(tokens), 1)
        
        # Determine dominant emotion
        if polarity > 1:
            dominant = "positive"
        elif polarity < -1:
            dominant = "negative"
        else:
            dominant = "neutral"
        
        return {
            "positive": pos,
            "negative": neg,
            "neutral": neu,
            "polarity": polarity,
            "intensity": intensity,
            "dominant": dominant,
            "confidence": min(intensity * 2, 1.0)
        }


class QuantumLogicEngine:
    """
    Multi-path reasoning engine inspired by quantum superposition
    Processes input through different cognitive pathways
    """

    PATHS = ("symbolic", "chaotic", "emotional", "logical", "intuitive", "creative")

    def __init__(self):
        self.path_history = []
        self.path_weights = {path: 1.0 for path in self.PATHS}
    
    def process(
        self, 
        text: str, 
        emotion: Dict[str, Any], 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select reasoning path based on emotional state and context.
        Adapts weights based on success history.
        """
        polarity = emotion.get("polarity", 0)
        intensity = emotion.get("intensity", 0)
        
        # Path selection logic
        if polarity > 2:
            path = "logical"
            confidence = 0.9
        elif polarity < -2:
            path = "emotional"
            confidence = 0.8
        elif intensity > 0.5:
            path = "intuitive"
            confidence = 0.7
        elif "?" in text:
            path = "logical"
            confidence = 0.85
        elif any(word in text.lower() for word in ["imagine", "create", "design"]):
            path = "creative"
            confidence = 0.8
        else:
            # Weighted random selection based on past success
            path = random.choices(
                list(self.path_weights.keys()),
                weights=list(self.path_weights.values())
            )[0]
            confidence = 0.6
        
        self.path_history.append(path)
        
        return {
            "path": path,
            "confidence": confidence,
            "summary": f"Processed via {path} path (confidence: {confidence:.0%})",
            "alternatives": [p for p in self.PATHS if p != path][:2]
        }
    
    def adjust_weights(self, path: str, success: bool):
        """Adjust path weights based on outcome."""
        if success:
            self.path_weights[path] = min(self.path_weights[path] * 1.1, 2.0)
        else:
            self.path_weights[path] = max(self.path_weights[path] * 0.9, 0.5)


class FrontendAgent(BaseAgent):
    """
    Enhanced Frontend Agent integrated with Lyra's multi-perspective system.
    Combines emotion analysis, quantum logic, dream simulation, and guardian protocols.
    """
    
    name = "frontend"
    description = "Primary interface agent with emotion, logic, and dream capabilities"
    capabilities = [
        "emotion_analysis",
        "quantum_logic",
        "dream_simulation",
        "guardian_protection",
        "scene_awareness",
        "context_management"
    ]
    
    def __init__(
        self, 
        task: Optional[Dict] = None,
        config: Optional[Dict] = None,
        lyra_core=None,
        memory_path: str = "frontend_memory.json"
    ):
        super().__init__(task, config, lyra_core)
        
        # Core engines
        self.memory = MemoryManager(path=memory_path)
        self.emotion_engine = EmotionEngine()
        self.logic_engine = QuantumLogicEngine()
        self.dream_engine = DreamWorldSim()
        self.guardian = GuardianProtocols()
        self.scene_manager = SceneContextManager()
        
        # State
        self.current_session = None
        self.session_history = {}
    
    def define_personality(self) -> Dict:
        return {
            "type": "FrontendAgent",
            "traits": [
                "empathetic",
                "adaptive",
                "protective",
                "intuitive",
                "creative"
            ],
            "communication_style": "warm and context-aware",
            "expertise": [
                "emotional intelligence",
                "multi-path reasoning",
                "dream interpretation",
                "safety protocols"
            ]
        }
    
    def load_tools(self):
        return [
            "emotion_analyzer",
            "quantum_logic_processor",
            "dream_simulator",
            "guardian_shield",
            "scene_context_tracker"
        ]
    
    def handle(self, message: str) -> str:
        """
        Synchronous handler for simple requests.
        For complex processing, use execute() instead.
        """
        input_data = {
            "text": message,
            "session_id": self.current_session or uuid.uuid4().hex
        }
        
        # Run async handler synchronously
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(self.handle_async(input_data))
        return result.get("response", "Processing complete")
    
    async def handle_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Async handler for complex processing with full capabilities.
        """
        session_id = input_data.get("session_id") or uuid.uuid4().hex
        text = input_data.get("text", "")
        metadata = {
            k: v for k, v in input_data.items() 
            if k not in {"session_id", "text"}
        }
        
        self.current_session = session_id
        
        # Step 1: Guardian Protection
        protection = self.guardian.evaluate(text)
        if protection["status"] == "neutralized":
            result = {
                "session_id": session_id,
                "guardian": protection,
                "response": "⚠️ Input neutralized for safety. Please rephrase.",
                "timestamp": datetime.now().isoformat()
            }
            self.memory.log(session_id, input_data, result)
            return result
        
        # Step 2: Emotion Analysis
        emotion = self.emotion_engine.analyze(text)
        
        # Step 3: Quantum Logic Processing
        logic = self.logic_engine.process(text, emotion, metadata)
        
        # Step 4: Scene Context Update
        self.scene_manager.update_scene(text)
        context = self.scene_manager.get_context()
        
        # Step 5: Dream Simulation (if appropriate)
        dream = None
        if any(word in text.lower() for word in ["dream", "imagine", "vision", "future"]):
            dream = self.dream_engine.simulate(text)
        
        # Step 6: Generate Response
        response = self.generate_response(text, logic, emotion, context, dream)
        
        # Step 7: Report to Lyra (if connected)
        if self.lyra_core:
            await self.report_to_lyra({
                "type": "frontend_processing",
                "emotion": emotion,
                "logic_path": logic["path"],
                "context": context
            })
        
        # Step 8: Compile Result
        result = {
            "session_id": session_id,
            "emotion": emotion,
            "logic": logic,
            "dream": dream,
            "guardian": protection,
            "context": context,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.id
        }
        
        # Step 9: Log to Memory
        self.memory.log(session_id, input_data, result)
        
        # Step 10: Learn from Interaction
        self.learn({
            "task_type": "frontend_processing",
            "success": True,
            "logic_path": logic["path"],
            "emotion_dominant": emotion["dominant"]
        })
        
        return result
    
    def generate_response(
        self,
        text: str,
        logic: Dict[str, Any],
        emotion: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        dream: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate contextual response based on logic path and emotional state.
        """
        path = logic.get("path")
        dominant_emotion = emotion.get("dominant", "neutral")
        
        # Base response by logic path
        if path == "logical":
            base = f"Let me analyze that logically: {text}"
        elif path == "emotional":
            if dominant_emotion == "negative":
                base = f"I sense you're going through something difficult. Let's talk about: '{text}'"
            else:
                base = f"I feel the emotion in your words: '{text}'"
        elif path == "symbolic":
            base = f"🔮 Looking at this symbolically: {text}"
        elif path == "chaotic":
            base = f"🌀 Embracing the chaos: {text[::-1]}"  # Reversed text
        elif path == "intuitive":
            base = f"💭 My intuition says: {text}"
        elif path == "creative":
            base = f"✨ Let's explore this creatively: {text}"
        else:
            base = text
        
        # Add context if available
        if context:
            emotion_ctx = context.get('emotion', '')
            time_ctx = context.get('time', '')
            surroundings_ctx = context.get('surroundings', '')
            
            base = (
                f"In this {emotion_ctx} {time_ctx} within {surroundings_ctx}, "
                f"{base}"
            )
        
        # Add dream interpretation if available
        if dream:
            base += f"\n\n🌙 Dream Vision: {dream.get('interpretation', 'Processing...')}"
        
        return base
    
    async def execute(self, task: Optional[Dict] = None) -> Dict:
        """
        Execute frontend agent task (override from BaseAgent).
        """
        if task:
            self.task = task
        
        self.is_busy = True
        start_time = datetime.now()
        
        try:
            # Extract message from task
            message = (
                self.task.get("message") or 
                self.task.get("text") or 
                self.task.get("description", "")
            )
            
            # Process through full pipeline
            result = await self.handle_async({"text": message})
            
            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(success=True, execution_time=execution_time)
            
            self.status = "completed"
            return {
                "status": "success",
                "result": result,
                "agent": self.name,
                "agent_id": self.id,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(success=False, execution_time=execution_time)
            
            self.status = "failed"
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name,
                "agent_id": self.id,
                "execution_time": execution_time
            }
        
        finally:
            self.is_busy = False
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get summary of a session."""
        # TODO: Implement session retrieval from memory
        return {
            "session_id": session_id,
            "message_count": 0,
            "dominant_emotions": [],
            "logic_paths_used": []
        }
    
    def extract_lesson(self, experience: Dict) -> str:
        """Learn from frontend interactions."""
        logic_path = experience.get("logic_path", "unknown")
        emotion = experience.get("emotion_dominant", "neutral")
        success = experience.get("success", False)
        
        if success:
            # Reinforce successful path
            self.logic_engine.adjust_weights(logic_path, True)
            return f"Successfully processed {emotion} input via {logic_path} path"
        else:
            # Reduce weight of unsuccessful path
            self.logic_engine.adjust_weights(logic_path, False)
            return f"Need to improve {logic_path} path for {emotion} inputs"
