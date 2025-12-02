#!/usr/bin/env python3
# api_gateway.py - API Gateway for AI Agents

import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gateway")

# Try to import agent registry
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

        def get_agent(self, agent_id):
            return None

        def list_agents(self):
            return []

    agent_registry = AgentRegistryStub()

# Create FastAPI app
app = FastAPI(
    title="AI Agents Gateway", description="API Gateway for AI Agents", version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Agents Gateway", "version": "1.0.0"}


@app.get("/agents")
async def list_agents():
    """List all available agents."""
    return agent_registry.list_agents()


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get information about a specific agent."""
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return agent


@app.post("/agents/{agent_id}/process")
async def process_agent_request(agent_id: str, request: Request):
    """Process a request with the specified agent."""
    try:
        request_data = await request.json()
        return await agent_registry.call_agent(agent_id, request_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run the gateway
    logger.info("Starting AI Agents Gateway on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
