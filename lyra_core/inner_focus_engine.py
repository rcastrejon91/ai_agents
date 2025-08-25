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


"""Inner Focus Engine for attention management."""


class InnerFocusEngine:
    def __init__(self):
        self.focus_items = []

    def add_focus(self, item: str, weight: float = 1.0, emotion: str = None):
        """Add an item to focus on."""
        focus_entry = {"item": item, "weight": weight, "emotion": emotion}
        self.focus_items.append(focus_entry)

    def top(self):
        """Get the top focus item."""
        if not self.focus_items:
            return None
        return max(self.focus_items, key=lambda x: x["weight"])
