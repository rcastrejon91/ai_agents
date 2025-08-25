from agents import REGISTRY


class AgentManager:
    def __init__(self):
        self.agents = {name: cls() for name, cls in REGISTRY.items()}

    def dispatch(self, agent_name: str, message: str) -> str:
        agent = self.agents.get(agent_name.lower())
        if not agent:
            return f"❌ Unknown agent '{agent_name}'"
        return agent.handle(message)


"""Agent Manager for handling agent dispatch."""


class AgentManager:
    def __init__(self):
        self.agents = {}

    def dispatch(self, agent_name: str, query: str) -> str:
        """Dispatch a query to the specified agent."""
        # Simple routing logic
        if agent_name == "finance":
            return f"Finance Agent: Processing query about {query}"
        elif agent_name == "legal":
            return f"Legal Agent: Analyzing {query}"
        elif agent_name == "healthcare":
            return f"Healthcare Agent: Reviewing {query}"
        elif agent_name == "retail":
            return f"Retail Agent: Handling {query}"
        elif agent_name == "concierge":
            return f"Concierge Agent: Assisting with {query}"
        else:
            return f"Unknown agent {agent_name}. Query: {query}"
