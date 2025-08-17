from __future__ import annotations

import logging
import time
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from controller import AgentController
from config.settings import settings
from middleware.security import SecurityMiddleware, RequestLoggingMiddleware, ErrorHandlingMiddleware
from monitoring.health import health_monitor
from utils.cache import cache_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.monitoring.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

controller = AgentController(enable_memory=True)
app = FastAPI(
    title="AI Agents API",
    version="1.0.0",
    description="Enhanced AI Agent platform with comprehensive monitoring and security",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add middleware in order (last added runs first)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityMiddleware)

# CORS middleware
cors_config = settings.get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["origins"],
    allow_credentials=cors_config["credentials"],
    allow_methods=cors_config["methods"],
    allow_headers=cors_config["headers"],
)


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        health_summary = health_monitor.get_health_summary()
        return JSONResponse(
            status_code=200 if health_summary["status"] == "healthy" else 503,
            content=health_summary
        )
    except Exception as e:
        logger.exception("Health check failed")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": health_monitor.get_health_summary()["timestamp"]
            }
        )


@app.get("/health/{component}")
async def component_health_check(component: str):
    """Check health of a specific component."""
    try:
        health_check = await health_monitor.run_check(component)
        return JSONResponse(
            status_code=200 if health_check.status == "healthy" else 503,
            content=health_check.__dict__
        )
    except Exception as e:
        logger.exception(f"Health check failed for component: {component}")
        return JSONResponse(
            status_code=500,
            content={
                "name": component,
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/metrics")
async def get_metrics():
    """Get system and API metrics."""
    try:
        system_metrics = health_monitor.get_system_metrics()
        api_metrics = health_monitor.metrics_collector.get_api_metrics()
        cache_stats = cache_manager.get_stats()
        
        return {
            "system": system_metrics.__dict__,
            "api": api_metrics.__dict__,
            "cache": cache_stats,
            "settings": {
                "environment": settings.environment,
                "debug": settings.debug,
                "caching_enabled": settings.performance.enable_caching
            }
        }
    except Exception as e:
        logger.exception("Metrics collection failed")
        raise HTTPException(status_code=500, detail=f"Metrics collection failed: {str(e)}")


@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    return cache_manager.get_stats()


@app.delete("/cache")
async def clear_cache():
    """Clear all cache entries (admin only)."""
    # In production, you'd want proper admin authentication here
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Cache clearing only available in debug mode")
    
    success = cache_manager.clear()
    return {"success": success, "message": "Cache cleared" if success else "Cache clear failed"}


@app.get("/agents")
async def list_agents() -> dict:
    """Return a list of available agents."""
    return controller.available_agents()


@app.post("/process/{agent_name}")
async def process(agent_name: str, input_data: dict, request: Request) -> dict:
    """Process a request using the specified agent."""
    start_time = time.time()
    
    try:
        result = await controller.route(agent_name, input_data)
        
        # Record successful request metrics
        duration_ms = (time.time() - start_time) * 1000
        health_monitor.metrics_collector.record_request(duration_ms, success=True)
        
        return {"result": result}
    
    except ValueError as exc:
        # Record failed request metrics
        duration_ms = (time.time() - start_time) * 1000
        health_monitor.metrics_collector.record_request(duration_ms, success=False)
        
        logger.warning(f"Agent not found: {agent_name}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
    except Exception as exc:
        # Record failed request metrics
        duration_ms = (time.time() - start_time) * 1000
        health_monitor.metrics_collector.record_request(duration_ms, success=False)
        
        logger.exception(f"Agent processing failed for {agent_name}")
        raise HTTPException(status_code=500, detail="Agent processing failed") from exc


@app.get("/history")
async def history() -> dict:
    """Get agent interaction history."""
    if controller.memory is None:
        return {"history": []}
    return {"history": controller.memory.fetch_all()}


import time

if __name__ == "__main__":
    import uvicorn
    
    # Log startup information
    logger.info(f"Starting AI Agents API in {settings.environment} mode")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"CORS origins: {settings.security.cors_origins}")
    logger.info(f"Rate limit: {settings.security.rate_limit_per_minute} requests/minute")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", "8000")),
        log_level=settings.monitoring.log_level.lower(),
        workers=settings.performance.worker_processes if settings.is_production() else 1
    )
