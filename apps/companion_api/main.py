from fastapi import FastAPI
from pydantic import BaseModel
from agents.frontend_agent import FrontendAgent

app = FastAPI(title="Companion API", version="1.0.0")
agent = FrontendAgent()


class InputPayload(BaseModel):
    text: str
    metadata: dict | None = None


@app.post("/handle")
async def handle(payload: InputPayload):
    result = await agent.handle(payload.model_dump())
    return result


@app.get("/health")
def health():
    return {"status": "ok"}
