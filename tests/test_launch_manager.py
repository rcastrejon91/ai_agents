import asyncio
import os
import sys
import pytest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bots.core.launch_manager import (
    FloBot,
    BotRegistry,
    LaunchManager,
    BotValidationError,
    BotNotFoundError,
)


def test_add_invalid_bot():
    registry = BotRegistry()
    bot = FloBot(name="bad", category="demo", description="missing")
    with pytest.raises(BotValidationError):
        registry.add_bot(bot)


def test_launch_callable_bot():
    registry = BotRegistry()

    def greet(target: str):
        return f"hi {target}"

    bot = FloBot(
        name="greeter",
        category="test",
        description="greets",
        launch_callable=greet,
    )
    registry.add_bot(bot)
    manager = LaunchManager(registry)
    assert manager.launch("greeter", target="bob") == "hi bob"


def test_launch_missing_bot():
    registry = BotRegistry()
    manager = LaunchManager(registry)
    with pytest.raises(BotNotFoundError):
        manager.launch("ghost")


def test_async_launch():
    registry = BotRegistry()

    def greet(target: str):
        return f"hello {target}"

    bot = FloBot(
        name="async",
        category="test",
        description="async bot",
        launch_callable=greet,
    )
    registry.add_bot(bot)
    manager = LaunchManager(registry)
    result = asyncio.run(manager.launch_async("async", target="alice"))
    assert result == "hello alice"
