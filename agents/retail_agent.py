from agents.base import BaseAgent


class RetailAgent(BaseAgent):
    name = "retail"

    def handle(self, message: str) -> str:
        return f"[RetailAgent] (demo) Merch ops: {message}"
