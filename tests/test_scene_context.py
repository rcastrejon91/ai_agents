import asyncio

from agents.frontend_agent import FrontendAgent
from agents.scene_context import SceneContextManager


def test_handle_includes_context() -> None:
    ctx_manager = SceneContextManager()
    ctx_manager.update_scene("cold but full of love")
    assert ctx_manager.get_context()["surroundings"] == "frozen temple"

    agent = FrontendAgent()
    output = asyncio.run(agent.handle({"text": "cold but full of love"}))
    assert "context" in output and isinstance(output["context"], dict)
    assert output["response"]

