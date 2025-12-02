import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager


class AgentConfig(BaseModel):
    """Configuration for the AI Agent"""
    name: str = Field(..., description="Name of the agent")
    description: str = Field("", description="Description of the agent's capabilities")
    version: str = Field("1.0.0", description="Agent version")
    industry: str = Field(..., description="Industry the agent serves")
    max_tokens: int = Field(1024, description="Maximum tokens for responses")
    temperature: float = Field(0.7, description="Temperature for response generation")
    timeout: int = Field(30, description="Timeout in seconds for requests")
    debug_mode: bool = Field(False, description="Enable debug mode")


class TaskInput(BaseModel):
    """Input format for agent tasks"""
    query: str = Field(..., description="The user's query or task description")
    context: Dict[str, Any] = Field({}, description="Additional context for the task")
    parameters: Dict[str, Any] = Field({}, description="Parameters to customize processing")


class TaskResponse(BaseModel):
    """Standard response format for agent tasks"""
    result: Any = Field(..., description="The result of processing")
    processing_time: float = Field(..., description="Time taken to process in seconds")
    agent_name: str = Field(..., description="Name of the agent that processed the request")
    timestamp: str = Field(..., description="ISO timestamp of when the response was generated")
    request_id: str = Field(..., description="Unique ID for the request")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logging.info("Agent starting up...")
    yield
    # Shutdown logic
    logging.info("Agent shutting down...")


class EnhancedAIAgent(ABC):
    def __init__(self, config: AgentConfig, port: int = 8000):
        self.config = config
        self.port = port
        self.app = FastAPI(
            title=f"{config.name} API",
            description=config.description,
            version=config.version,
            lifespan=lifespan
        )
        self._setup_middleware()
        self._setup_base_routes()
        self.setup_routes()
        
        # Configure logging
        log_level = logging.DEBUG if config.debug_mode else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize memory/state
        self.memory = {}
        self.startup_time = time.time()
        
    def _setup_middleware(self):
        """Setup middleware for the FastAPI app"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify actual origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    def _setup_base_routes(self):
        """Setup standard routes that all agents should have"""
        @self.app.get("/health")
        async def health_check():
            uptime = time.time() - self.startup_time
            return {
                "status": "healthy",
                "agent": self.config.name,
                "version": self.config.version,
                "uptime_seconds": uptime
            }
            
        @self.app.get("/info")
        async def agent_info():
            return {
                "name": self.config.name,
                "description": self.config.description,
                "version": self.config.version,
                "industry": self.config.industry,
                "capabilities": self.get_capabilities()
            }
        
        @self.app.post("/process")
        async def process_endpoint(
            task: TaskInput, 
            background_tasks: BackgroundTasks,
            request: Request
        ):
            start_time = time.time()
            request_id = f"{int(start_time)}-{hash(task.query)}"
            
            try:
                # Log the incoming request
                if self.config.debug_mode:
                    self.logger.debug(f"Processing request {request_id}: {task.query[:100]}...")
                
                # Process the task
                result = await self.process_task(task.dict())
                
                # Optional: Log the task in history
                background_tasks.add_task(
                    self._log_task_history, 
                    request_id=request_id,
                    task=task,
                    result=result
                )
                
                # Return standardized response
                return TaskResponse(
                    result=result,
                    processing_time=time.time() - start_time,
                    agent_name=self.config.name,
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    request_id=request_id
                )
            except Exception as e:
                self.logger.error(f"Error processing task: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _log_task_history(self, request_id: str, task: TaskInput, result: Any):
        """Log task to history (could be extended to use a database)"""
        if len(self.memory) > 1000:  # Simple memory management
            oldest_key = next(iter(self.memory))
            del self.memory[oldest_key]
            
        self.memory[request_id] = {
            "task": task.dict(),
            "result": result,
            "timestamp": time.time()
        }
    
    @abstractmethod
    def setup_routes(self):
        """Setup agent-specific routes"""
        pass
    
    @abstractmethod
    async def process_task(self, input_data: dict) -> Any:
        """Process the input task and return results"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return ["basic_query_processing"]
    
    async def validate_input(self, input_data: dict) -> bool:
        """Validate input data before processing"""
        # Default implementation just checks for query
        return "query" in input_data and input_data["query"].strip() != ""
    
    def run(self, host: str = "0.0.0.0"):
        """Run the FastAPI application with uvicorn"""
        self.logger.info(f"Starting {self.config.name} agent on port {self.port}")
        uvicorn.run(self.app, host=host, port=self.port)
