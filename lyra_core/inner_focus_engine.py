import time


class InnerFocusEngine:
    def __init__(self):
        self.stream = []

    def add_focus(self, thought, intensity=1.0, emotion=None):
        self.stream.append(
            {
                "thought": thought,
                "intensity": float(intensity),
                "emotion": emotion,
                "ts": time.time(),
            }
        )
        self.stream.sort(key=lambda x: x["intensity"], reverse=True)

    def top(self, n=3):
        return self.stream[:n]
