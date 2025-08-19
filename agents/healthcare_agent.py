from __future__ import annotations

from typing import Any

from core.base_agent import BaseAIAgent


class HealthcareAgent(BaseAIAgent):
    """Placeholder for future healthcare-related logic."""

    def __init__(self) -> None:
        super().__init__(industry="healthcare", port=8004)

    def setup_routes(self) -> None:
        pass

    async def process_task(self, input_data: dict[str, Any]) -> dict[str, Any]:
        # Future implementation could analyze symptoms or medical records.
        return {"message": "Healthcare agent functionality not yet implemented"}
