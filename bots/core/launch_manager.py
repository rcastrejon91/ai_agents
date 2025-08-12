"""Minimal LaunchManager and BotRegistry.

This module provides a very small registry for mapping bot names to callables
and a ``LaunchManager`` capable of launching bots immediately or scheduling
them for later execution via APScheduler.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Dict

try:  # pragma: no cover - Python < 3.9 fallback
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler


class BotError(Exception):
    """Base error for FloBot operations."""


class BotRegistry:
    """Very small registry for named bot callables."""

    def __init__(self) -> None:
        self._bots: Dict[str, Callable[..., Any]] = {}

    def add_bot(self, name: str, fn: Callable[..., Any]) -> None:
        self._bots[name] = fn

    def get(self, name: str) -> Callable[..., Any]:
        try:
            return self._bots[name]
        except KeyError as exc:  # pragma: no cover - informative re-raise
            raise BotError(f"Bot '{name}' not registered") from exc


class LaunchManager:
    """Schedules and launches bots from a registry."""

    def __init__(self, registry: BotRegistry, tz: str = "UTC") -> None:
        self.registry = registry

        self.logger = logging.getLogger("flobot.launch")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = RotatingFileHandler("flobot.log", maxBytes=1_000_000, backupCount=3)
            self.logger.addHandler(handler)

        if ZoneInfo is not None:
            self.tz = ZoneInfo(tz)
        else:  # pragma: no cover - APScheduler accepts ``None`` timezone
            self.tz = None

        self.scheduler = BackgroundScheduler(timezone=self.tz)
        self._started = False

    # ------------------------------------------------------------------
    # Lifecycle helpers
    def start(self) -> None:
        """Start the scheduler exactly once."""

        if not self._started:
            self.scheduler.start()
            self._started = True

    def shutdown(self, wait: bool = False) -> None:
        if self._started:
            self.scheduler.shutdown(wait=wait)
            self._started = False

    # ------------------------------------------------------------------
    # Immediate launch helpers
    def launch(self, bot_name: str, *args, **kwargs) -> Any:
        """Run a bot immediately (sync wrapper)."""

        fn = self.registry.get(bot_name)
        try:
            result = fn(*args, **kwargs)
            self.logger.info("Bot %s launched OK", bot_name)
            return result
        except Exception as exc:  # pragma: no cover - logging branch
            self.logger.error("Bot %s launch failed: %s", bot_name, exc)
            raise BotError(str(exc)) from exc

    async def launch_async(self, bot_name: str, *args, **kwargs) -> Any:
        """Run a bot immediately (async context)."""

        fn = self.registry.get(bot_name)
        try:
            result = fn(*args, **kwargs)
            self.logger.info("Bot %s launched OK (async)", bot_name)
            return result
        except Exception as exc:  # pragma: no cover - logging branch
            self.logger.error("Bot %s launch failed: %s", bot_name, exc)
            raise BotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Scheduling helpers
    def schedule_launch(self, bot_name: str, delay_seconds: int, *args, **kwargs) -> Job:
        """Schedule a bot to launch after ``delay_seconds``.

        Parameters
        ----------
        bot_name:
            Name of the registered bot to launch.
        delay_seconds:
            Delay in seconds before execution.

        Returns
        -------
        Job
            The APScheduler job handle for further inspection.
        """

        self.start()  # idempotent

        run_time = (
            datetime.now(self.tz) + timedelta(seconds=delay_seconds)
            if self.tz
            else datetime.now() + timedelta(seconds=delay_seconds)
        )

        fn = self.registry.get(bot_name)

        job = self.scheduler.add_job(
            fn,
            trigger="date",
            run_date=run_time,
            args=args,
            kwargs={"trigger": "schedule", **kwargs},
            id=f"launch:{bot_name}:{int(run_time.timestamp())}",
            replace_existing=True,
        )

        self.logger.info("Scheduled %s at %s (job=%s)", bot_name, run_time, job.id)
        return job


__all__ = ["BotError", "BotRegistry", "LaunchManager"]

