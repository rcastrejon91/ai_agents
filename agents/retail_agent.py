from __future__ import annotations

from typing import Any

from core.base_agent import BaseAIAgent


class RetailAgent(BaseAIAgent):
    """Agent to suggest inventory reorder amounts."""

    def __init__(self) -> None:
        super().__init__(industry="retail", port=8003)

    def setup_routes(self) -> None:
        pass

    async def process_task(self, input_data: dict[str, Any]) -> dict[str, Any]:
        stock = int(input_data.get("stock", 0))
        sales = int(input_data.get("sales_last_week", 0))
        threshold = int(input_data.get("threshold", 10))
        avg_daily_sales = sales / 7
        suggested = max(threshold - stock, int(avg_daily_sales * 7) - stock)
        if suggested < 0:
            suggested = 0
        return {"reorder_quantity": suggested}
