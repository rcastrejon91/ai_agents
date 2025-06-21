from fastapi import Body
from core.base_agent import BaseAIAgent


class HealthcareAgent(BaseAIAgent):
    def __init__(self, port: int = 8002):
        super().__init__("healthcare", port)

    def setup_routes(self):
        @self.app.post("/bmi")
        async def bmi(data: dict = Body(...)):
            weight = data.get("weight")
            height = data.get("height")
            if weight is None or height is None:
                return {"error": "'weight' and 'height' are required"}
            try:
                bmi_val = float(weight) / (float(height) ** 2)
            except (ValueError, ZeroDivisionError):
                return {"error": "Invalid numeric values"}
            return {"bmi": bmi_val}

    async def process_task(self, input_data: dict):
        return await self.app.router.routes[0].endpoint(input_data)

if __name__ == "__main__":
    HealthcareAgent().run()
