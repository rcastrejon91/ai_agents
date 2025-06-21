from __future__ import annotations

from typing import Dict, Any
from core.base_agent import BaseAIAgent


class FinanceAgent(BaseAIAgent):
    """Simple finance agent that calculates profit or loss."""

    def __init__(self) -> None:
        super().__init__(industry="finance", port=8001)

    def setup_routes(self) -> None:
        # This example agent does not expose its own API routes yet.
        pass

    async def process_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        revenue = float(input_data.get("revenue", 0))
        expenses = float(input_data.get("expenses", 0))
        profit = revenue - expenses
        return {"profit": profit}
