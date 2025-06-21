from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException

from controller import AgentController

logging.basicConfig(level=logging.INFO)

controller = AgentController(enable_memory=True)
app = FastAPI(title="AITaskFlo API")


@app.get("/agents")
async def list_agents() -> dict:
    """Return a list of available agents."""
    return controller.available_agents()


@app.post("/process/{agent_name}")
async def process(agent_name: str, input_data: dict) -> dict:
    try:
        result = await controller.route(agent_name, input_data)
        return {"result": result}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - general error
        raise HTTPException(status_code=500, detail="Agent processing failed") from exc


@app.get("/history")
async def history() -> dict:
    if controller.memory is None:
        return {"history": []}
    return {"history": controller.memory.fetch_all()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
