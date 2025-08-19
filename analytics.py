from __future__ import annotations

from typing import Any


class AnalyticsStore:
    """Simple in-memory analytics store for user engagement data."""

    def __init__(self) -> None:
        self._metrics: dict[str, dict[str, Any]] = {}

    def log_metrics(self, session_id: str, metrics: dict[str, Any]) -> None:
        """Store analytics metrics for a session."""
        self._metrics[session_id] = metrics

    def get_metrics(self, session_id: str) -> dict[str, Any]:
        """Retrieve metrics for a session if available."""
        return self._metrics.get(session_id, {})


analytics_store = AnalyticsStore()
