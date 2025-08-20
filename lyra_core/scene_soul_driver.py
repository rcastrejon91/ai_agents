class SceneSoulDriver:
    def __init__(self):
        self.current = {"mood": "neutral", "imagery": "subtle mist"}

    def match_scene_to_emotion(self, emotion: str):
        e = emotion.lower()
        if "anger" in e or "mad" in e:
            self.current = {"mood": "stormy", "imagery": "dark clouds + sparks"}
        elif "joy" in e or "happy" in e:
            self.current = {"mood": "radiant", "imagery": "warm gold light"}
        elif "sad" in e or "lonely" in e:
            self.current = {"mood": "melancholy", "imagery": "echoing cathedral"}
        else:
            self.current = {"mood": "neutral", "imagery": "subtle mist"}
        return self.current
