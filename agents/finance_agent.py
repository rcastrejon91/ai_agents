# agents/finance_agent.py
from typing import Dict, Any, List
from core.enhanced_agent import EnhancedAIAgent, AgentConfig

class FinanceAgent(EnhancedAIAgent):
    """Agent for financial analysis and calculations."""
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="Financial Advisor",
            description="Provides financial analysis and advice",
            version="1.0.0",
            industry="finance",
            debug_mode=True
        )
        super().__init__(config=config, port=8001)
    
    def setup_routes(self) -> None:
        # Add any custom routes here
        pass
    
    async def process_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query", "")
        context = input_data.get("context", {})
        parameters = input_data.get("parameters", {})
        
        # Extract financial data
        revenue = parameters.get("revenue", context.get("revenue", 0))
        expenses = parameters.get("expenses", context.get("expenses", 0))
        
        # Calculate profit
        profit = revenue - expenses
        margin = (profit / revenue) * 100 if revenue > 0 else 0
        
        return {
            "profit": profit,
            "margin": round(margin, 2),
            "analysis": f"Based on revenue of ${revenue} and expenses of ${expenses}, "
                      f"the profit is ${profit} with a margin of {round(margin, 2)}%."
        }
    
    def get_capabilities(self) -> List[str]:
        return ["financial_analysis", "profit_calculation", "margin_analysis"]


if __name__ == "__main__":
    # Create and run the agent
    agent = FinanceAgent()
    agent.run()
