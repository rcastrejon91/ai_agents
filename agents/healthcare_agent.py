from agents.base import BaseAgent


class HealthcareAgent(BaseAgent):
    name = "healthcare"

    def handle(self, message: str) -> str:
        return f"[HealthcareAgent] (demo) Triage: {message}"
