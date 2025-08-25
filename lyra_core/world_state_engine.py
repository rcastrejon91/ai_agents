class WorldStateEngine:
    def __init__(self):
        self.events = []
        self.last_emotion = "neutral"

    def add_event(self, event):
        self.events.append(event)

    def react_to_emotion(self, emotion: str):
        self.last_emotion = emotion
        self.add_event({"type": "emotion", "value": emotion})
        return f"World shifts with emotion: {emotion}"

    def monitor_environment(self, env):
        if env.get("obstacle_distance", 999) < 0.5:
            return "⚠️ Obstacle too close"
        if env.get("temp_c", 25) > 70:
            return "⚠️ Overheating"
        return "Environment stable"

    def summary(self):
        return {"events": self.events[-5:], "emotion": self.last_emotion}


"""World State Engine for tracking environment and events."""


class WorldStateEngine:
    def __init__(self):
        self.events = []
        self.environment_data = {}

    def add_event(self, event: dict):
        """Add an event to the world state."""
        self.events.append(event)

    def react_to_emotion(self, emotion: str):
        """React to emotional input."""
        self.add_event({"type": "emotion", "emotion": emotion})

    def monitor_environment(self, env_data: dict):
        """Monitor environmental data."""
        self.environment_data.update(env_data)
        # Simple hazard detection
        if env_data.get("temperature", 0) > 100:
            return "High temperature detected"
        return "Environment stable"

    def summary(self):
        """Get a summary of the world state."""
        return {"event_count": len(self.events), "environment": self.environment_data}
