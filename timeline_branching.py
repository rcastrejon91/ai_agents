"""Timeline Branching Utilities
=============================

Provides a minimal interface for divergence and convergence of
timeline states to simulate potential consequence paths.
"""

from __future__ import annotations

from typing import Any


class TimelineBranching:
    """Manage simple timeline states."""

    def __init__(self) -> None:
        self.timeline: list[dict[str, Any]] = [{"branch": 0, "description": "origin"}]

    def diverge(self, description: str) -> dict[str, Any]:
        """Create a new branch from the current timeline."""
        branch = {"branch": len(self.timeline), "description": description}
        self.timeline.append(branch)
        return branch

    def converge(self, branch_id: int) -> dict[str, Any]:
        """Return to a previous branch, trimming future states."""
        self.timeline = [b for b in self.timeline if b["branch"] <= branch_id]
        return self.timeline[-1]
