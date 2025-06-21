from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from agents import (
    FinanceAgent,
    LegalAgent,
    RetailAgent,
    HealthcareAgent,
    RealEstateAgent,
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
        }
        self.logger = logging.getLogger(self.__class__.__name__)
        self.memory = None
        if enable_memory:
            from memory import Memory

            self.memory = Memory()

    async def route(self, agent_name: str, input_data: Dict[str, Any]) -> Any:
        agent = self.agents.get(agent_name)
        if agent is None:
            self.logger.error("Unknown agent requested: %s", agent_name)
            raise ValueError(f"Unknown agent '{agent_name}'")
        if not isinstance(input_data, dict):
            self.logger.error("Input data for %s must be a dictionary", agent_name)
            raise ValueError("Input data must be a dictionary")
        try:
            result = await agent.process_task(input_data)
            self.logger.info("Agent %s processed task", agent_name)
            if self.memory:
                self.memory.record(agent_name, input_data, result)
            return result
        except Exception:
            self.logger.exception("Agent %s failed to process task", agent_name)
            raise

    def available_agents(self) -> Dict[str, str]:
        return {name: agent.industry for name, agent in self.agents.items()}
