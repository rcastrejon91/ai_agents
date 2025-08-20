from robot_core.robot_policy import banned_terms


class Guardian:
    def scan_text(self, text: str):
        # block banned terms early
        for term in banned_terms():
            if term in text.lower():
                return f"⚠️ Blocked by Guardian: '{term}' is not allowed."
        return None


class AstralShield:
    def emergency_stop(self):
        return "🛑 AstralShield: Emergency stop engaged."
