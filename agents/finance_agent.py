from fastapi import Body
from core.base_agent import BaseAIAgent


class FinanceAgent(BaseAIAgent):
    def __init__(self, port: int = 8001):
        super().__init__("finance", port)

    def setup_routes(self):
        @self.app.post("/roi")
        async def roi(data: dict = Body(...)):
            initial = data.get("initial")
            final = data.get("final")
            if initial is None or final is None:
                return {"error": "'initial' and 'final' are required"}
            try:
                roi_value = (float(final) - float(initial)) / float(initial) * 100
            except (ValueError, ZeroDivisionError):
                return {"error": "Invalid numeric values"}
            return {"roi": roi_value}

    async def process_task(self, input_data: dict):
        return await self.app.router.routes[0].endpoint(input_data)

if __name__ == "__main__":
    FinanceAgent().run()
