class GuardianProtocols:
    """Basic safeguards against negative input or overload."""

    NEGATIVE_KEYWORDS = {"threat", "attack", "hate", "angry"}

    def evaluate(self, text: str) -> dict:
        """Return a protection status and message."""
        lowered = text.lower()
        if any(word in lowered for word in self.NEGATIVE_KEYWORDS):
            return {
                "status": "neutralized",
                "message": "Neutralized threat, standing down.",
            }
        return {"status": "clear", "message": "All clear."}
