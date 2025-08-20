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
