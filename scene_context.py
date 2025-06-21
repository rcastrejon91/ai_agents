class SceneContextManager:
    """Manage time, emotional atmosphere, and surroundings for the agent."""

    def __init__(self) -> None:
        self.current_scene = {
            "time": "dusk",
            "emotion": "curious",
            "surroundings": "twilight forest",
        }

    def update_scene(self, input_data: str) -> None:
        """Update scene details based on the latest user input."""
        lowered = input_data.lower()
        if "cold" in lowered:
            self.current_scene["surroundings"] = "frozen temple"
        if "love" in lowered:
            self.current_scene["emotion"] = "enchanted"

    def get_context(self) -> dict:
        """Return the current scene context."""
        return self.current_scene
