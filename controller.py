from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, Dict

from agents import (
    FinanceAgent,
    HealthcareAgent,
    LegalAgent,
    PricingAgent,
    RealEstateAgent,
    RetailAgent,
)


class AgentController:
    """Routes requests to the appropriate agent."""

    def __init__(self, enable_memory: bool = False) -> None:
        self.agents = {
            "finance": FinanceAgent(),
            "legal": LegalAgent(),
            "retail": RetailAgent(),
            "healthcare": HealthcareAgent(),
            "real_estate": RealEstateAgent(),
            "pricing": PricingAgent(),
        }
        self.logger = logging.getLogger(self.__class__.__name__)
        self.memory = None
        if enable_memory:
            from memory import MemoryManager

            self.memory = MemoryManager()

    async def route(self, agent_name: str, input_data: Dict[str, Any]) -> Any:
        agent = self.agents.get(agent_name)
        if agent is None:
            self.logger.error("Unknown agent requested: %s", agent_name)
            raise ValueError(f"Unknown agent '{agent_name}'")
        if not isinstance(input_data, dict):
            self.logger.error("Input data for %s must be a dictionary", agent_name)
            raise ValueError("Input data must be a dictionary")
        try:
            session_id = input_data.get("session_id")
            if not session_id:
                session_id = uuid.uuid4().hex

            full_input = dict(input_data)
            full_input.setdefault("session_id", session_id)

            result = await agent.process_task(full_input)
            self.logger.info("Agent %s processed task", agent_name)
            if isinstance(result, dict):
                result.setdefault("session_id", session_id)
            if self.memory:
                # persist complete turn history
                self.memory.log(session_id, full_input, result)
            return result
        except Exception:
            self.logger.exception("Agent %s failed to process task", agent_name)
            raise

    def available_agents(self) -> Dict[str, str]:
        return {name: agent.industry for name, agent in self.agents.items()}


async def _memory_test() -> None:
    """Simple in-process test for the memory manager."""
    ctrl = AgentController(enable_memory=True)
    session_id = uuid.uuid4().hex
    await ctrl.route(
        "finance", {"session_id": session_id, "revenue": 100, "expenses": 50}
    )
    await ctrl.route(
        "finance", {"session_id": session_id, "revenue": 200, "expenses": 125}
    )
    await ctrl.route(
        "pricing",
        {
            "session_id": session_id,
            "metrics": {
                "timeOnPage": 120,
                "pageViews": 3,
                "timeOfDay": 14,
                "dayOfWeek": 2,
                "location": 5,
                "deviceType": 3,
                "returningVisitor": 1,
            },
        },
    )
    history = ctrl.memory.recall(session_id) if ctrl.memory else []
    print(json.dumps(history, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agent Controller")
    parser.add_argument("--test-memory", action="store_true", help="run memory test")
    args = parser.parse_args()

    if args.test_memory:
        asyncio.run(_memory_test())
