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

        # Determine time of day
        if any(word in lowered for word in ("dawn", "morning", "sunrise")):
            self.current_scene["time"] = "dawn"
        elif any(word in lowered for word in ("noon", "afternoon")):
            self.current_scene["time"] = "afternoon"
        elif any(word in lowered for word in ("evening", "night", "dusk")):
            self.current_scene["time"] = "night"

        # Determine surroundings
        if any(word in lowered for word in ("cold", "snow", "ice")):
            self.current_scene["surroundings"] = "frozen temple"
        elif "rain" in lowered:
            self.current_scene["surroundings"] = "rain-soaked streets"
        elif "forest" in lowered:
            self.current_scene["surroundings"] = "twilight forest"

        # Determine emotional atmosphere
        if "love" in lowered:
            self.current_scene["emotion"] = "enchanted"
        elif any(word in lowered for word in ("fear", "worry")):
            self.current_scene["emotion"] = "tense"

    def get_context(self) -> dict:
        """Return a copy of the current scene context."""
        return dict(self.current_scene)
