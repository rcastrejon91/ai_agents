from fastapi import Body
from core.base_agent import BaseAIAgent


class RetailAgent(BaseAIAgent):
    def __init__(self, port: int = 8004):
        super().__init__("retail", port)

    def setup_routes(self):
        @self.app.post("/discount")
        async def discount(data: dict = Body(...)):
            price = data.get("price")
            percentage = data.get("percentage")
            if price is None or percentage is None:
                return {"error": "'price' and 'percentage' are required"}
            try:
                final_price = float(price) * (1 - float(percentage) / 100)
            except ValueError:
                return {"error": "Invalid numeric values"}
            return {"discounted_price": final_price}

    async def process_task(self, input_data: dict):
        return await self.app.router.routes[0].endpoint(input_data)

if __name__ == "__main__":
    RetailAgent().run()
