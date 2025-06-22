"""Guardian System Modules
=======================

Provides basic security toggling, event logging, and emotional profiling.
"""

from __future__ import annotations

import hashlib


class GuardianMode:
    """Toggle CIA mode on or off."""

    def __init__(self) -> None:
        self.cia_mode = False

    def activate_cia_mode(self) -> str:
        self.cia_mode = True
        return "\U0001F6E1\uFE0F CIA Mode Activated: Threat detection + forensic tracking live."

    def deactivate_cia_mode(self) -> str:
        self.cia_mode = False
        return "\U0001F54A\uFE0F CIA Mode Deactivated: Returning to compassionate companion state."


class GuardianDashboard:
    """Track status, threat level, and a simple log."""

    def __init__(self) -> None:
        self.status = "idle"
        self.threat_level = "low"
        self.logs: list[str] = []

    def update_status(self, status: str) -> str:
        self.status = status
        self.logs.append(f"Status updated to: {status}")
        return f"Dashboard status: {status}"

    def set_threat_level(self, level: str) -> str:
        self.threat_level = level
        self.logs.append(f"Threat level set to: {level}")
        return f"Threat level: {level}"

    def get_logs(self) -> list[str]:
        return self.logs


class ForensicLogger:
    """Store key events with their details."""

    def __init__(self) -> None:
        self.records: list[dict[str, str]] = []

    def log_event(self, event_type: str, details: str) -> str:
        entry = {"type": event_type, "details": details}
        self.records.append(entry)
        return f"Logged event: {event_type}"

    def get_all_logs(self) -> list[dict[str, str]]:
        return self.records


class EmotionalProfile:
    """Capture emotional states over time."""

    def __init__(self, user_name: str) -> None:
        self.user_name = user_name
        self.emotion_states: list[dict[str, int | str]] = []

    def add_emotion_state(self, emotion: str, intensity: int) -> str:
        self.emotion_states.append({"emotion": emotion, "intensity": intensity})
        return f"Emotion '{emotion}' recorded with intensity {intensity}."

    def get_emotional_history(self) -> list[dict[str, int | str]]:
        return self.emotion_states


class EvolutionaryBiologyResponder:
    """Provide simple evolutionary biology observations."""

    def __init__(self) -> None:
        self.notes: list[str] = []

    def describe_selection_pressure(self, species: str, pressure: str) -> str:
        """Return a note about how a species may adapt to a given pressure."""
        note = (
            f"Under {pressure} pressure, {species} populations may evolve traits "
            f"that improve survival and reproduction."
        )
        self.notes.append(note)
        return note

    def get_notes(self) -> list[str]:
        return self.notes


class NeuralThreatResponder:
    """Simulate amygdala-like threat assessments."""

    def assess_threat(self, input_data: str) -> str:
        """Return a message signaling a high-risk pattern."""
        return "\u26a0\ufe0f High-risk pattern detected \u2013 prepping countermeasure."


class BehaviorAdaptation:
    """Track observed behaviors over time."""

    def __init__(self) -> None:
        self.patterns: list[str] = []

    def track_behavior(self, behavior: str) -> str:
        self.patterns.append(behavior)
        return f"Behavior logged: {behavior}"

    def get_history(self) -> list[str]:
        return self.patterns


def tag_event_with_dna(event: str) -> str:
    """Return a unique DNA-style hash for the given event."""
    return hashlib.sha256(event.encode()).hexdigest()


class EthicalGatekeeper:
    """Allow selective locking of functions based on ethics."""

    def __init__(self) -> None:
        self.locked_functions: list[str] = []

    def toggle_lock(self, func_name: str, state: bool) -> None:
        if state:
            if func_name not in self.locked_functions:
                self.locked_functions.append(func_name)
        else:
            if func_name in self.locked_functions:
                self.locked_functions.remove(func_name)

    def is_locked(self, func_name: str) -> bool:
        return func_name in self.locked_functions


if __name__ == "__main__":
    guardian = GuardianMode()
    dashboard = GuardianDashboard()
    forensics = ForensicLogger()
    emotion_tracker = EmotionalProfile("Ricky")
    evo_responder = EvolutionaryBiologyResponder()
    threat_responder = NeuralThreatResponder()
    behavior_tracker = BehaviorAdaptation()
    gatekeeper = EthicalGatekeeper()

    demo_output = [
        guardian.activate_cia_mode(),
        dashboard.update_status("scanning environment"),
        dashboard.set_threat_level("medium"),
        forensics.log_event("anomaly_detected", "Unusual IP address access detected."),
        emotion_tracker.add_emotion_state("focused", 8),
        evo_responder.describe_selection_pressure("finch", "drought"),
        threat_responder.assess_threat("unusual pattern"),
        behavior_tracker.track_behavior("evasive action taken"),
        tag_event_with_dna("Unusual IP address access detected."),
        str(gatekeeper.is_locked("assess_threat")),
    ]
    for line in demo_output:
        print(line)
