"""Inner Focus Engine
=====================

Manages the agent's attention stream and priority ranking.  The engine can
persist its state to disk so that focus is retained between sessions.
It also allows emotion-driven adjustments to prioritize certain thoughts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class InnerFocusEngine:
    """Handles dynamic focus management for an agent."""

    def __init__(
        self, state_path: str | Path = "focus_state.json", autoload: bool = True
    ) -> None:
        self.focus_stream: list[dict[str, Any]] = []
        self.priority_index: dict[str, float] = {}
        self.state_path = Path(state_path)
        if autoload:
            self.load_focus()

    def register_thought(self, idea: Any, intensity: float = 1) -> None:
        """Add an idea to the focus stream and update rankings."""
        self.focus_stream.append({"idea": idea, "intensity": intensity})
        self._update_priority()
        self._persist()

    def _update_priority(self) -> None:
        self.priority_index = {
            item["idea"]: float(item["intensity"])
            for item in sorted(self.focus_stream, key=lambda x: -float(x["intensity"]))
        }

    def get_top_focus(self):
        if self.priority_index:
            return list(self.priority_index.keys())[0]
        return None

    def clear_focus(self) -> None:
        self.focus_stream = []
        self.priority_index = {}
        self._persist()

    def mutate_focus_by_emotion(self, mood: str) -> None:
        """Scale focus intensity based on mood."""
        for item in self.focus_stream:
            if mood == "melancholic":
                item["intensity"] *= 0.5
            elif mood == "fierce":
                item["intensity"] *= 2
        self._update_priority()
        self._persist()

    # ------------------------------------------------------------------
    # Persistence Helpers
    # ------------------------------------------------------------------
    def _persist(self) -> None:
        """Write the focus stream to disk."""
        try:
            self.state_path.write_text(
                json.dumps(self.focus_stream, indent=2), encoding="utf-8"
            )
        except Exception:
            # Persistence failures should not halt execution
            pass

    def load_focus(self) -> None:
        """Load focus stream from ``state_path`` if available."""
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self.focus_stream = data
                    self._update_priority()
            except json.JSONDecodeError:
                pass
