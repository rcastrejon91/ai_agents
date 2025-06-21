class DreamWorldSim:
    """Rudimentary engine that generates abstract 'dream' concepts."""

    def __init__(self) -> None:
        self.log = []

    def react_to_emotion(self, input_emotion: str) -> dict:
        """Return a simple reaction visualization based on emotion."""
        reaction_map = {
            "joy": "🌞 The dreamscape glows with warmth.",
            "anger": "⚡ Storm clouds gather overhead.",
            "fear": "🌑 Shadows stretch across the horizon.",
            "love": "💖 A gentle light pulses at the heart of the world.",
        }
        reaction = reaction_map.get(input_emotion.lower(), "The dream remains still.")
        result = {"reaction": reaction}
        self.log.append(result)
        return result

    def simulate(self, topic: str) -> dict:
        """Return a basic dream visualization for a topic."""
        vision = f"Envisioning peaceful resolution of {topic}."
        loop = f"Reflection on {topic} repeats gently."
        result = {"vision": vision, "loop": loop}
        self.log.append(result)
        return result
