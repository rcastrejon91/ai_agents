"""Guardian System Modules
=======================

Provides basic security toggling, event logging, and emotional profiling.
"""

from __future__ import annotations


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


if __name__ == "__main__":
    guardian = GuardianMode()
    dashboard = GuardianDashboard()
    forensics = ForensicLogger()
    emotion_tracker = EmotionalProfile("Ricky")

    demo_output = [
        guardian.activate_cia_mode(),
        dashboard.update_status("scanning environment"),
        dashboard.set_threat_level("medium"),
        forensics.log_event("anomaly_detected", "Unusual IP address access detected."),
        emotion_tracker.add_emotion_state("focused", 8),
    ]
    for line in demo_output:
        print(line)
