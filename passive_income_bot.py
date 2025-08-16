"""Automated dynamic pricing example.

This script periodically runs the PricingAgent with sample metrics and
logs the resulting price recommendations to ``pricing_log.json``. It is a
simple demonstration of how automated pricing could help generate
revenue while you sleep. No real profit is guaranteed.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List

from controller import AgentController

LOG_FILE = Path("pricing_log.json")


def load_history() -> List[Dict[str, float]]:
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text())
        except json.JSONDecodeError:
            return []
    return []


def save_history(history: List[Dict[str, float]]) -> None:
    LOG_FILE.write_text(json.dumps(history, indent=2))


async def generate_price(ctrl: AgentController, metrics: Dict[str, int]) -> float:
    result = await ctrl.route("pricing", {"metrics": metrics})
    return float(result.get("price", 0.0))


async def main() -> None:
    ctrl = AgentController(enable_memory=True)
    metrics_samples = [
        {
            "timeOnPage": 120,
            "pageViews": 3,
            "timeOfDay": 23,
            "dayOfWeek": 5,
            "location": 2,
            "deviceType": 2,
            "returningVisitor": 1,
        },
        {
            "timeOnPage": 45,
            "pageViews": 2,
            "timeOfDay": 9,
            "dayOfWeek": 1,
            "location": 6,
            "deviceType": 1,
            "returningVisitor": 0,
        },
    ]

    history = load_history()

    for metrics in metrics_samples:
        price = await generate_price(ctrl, metrics)
        history.append(
            {
                "timestamp": time.time(),
                "metrics": metrics,
                "price": price,
            }
        )
        save_history(history)
        # Sleep between calculations to mimic periodic updates
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
