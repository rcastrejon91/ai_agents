from typing import Dict


class SceneContextManager:
    """Manage time, emotional atmosphere, and surroundings for the agent."""

    def __init__(self) -> None:
        self.current_scene: Dict[str, str] = {
            "time": "dusk",
            "emotion": "curious",
            "surroundings": "twilight forest",
        }

    def update_scene(self, input_data: str) -> None:
        lowered = (input_data or "").lower()
        if "cold" in lowered:
            self.current_scene["surroundings"] = "frozen temple"
        if "love" in lowered:
            self.current_scene["emotion"] = "enchanted"

    def get_context(self) -> Dict[str, str]:
        return dict(self.current_scene)
