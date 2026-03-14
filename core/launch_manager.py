"""Launch manager for FloBots.

This module provides a registry system and universal launch function
for executing FloBots via chat prompts, dashboard buttons, or
scheduled tasks. Bots can be either internal Python callables or
external API endpoints.
"""

import asyncio
import json
import logging
import time
import urllib.request
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Dict, List, Optional

from apscheduler.schedulers.background import BackgroundScheduler


class BotError(Exception):
    """Base error for FloBot operations."""


class BotNotFoundError(BotError):
    """Raised when a bot is not found in the registry."""


class BotLaunchError(BotError):
    """Raised when launching a bot fails."""


class BotValidationError(BotError):
    """Raised when a bot definition is invalid."""


@dataclass
class FloBot:
    """Represents a single FloBot."""

    name: str
    category: str
    description: str
    launch_callable: Optional[Callable[..., Any]] = None
    api_endpoint: Optional[str] = None

    def run(self, *args, **kwargs) -> Any:
        """Run the FloBot using the appropriate method."""
        if self.launch_callable:
            return self.launch_callable(*args, **kwargs)
        if self.api_endpoint:
            data = json.dumps({"args": args, "kwargs": kwargs}).encode("utf-8")
            req = urllib.request.Request(
                self.api_endpoint,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req) as resp:
                return resp.read().decode()
        raise BotValidationError(f"FloBot '{self.name}' has no launch method defined")

    async def run_async(self, *args, **kwargs) -> Any:
        """Asynchronously run the FloBot."""
        if self.launch_callable:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                None, lambda: self.launch_callable(*args, **kwargs)
            )
        if self.api_endpoint:

            def _call():
                data = json.dumps({"args": args, "kwargs": kwargs}).encode("utf-8")
                req = urllib.request.Request(
                    self.api_endpoint,
                    data=data,
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req) as resp:
                    return resp.read().decode()

            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, _call)
        raise BotValidationError(f"FloBot '{self.name}' has no launch method defined")


class BotRegistry:
    """Registry for storing and retrieving FloBots."""

    def __init__(self) -> None:
        self._bots: Dict[str, FloBot] = {}

    def add_bot(self, bot: FloBot) -> None:
        if not bot.launch_callable and not bot.api_endpoint:
            raise BotValidationError(
                f"Bot '{bot.name}' must define a callable or API endpoint"
            )
        self._bots[bot.name] = bot

    def remove_bot(self, name: str) -> None:
        self._bots.pop(name, None)

    def get_bot(self, name: str) -> Optional[FloBot]:
        return self._bots.get(name)

    def list_bots(self) -> List[FloBot]:
        return list(self._bots.values())

    def preview(self, name: str) -> Optional[Dict[str, str]]:
        bot = self.get_bot(name)
        if not bot:
            return None
        return {
            "name": bot.name,
            "category": bot.category,
            "description": bot.description,
        }


class LaunchManager:
    """Universal launcher for FloBots."""

    def __init__(
        self, registry: BotRegistry, logger: Optional[logging.Logger] = None
    ) -> None:
        self.registry = registry
        self.logger = logger or logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = RotatingFileHandler(
                "flobot_launch.log", maxBytes=1_000_000, backupCount=3
            )
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def launch(self, bot_name: str, trigger: str = "chat", *args, **kwargs) -> Any:
        """Launch a bot via the specified trigger.

        Parameters
        ----------
        bot_name: str
            Name of the bot in the registry.
        trigger: str
            Trigger type: "chat", "dashboard", or "schedule".
        """
        bot = self.registry.get_bot(bot_name)
        if not bot:
            raise BotNotFoundError(f"Bot '{bot_name}' not found")

        try:
            result = bot.run(*args, **kwargs)
            self.logger.info("Bot %s launched via %s: success", bot_name, trigger)
            return result
        except Exception as exc:
            self.logger.error("Bot %s launch via %s failed: %s", bot_name, trigger, exc)
            raise BotLaunchError(str(exc))

    async def launch_async(
        self, bot_name: str, trigger: str = "chat", *args, **kwargs
    ) -> Any:
        """Asynchronously launch a bot."""
        bot = self.registry.get_bot(bot_name)
        if not bot:
            raise BotNotFoundError(f"Bot '{bot_name}' not found")
        try:
            result = await bot.run_async(*args, **kwargs)
            self.logger.info("Bot %s launched via %s: success", bot_name, trigger)
            return result
        except Exception as exc:
            self.logger.error("Bot %s launch via %s failed: %s", bot_name, trigger, exc)
            raise BotLaunchError(str(exc))

    def schedule_launch(
        self, bot_name: str, delay_seconds: int, *args, **kwargs
    ) -> None:
        """Schedule a bot to launch after a delay (in seconds)."""
        self.scheduler.add_job(
            self.launch,
            trigger="date",
            run_date=time.time() + delay_seconds,
            args=(bot_name,),
            kwargs={"trigger": "schedule", **kwargs},
        )


# Example usage placeholders (to be removed or replaced in production)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    registry = BotRegistry()

    def example_bot_action(target: str) -> str:
        return f"Bot activated on {target}!"

    bot = FloBot(
        name="example",
        category="demo",
        description="A simple example bot",
        launch_callable=example_bot_action,
    )

    registry.add_bot(bot)

    manager = LaunchManager(registry)

    print(manager.launch("example", "chat", "world"))

    async def main():
        await manager.launch_async("example", "chat", "async world")

    asyncio.run(main())

    manager.schedule_launch("example", 5, target="scheduled world")
    time.sleep(6)
