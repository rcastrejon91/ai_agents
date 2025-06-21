import re
from fastapi import Body
from core.base_agent import BaseAIAgent


def simple_summarize(text: str, sentences: int = 2) -> str:
    parts = re.split(r"(?<=[.!?]) +", text)
    return " ".join(parts[:sentences])


class LegalAgent(BaseAIAgent):
    def __init__(self, port: int = 8003):
        super().__init__("legal", port)

    def setup_routes(self):
        @self.app.post("/summarize")
        async def summarize(data: dict = Body(...)):
            text = data.get("text")
            if not text:
                return {"error": "'text' is required"}
            summary = simple_summarize(str(text))
            return {"summary": summary}

    async def process_task(self, input_data: dict):
        return await self.app.router.routes[0].endpoint(input_data)

if __name__ == "__main__":
    LegalAgent().run()
