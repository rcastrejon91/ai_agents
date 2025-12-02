# agents/pricing_agent.py
from __future__ import annotations

import random
from typing import Any, Dict, List

from analytics import analytics_store
from core.enhanced_agent import AgentConfig, EnhancedAIAgent


class PricingAgent(EnhancedAIAgent):
    """Agent implementing a simple dynamic pricing algorithm."""

    def __init__(self) -> None:
        config = AgentConfig(
            name="Dynamic Pricing Agent",
            description="Calculates dynamic prices based on user engagement metrics",
            version="1.0.0",
            industry="pricing",
            debug_mode=True,
        )
        super().__init__(config=config, port=8004)

    def setup_routes(self) -> None:
        # No custom FastAPI routes for this example
        pass

    async def process_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Extract query if it exists, otherwise use empty string
        query = input_data.get("query", "")

        # Get session ID from context or parameters
        context = input_data.get("context", {})
        parameters = input_data.get("parameters", {})
        session_id = str(
            context.get("session_id", parameters.get("session_id", "default"))
        )

        # Get metrics from context or parameters
        metrics = context.get("metrics", parameters.get("metrics", {}))

        if metrics:
            analytics_store.log_metrics(session_id, metrics)
            self.logger.info(f"Logged metrics for session {session_id}")

        # Get metrics or generate dummy ones
        metrics = analytics_store.get_metrics(session_id) or self._dummy_metrics()
        price = self._calculate_price(metrics)

        explanation = self._generate_price_explanation(metrics, price)

        return {"price": price, "metrics": metrics, "explanation": explanation}

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

    def _generate_price_explanation(self, metrics: Dict[str, Any], price: float) -> str:
        """Generate a human-readable explanation of the price calculation."""
        factors = {
            "timeOnPage": {"weight": 0.2, "max": 300, "name": "time spent on page"},
            "pageViews": {"weight": 0.15, "max": 5, "name": "number of page views"},
            "timeOfDay": {"weight": 0.1, "max": 24, "name": "time of day"},
            "dayOfWeek": {"weight": 0.15, "max": 7, "name": "day of week"},
            "location": {"weight": 0.2, "max": 10, "name": "location"},
            "deviceType": {"weight": 0.1, "max": 3, "name": "device type"},
            "returningVisitor": {
                "weight": 0.1,
                "max": 1,
                "name": "returning visitor status",
            },
        }

        # Calculate impact of each factor
        factor_impacts = []
        for factor, data in factors.items():
            value = float(metrics.get(factor, 0))
            normalized = min(value / data["max"], 1.0)
            impact = normalized * data["weight"]
            factor_impacts.append((factor, impact, data["name"]))

        # Sort by impact (descending)
        factor_impacts.sort(key=lambda x: x[1], reverse=True)

        # Generate explanation using the top 2 factors
        top_factors = factor_impacts[:2]

        explanation = f"The price of ${price} was calculated based primarily on "
        explanation += f"{top_factors[0][2]}"
        explanation += f" and {top_factors[1][2]}."

        return explanation

    def get_capabilities(self) -> List[str]:
        return ["dynamic_pricing", "user_metrics_analysis", "price_optimization"]


if __name__ == "__main__":
    # Create and run the agent
    agent = PricingAgent()
    agent.run()
