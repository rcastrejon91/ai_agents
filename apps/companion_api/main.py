import logging
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agents.frontend_agent import FrontendAgent

# Configure logging (timestamp, log level, message)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("companion_api")

app = FastAPI(title="Companion API", version="1.0.0")
agent = FrontendAgent()


class InputPayload(BaseModel):
    text: str
    metadata: dict | None = None


# Middleware to track request latency and add request IDs
@app.middleware("http")
async def add_latency_and_request_id(request: Request, call_next):
    req_id = str(uuid.uuid4())[:8]  # short ID for logs
    start_time = time.time()

    # Attach ID to request state so handlers can access it
    request.state.req_id = req_id

    try:
        response = await call_next(request)
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.exception(f"[{req_id}] Unhandled error after {process_time:.2f}ms")
        return JSONResponse(
            status_code=500,
            content={"request_id": req_id, "error": "Internal server error"}
        )

    process_time = (time.time() - start_time) * 1000

    # Warn if request took longer than 1s
    if process_time > 1000:
        logger.warning(f"[{req_id}] {request.method} {request.url.path} took {process_time:.2f}ms")
    else:
        logger.info(f"[{req_id}] {request.method} {request.url.path} completed in {process_time:.2f}ms")

    # Add useful headers
    response.headers["X-Request-ID"] = req_id
    response.headers["X-Process-Time-ms"] = f"{process_time:.2f}"
    return response


@app.post("/handle")
async def handle(payload: InputPayload, request: Request):
    req_id = getattr(request.state, "req_id", "unknown")
    logger.info(f"[{req_id}] Incoming payload: text={payload.text}, metadata={payload.metadata}")

    try:
        result = await agent.handle(payload.model_dump())
        logger.info(f"[{req_id}] Agent result: {result}")
        return {"request_id": req_id, "result": result}
    except Exception as e:
        logger.exception(f"[{req_id}] Error while handling request")
        return JSONResponse(
            status_code=500,
            content={"request_id": req_id, "error": str(e)}
        )


@app.get("/health")
def health():
    return {"status": "ok"}
