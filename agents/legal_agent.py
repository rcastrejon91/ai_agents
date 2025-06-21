from __future__ import annotations

from typing import Dict, Any
from core.base_agent import BaseAIAgent


class LegalAgent(BaseAIAgent):
    """Agent providing basic clause extraction from contracts."""

    def __init__(self) -> None:
        super().__init__(industry="legal", port=8002)

    def setup_routes(self) -> None:
        pass

    async def process_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        contract: str = input_data.get("contract", "")
        keyword: str = input_data.get("keyword", "").lower()
        if not contract or not keyword:
            return {"clauses": []}

        clauses = [line.strip() for line in contract.splitlines() if keyword in line.lower()]
        return {"clauses": clauses}
