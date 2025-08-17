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
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler


class BotError(Exception):
    """Base error for FloBot operations with structured logging support."""
    
    def __init__(self, message: str, error_code: str = "BOT_ERROR", metadata: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        """Convert error to dictionary for structured logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "error_code": self.error_code,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class BotNotFoundError(BotError):
    """Raised when a bot is not found in the registry."""
    
    def __init__(self, bot_name: str, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(f"Bot '{bot_name}' not found in registry", "BOT_NOT_FOUND", metadata)
        self.bot_name = bot_name


class BotLaunchError(BotError):
    """Raised when launching a bot fails."""
    
    def __init__(self, bot_name: str, cause: str = None, metadata: Optional[Dict[str, Any]] = None):
        message = f"Failed to launch bot '{bot_name}'"
        if cause:
            message += f": {cause}"
        super().__init__(message, "BOT_LAUNCH_FAILED", metadata)
        self.bot_name = bot_name
        self.cause = cause


class BotValidationError(BotError):
    """Raised when a bot definition is invalid."""
    
    def __init__(self, bot_name: str, validation_errors: List[str], metadata: Optional[Dict[str, Any]] = None):
        message = f"Bot '{bot_name}' validation failed: {', '.join(validation_errors)}"
        super().__init__(message, "BOT_VALIDATION_FAILED", metadata)
        self.bot_name = bot_name
        self.validation_errors = validation_errors


class BotSecurityError(BotError):
    """Raised when a bot operation violates security policies."""
    
    def __init__(self, bot_name: str, violation: str, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(f"Security violation in bot '{bot_name}': {violation}", "BOT_SECURITY_VIOLATION", metadata)
        self.bot_name = bot_name
        self.violation = violation


class BotRateLimitError(BotError):
    """Raised when a bot exceeds rate limits."""
    
    def __init__(self, bot_name: str, limit_type: str, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(f"Bot '{bot_name}' exceeded {limit_type} rate limit", "BOT_RATE_LIMIT_EXCEEDED", metadata)
        self.bot_name = bot_name
        self.limit_type = limit_type


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
    """Registry for storing and retrieving FloBots with validation."""

    def __init__(self) -> None:
        self._bots: Dict[str, FloBot] = {}

    def add_bot(self, bot: FloBot) -> None:
        """Add a bot to the registry with validation."""
        validation_errors = []
        
        # Check required fields
        if not bot.name or not isinstance(bot.name, str):
            validation_errors.append("Bot name must be a non-empty string")
        
        if not bot.launch_callable and not bot.api_endpoint:
            validation_errors.append("Bot must define either a callable or API endpoint")
            
        # Validate bot name format (alphanumeric, underscore, hyphen only)
        import re
        if bot.name and not re.match(r'^[a-zA-Z0-9_-]+$', bot.name):
            validation_errors.append("Bot name can only contain alphanumeric characters, underscores, and hyphens")
            
        # Check for duplicate names
        if bot.name in self._bots:
            validation_errors.append(f"Bot with name '{bot.name}' already exists")
            
        # Validate API endpoint if provided
        if bot.api_endpoint:
            if not isinstance(bot.api_endpoint, str) or not bot.api_endpoint.startswith(('http://', 'https://')):
                validation_errors.append("API endpoint must be a valid HTTP/HTTPS URL")
        
        if validation_errors:
            raise BotValidationError(bot.name or "unknown", validation_errors)
            
        self._bots[bot.name] = bot

    def remove_bot(self, name: str) -> bool:
        """Remove a bot from the registry. Returns True if bot was found and removed."""
        return self._bots.pop(name, None) is not None

    def get_bot(self, name: str) -> Optional[FloBot]:
        """Get a bot by name."""
        return self._bots.get(name)

    def list_bots(self) -> List[FloBot]:
        """List all registered bots."""
        return list(self._bots.values())
        
    def get_bot_names(self) -> List[str]:
        """Get list of all bot names."""
        return list(self._bots.keys())
        
    def bot_exists(self, name: str) -> bool:
        """Check if a bot with the given name exists."""
        return name in self._bots

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
    """Universal launcher for FloBots with security and rate limiting."""

    def __init__(
        self, 
        registry: BotRegistry, 
        logger: Optional[logging.Logger] = None,
        enable_security: bool = True,
        rate_limit_per_minute: int = 10
    ) -> None:
        self.registry = registry
        self.enable_security = enable_security
        self.rate_limit_per_minute = rate_limit_per_minute
        self._rate_limit_tracker: Dict[str, List[float]] = {}
        
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

    def _validate_security(self, bot_name: str, trigger: str, **kwargs) -> None:
        """Validate security constraints for bot launch."""
        if not self.enable_security:
            return
            
        # Rate limiting per bot
        current_time = time.time()
        if bot_name not in self._rate_limit_tracker:
            self._rate_limit_tracker[bot_name] = []
            
        # Clean old entries (older than 1 minute)
        cutoff_time = current_time - 60
        self._rate_limit_tracker[bot_name] = [
            t for t in self._rate_limit_tracker[bot_name] if t > cutoff_time
        ]
        
        # Check rate limit
        if len(self._rate_limit_tracker[bot_name]) >= self.rate_limit_per_minute:
            raise BotRateLimitError(
                bot_name, 
                "launch_rate", 
                {"attempts_in_last_minute": len(self._rate_limit_tracker[bot_name])}
            )
            
        # Add current attempt
        self._rate_limit_tracker[bot_name].append(current_time)
        
        # Validate trigger type
        allowed_triggers = ["chat", "dashboard", "schedule", "api"]
        if trigger not in allowed_triggers:
            raise BotSecurityError(
                bot_name, 
                f"Invalid trigger type '{trigger}'. Allowed: {allowed_triggers}",
                {"trigger": trigger, "allowed_triggers": allowed_triggers}
            )
        
        # Check for suspicious patterns in kwargs
        for key, value in kwargs.items():
            if isinstance(value, str):
                # Basic injection detection
                suspicious_patterns = [
                    r'<script\b',
                    r'javascript:',
                    r'eval\s*\(',
                    r'exec\s*\(',
                    r'__import__',
                    r'\.\./',
                    r'(drop|delete|insert|update)\s+table',
                ]
                import re
                for pattern in suspicious_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        raise BotSecurityError(
                            bot_name,
                            f"Suspicious content detected in parameter '{key}'",
                            {"parameter": key, "pattern": pattern}
                        )

    def _log_launch_attempt(self, bot_name: str, trigger: str, success: bool, error: Optional[Exception] = None, **kwargs) -> None:
        """Log bot launch attempt with structured data."""
        log_data = {
            "bot_name": bot_name,
            "trigger": trigger,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "kwargs_keys": list(kwargs.keys())  # Don't log actual values for security
        }
        
        if error:
            log_data["error"] = {
                "type": error.__class__.__name__,
                "message": str(error)
            }
            if isinstance(error, BotError):
                log_data["error"].update(error.to_dict())
        
        if success:
            self.logger.info("Bot launch successful: %s", json.dumps(log_data))
        else:
            self.logger.error("Bot launch failed: %s", json.dumps(log_data))

    def launch(self, bot_name: str, trigger: str = "chat", *args, **kwargs) -> Any:
        """Launch a bot via the specified trigger with security validation.

        Parameters
        ----------
        bot_name: str
            Name of the bot in the registry.
        trigger: str
            Trigger type: "chat", "dashboard", "schedule", or "api".
        """
        try:
            # Security validation
            self._validate_security(bot_name, trigger, **kwargs)
            
            # Get bot from registry
            bot = self.registry.get_bot(bot_name)
            if not bot:
                raise BotNotFoundError(bot_name, {"trigger": trigger, "available_bots": list(self.registry._bots.keys())})

            # Launch bot
            result = bot.run(*args, **kwargs)
            
            # Log success
            self._log_launch_attempt(bot_name, trigger, True, **kwargs)
            
            return result
            
        except Exception as e:
            # Log failure
            self._log_launch_attempt(bot_name, trigger, False, e, **kwargs)
            raise
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
