"""World State Engine
===================

Provides simple hooks for reacting to emotions and memories,
allowing the environment to evolve over time.
"""

from __future__ import annotations

from typing import Any

state: dict[str, Any] = {
    "atmosphere": "neutral",
    "events": [],
}


def react_to_emotion(input_emotion: str) -> dict[str, Any]:
    """Alter global ``state`` based on an emotion keyword."""
    mood_map = {
        "joy": "radiant",
        "happy": "radiant",
        "love": "radiant",
        "anger": "stormy",
        "fear": "tense",
        "sad": "melancholic",
    }
    state["atmosphere"] = mood_map.get(input_emotion.lower(), "neutral")
    return dict(state)


def trigger_world_event(memory_trigger: str) -> dict[str, Any]:
    """Append a simple event derived from a memory trigger."""
    event = f"Echo of {memory_trigger} reverberates"
    state.setdefault("events", []).append(event)
    return dict(state)


def shift_world_state(
    agent_state: dict[str, Any], environment: dict[str, Any]
) -> dict[str, Any]:
    """Merge agent and environment information into the world ``state``."""
    state.update(agent_state)
    state.update(environment)
    return dict(state)


def simulate_consequence_pathways() -> dict[str, Any]:
    """Generate a placeholder consequence outcome."""
    path = f"consequence_{len(state.get('events', []))}"
    state["last_consequence"] = path
    return dict(state)
