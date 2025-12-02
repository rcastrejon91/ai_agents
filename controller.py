#!/usr/bin/env python3
# Controller Script - Manages AI agent operations

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("controller")

# Try to import from core directory
try:
    from core.agent_registry import agent_registry
except ImportError:
    logger.error(
        "Could not import agent_registry. Make sure core/agent_registry.py exists."
    )

    # Create a simple stub for testing
    class AgentRegistryStub:
        async def call_agent(self, agent_id, request_data):
            return {"error": "Agent registry not available"}

        def register_agent(self, agent_id, host, port):
            logger.info(f"Would register agent {agent_id} at {host}:{port}")
            return True

        def get_agent(self, agent_id):
            return None

        def list_agents(self):
            return []

    agent_registry = AgentRegistryStub()


class AgentController:
    """Controller for managing and routing requests to agents."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def register_agents(self) -> None:
        """Register all agents with the registry."""
        agent_configs = [
            {"id": "finance-agent", "host": "localhost", "port": 8001},
            {"id": "legal-agent", "host": "localhost", "port": 8002},
            {"id": "retail-agent", "host": "localhost", "port": 8003},
            {"id": "pricing-agent", "host": "localhost", "port": 8004},
            {"id": "healthcare-agent", "host": "localhost", "port": 8005},
            {"id": "real-estate-agent", "host": "localhost", "port": 8006},
        ]

        for config in agent_configs:
            success = agent_registry.register_agent(
                config["id"], config["host"], config["port"]
            )
            if success:
                self.logger.info(f"Registered agent: {config['id']}")
            else:
                self.logger.warning(f"Failed to register agent: {config['id']}")

    async def route(
        self, agent_id: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route a request to the specified agent."""
        return await agent_registry.call_agent(agent_id, request_data)


async def start_agents():
    """Start all agents in separate processes."""
    import subprocess

    agent_modules = [
        "agents/finance_agent.py",
        "agents/legal_agent.py",
        "agents/retail_agent.py",
        "agents/pricing_agent.py",
        "agents/healthcare_agent.py",
        "agents/real_estate_agent.py",
    ]

    processes = []
    for module in agent_modules:
        if os.path.exists(module):
            process = subprocess.Popen([sys.executable, module])
            processes.append((module, process))
            logger.info(f"Started agent: {module}")
        else:
            logger.warning(f"Agent module not found: {module}")

    return processes


async def test_agents():
    """Test all registered agents."""
    controller = AgentController()
    controller.register_agents()

    # Test pricing agent
    try:
        pricing_result = await controller.route(
            "pricing-agent",
            {
                "query": "Calculate price",
                "parameters": {
                    "session_id": "test-session",
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
            },
        )
        print(f"Pricing Agent Result: {json.dumps(pricing_result, indent=2)}")
    except Exception as e:
        print(f"Error testing pricing agent: {str(e)}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI Agent Controller")
    parser.add_argument("--start", action="store_true", help="Start all agents")
    parser.add_argument("--test", action="store_true", help="Test all agents")
    parser.add_argument(
        "--register", action="store_true", help="Register agents with registry"
    )
    args = parser.parse_args()

    # Run the appropriate action
    if args.start:
        processes = asyncio.run(start_agents())
        try:
            # Keep the main process running
            print("Agents started. Press Ctrl+C to stop.")
            while True:
                asyncio.run(asyncio.sleep(1))
        except KeyboardInterrupt:
            # Terminate all agent processes on Ctrl+C
            print("\nStopping all agents...")
            for module, process in processes:
                print(f"Stopping {module}...")
                process.terminate()
            print("All agents stopped")
    elif args.test:
        asyncio.run(test_agents())
    elif args.register:
        controller = AgentController()
        controller.register_agents()
        print("Agents registered")
    else:
        print("No action specified. Use --start, --test, or --register")
        parser.print_help()
