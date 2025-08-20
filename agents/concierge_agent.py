from agents.base import BaseAgent


class ConciergeAgent(BaseAgent):
    name = "concierge"

    def handle(self, message: str) -> str:
        return f"[ConciergeAgent] (demo) Booking: {message}"
