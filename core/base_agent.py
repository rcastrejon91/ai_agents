import logging
from abc import ABC, abstractmethod

import uvicorn
from fastapi import FastAPI


class BaseAIAgent(ABC):
    def __init__(self, industry: str, port: int):
        self.industry = industry
        self.port = port
        self.app = FastAPI()
        self.setup_routes()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def setup_routes(self):
        pass

    @abstractmethod
    async def process_task(self, input_data: dict):
        pass

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)
