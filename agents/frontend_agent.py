from __future__ import annotations

import random
import uuid
from typing import Any

from agents.scene_context import SceneContextManager
from dream_world_sim import DreamWorldSim
from guardian_protocols import GuardianProtocols
from memory import MemoryManager


class EmotionEngine:
    """Lightweight placeholder for sentiment analysis."""

    POSITIVE_WORDS = {
        "love",
        "great",
        "happy",
        "wonderful",
        "fantastic",
        "good",
    }
    NEGATIVE_WORDS = {
        "sad",
        "bad",
        "angry",
        "terrible",
        "awful",
        "upset",
    }

    def analyze(self, text: str) -> dict[str, Any]:
        tokens = text.lower().split()
        pos = sum(1 for t in tokens if t in self.POSITIVE_WORDS)
        neg = sum(1 for t in tokens if t in self.NEGATIVE_WORDS)
        polarity = pos - neg
        return {"positive": pos, "negative": neg, "polarity": polarity}


class QuantumLogicEngine:
    """Stub logic engine that chooses a processing path."""

    PATHS = ("symbolic", "chaotic", "emotional", "logical")

    def process(
        self, text: str, emotion: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Select a reasoning path based on input emotion."""
        if emotion.get("polarity", 0) > 1:
            path = "logical"
        elif emotion.get("polarity", 0) < -1:
            path = "emotional"
        else:
            path = random.choice(["symbolic", "chaotic"])
        return {"path": path, "summary": f"Processed via {path} path"}


class FrontendAgent:
    """Interface layer that connects memory, emotion and quantum logic."""

    def __init__(self, memory_path: str = "frontend_memory.json") -> None:
        self.memory = MemoryManager(path=memory_path)
        self.emotion_engine = EmotionEngine()
        self.logic_engine = QuantumLogicEngine()
        self.dream_engine = DreamWorldSim()
        self.guardian = GuardianProtocols()
        self.scene_manager = SceneContextManager()

    def generate_response(
        self,
        text: str,
        logic: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> str:
        """Return a rudimentary response based on the chosen logic path,
        optionally enriched with scene context."""
        path = logic.get("path")
        if path == "logical":
            base = f"Understood: {text}"
        elif path == "emotional":
            base = f"I sense strong feelings in: '{text}'"
        elif path == "symbolic":
            base = f"🔮 {text}"
        elif path == "chaotic":
            base = text[::-1]
        else:
            base = text

        if context:
            return (
                f"In this {context.get('emotion', '')} {context.get('time', '')} within "
                f"{context.get('surroundings', '')}, {base}"
            )
        return base

    async def handle(self, input_data: dict[str, Any]) -> dict[str, Any]:
        session_id = input_data.get("session_id") or uuid.uuid4().hex
        text = input_data.get("text", "")
        metadata = {
            k: v for k, v in input_data.items() if k not in {"session_id", "text"}
        }

        protection = self.guardian.evaluate(text)
        if protection["status"] == "neutralized":
            result = {"session_id": session_id, "guardian": protection}
            self.memory.log(session_id, input_data, result)
            return result

        emotion = self.emotion_engine.analyze(text)
        logic = self.logic_engine.process(text, emotion, metadata)
        self.scene_manager.update_scene(text)
        context = self.scene_manager.get_context()
        response = self.generate_response(text, logic, context)
        dream = self.dream_engine.simulate(text)

        result = {
            "session_id": session_id,
            "emotion": emotion,
            "logic": logic,
            "dream": dream,
            "guardian": protection,
            "context": context,
            "response": response,
        }

        self.memory.log(session_id, input_data, result)
        return result
