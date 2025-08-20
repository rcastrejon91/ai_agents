from agents import REGISTRY


class AgentManager:
    def __init__(self):
        self.agents = {name: cls() for name, cls in REGISTRY.items()}

    def dispatch(self, agent_name: str, message: str) -> str:
        agent = self.agents.get(agent_name.lower())
        if not agent:
            return f"❌ Unknown agent '{agent_name}'"
        return agent.handle(message)
