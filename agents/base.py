class BaseAgent:
    name = "base"

    def handle(self, message: str) -> str:
        raise NotImplementedError
