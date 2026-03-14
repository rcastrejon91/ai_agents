"""
core/agent_registry.py - Central Agent Registry

Manages all AI agents and routes requests to them.
"""

import importlib
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Central registry for all AI agents"""
    
    def __init__(self):
        self.agents = {}
        self._load_agents()
    
    def _load_agents(self):
        """Load all available agents"""
        
        # Define available agents
        agent_modules = {
            "finance": "agents.finance_agent.FinanceAgent",
            "legal": "agents.legal_agent.LegalAgent",
            "healthcare": "agents.healthcare_agent.HealthcareAgent",
            "real_estate": "agents.real_estate_agent.RealEstateAgent",
            "retail": "agents.retail_agent.RetailAgent",
            "pricing": "agents.pricing_agent.PricingAgent",
            "concierge": "agents.concierge_agent.ConciergeAgent",
        }
        
        for agent_id, module_path in agent_modules.items():
            try:
                module_name, class_name = module_path.rsplit(".", 1)
                module = importlib.import_module(module_name)
                agent_class = getattr(module, class_name)
                
                # Instantiate agent
                agent_instance = agent_class()
                
                self.agents[agent_id] = {
                    "id": agent_id,
                    "name": class_name,
                    "instance": agent_instance,
                    "status": "active",
                    "calls": 0
                }
                
                logger.info(f"✅ Loaded agent: {agent_id}")
                
            except Exception as e:
                logger.warning(f"⚠️  Could not load agent {agent_id}: {e}")
                self.agents[agent_id] = {
                    "id": agent_id,
                    "name": agent_id.title(),
                    "instance": None,
                    "status": "unavailable",
                    "calls": 0
                }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [
            {
                "id": agent_id,
                "name": agent_data["name"],
                "status": agent_data["status"],
                "calls": agent_data["calls"]
            }
            for agent_id, agent_data in self.agents.items()
        ]
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get specific agent info"""
        return self.agents.get(agent_id)
    
    async def call_agent(self, agent_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific agent with request data"""
        
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_data = self.agents[agent_id]
        
        if agent_data["status"] != "active":
            raise RuntimeError(f"Agent {agent_id} is not active")
        
        # Increment call counter
        agent_data["calls"] += 1
        
        # Call agent
        try:
            agent_instance = agent_data["instance"]
            
            # Try different method names agents might use
            if hasattr(agent_instance, "process"):
                result = await agent_instance.process(request_data)
            elif hasattr(agent_instance, "handle"):
                result = await agent_instance.handle(request_data)
            elif hasattr(agent_instance, "execute"):
                result = await agent_instance.execute(request_data)
            else:
                # Fallback - just return agent info
                result = {
                    "agent": agent_id,
                    "message": f"{agent_data['name']} received request",
                    "request": request_data
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error calling agent {agent_id}: {e}")
            raise RuntimeError(f"Agent {agent_id} error: {str(e)}")


# Global instance
agent_registry = AgentRegistry()
