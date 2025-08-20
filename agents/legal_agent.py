from agents.base import BaseAgent


class LegalAgent(BaseAgent):
    name = "legal"

    def handle(self, message: str) -> str:
        return f"[LegalAgent] (demo) Legal research: {message}"
