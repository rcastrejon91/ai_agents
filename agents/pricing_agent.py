from __future__ import annotations

import random
from typing import Any, Dict

from analytics import analytics_store
from core.base_agent import BaseAIAgent


class PricingAgent(BaseAIAgent):
    """Agent implementing a simple dynamic pricing algorithm."""

    def __init__(self) -> None:
        super().__init__(industry="pricing", port=8004)

    def setup_routes(self) -> None:
        # No custom FastAPI routes for this example
        pass

    async def process_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        session_id = str(input_data.get("session_id", "default"))

        if "metrics" in input_data:
            analytics_store.log_metrics(session_id, input_data["metrics"])

        metrics = analytics_store.get_metrics(session_id) or self._dummy_metrics()
        price = self._calculate_price(metrics)
        return {"price": price, "metrics": metrics}

    def _dummy_metrics(self) -> Dict[str, Any]:
        return {
            "timeOnPage": random.randint(0, 300),
            "pageViews": random.randint(1, 5),
            "timeOfDay": random.randint(0, 23),
            "dayOfWeek": random.randint(1, 7),
            "location": random.randint(1, 10),
            "deviceType": random.choice([1, 2, 3]),
            "returningVisitor": random.randint(0, 1),
        }

    def _calculate_price(self, metrics: Dict[str, Any]) -> float:
        base_price = 29.99
        max_price = 49.99
        min_price = 19.99
        factors = {
            "timeOnPage": {"weight": 0.2, "max": 300},
            "pageViews": {"weight": 0.15, "max": 5},
            "timeOfDay": {"weight": 0.1, "max": 24},
            "dayOfWeek": {"weight": 0.15, "max": 7},
            "location": {"weight": 0.2, "max": 10},
            "deviceType": {"weight": 0.1, "max": 3},
            "returningVisitor": {"weight": 0.1, "max": 1},
        }
        score = 0.0
        for factor, data in factors.items():
            value = float(metrics.get(factor, 0))
            normalized = min(value / data["max"], 1.0)
            score += normalized * data["weight"]

        price_range = max_price - min_price
        calculated = min_price + price_range * score
        return round(calculated // 1 + 0.99, 2)
