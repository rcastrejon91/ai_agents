from agents.base import BaseAgent


class FinanceAgent(BaseAgent):
    name = "finance"

    def handle(self, message: str) -> str:
        return f"[FinanceAgent] (demo) Analyzing: {message}"
