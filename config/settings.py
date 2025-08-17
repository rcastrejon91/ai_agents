"""
Centralized configuration system for AI Agents platform.
Supports environment-specific settings with secure defaults.
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: Optional[str] = None
    max_connections: int = 10
    query_timeout: int = 30
    enable_query_logging: bool = False


@dataclass
class RedisConfig:
    """Redis/caching configuration settings."""
    url: Optional[str] = None
    max_connections: int = 10
    default_ttl: int = 300
    key_prefix: str = "ai_agents"


@dataclass
class SecurityConfig:
    """Security and authentication settings."""
    secret_key: Optional[str] = None
    admin_token: Optional[str] = None
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    cors_credentials: bool = True
    rate_limit_per_minute: int = 90
    rate_limit_burst: int = 10
    max_request_size: int = 1024 * 1024  # 1MB


@dataclass
class APIConfig:
    """API service configuration."""
    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3


@dataclass
class MonitoringConfig:
    """Monitoring and observability settings."""
    enable_metrics: bool = True
    enable_health_checks: bool = True
    enable_request_logging: bool = True
    log_level: str = "INFO"
    metrics_port: int = 9090


@dataclass
class PerformanceConfig:
    """Performance and optimization settings."""
    enable_caching: bool = True
    cache_ttl: int = 300
    max_cache_size: int = 1000
    enable_compression: bool = True
    worker_processes: int = 1


class Settings:
    """Centralized settings management with environment variable support."""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Load configurations
        self.database = self._load_database_config()
        self.redis = self._load_redis_config()
        self.security = self._load_security_config()
        self.api = self._load_api_config()
        self.monitoring = self._load_monitoring_config()
        self.performance = self._load_performance_config()
    
    def _load_database_config(self) -> DatabaseConfig:
        return DatabaseConfig(
            url=os.getenv("DATABASE_URL"),
            max_connections=int(os.getenv("DB_MAX_CONNECTIONS", "10")),
            query_timeout=int(os.getenv("DB_QUERY_TIMEOUT", "30")),
            enable_query_logging=os.getenv("DB_ENABLE_QUERY_LOGGING", "false").lower() == "true"
        )
    
    def _load_redis_config(self) -> RedisConfig:
        return RedisConfig(
            url=os.getenv("REDIS_URL"),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
            default_ttl=int(os.getenv("REDIS_DEFAULT_TTL", "300")),
            key_prefix=os.getenv("REDIS_KEY_PREFIX", "ai_agents")
        )
    
    def _load_security_config(self) -> SecurityConfig:
        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        return SecurityConfig(
            secret_key=os.getenv("SECRET_KEY"),
            admin_token=os.getenv("ADMIN_TOKEN"),
            cors_origins=[origin.strip() for origin in cors_origins],
            cors_credentials=os.getenv("CORS_CREDENTIALS", "true").lower() == "true",
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "90")),
            rate_limit_burst=int(os.getenv("RATE_LIMIT_BURST", "10")),
            max_request_size=int(os.getenv("MAX_REQUEST_SIZE", str(1024 * 1024)))
        )
    
    def _load_api_config(self) -> APIConfig:
        return APIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            stripe_secret_key=os.getenv("STRIPE_SECRET_KEY"),
            stripe_webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
            timeout=int(os.getenv("API_TIMEOUT", "30")),
            max_retries=int(os.getenv("API_MAX_RETRIES", "3"))
        )
    
    def _load_monitoring_config(self) -> MonitoringConfig:
        return MonitoringConfig(
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            enable_health_checks=os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true",
            enable_request_logging=os.getenv("ENABLE_REQUEST_LOGGING", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            metrics_port=int(os.getenv("METRICS_PORT", "9090"))
        )
    
    def _load_performance_config(self) -> PerformanceConfig:
        return PerformanceConfig(
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
            cache_ttl=int(os.getenv("CACHE_TTL", "300")),
            max_cache_size=int(os.getenv("MAX_CACHE_SIZE", "1000")),
            enable_compression=os.getenv("ENABLE_COMPRESSION", "true").lower() == "true",
            worker_processes=int(os.getenv("WORKER_PROCESSES", "1"))
        )
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration for web frameworks."""
        if self.is_production():
            # Stricter CORS in production
            return {
                "origins": self.security.cors_origins,
                "credentials": self.security.cors_credentials,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "headers": ["Content-Type", "Authorization", "X-Admin-Key"]
            }
        else:
            # More permissive in development
            return {
                "origins": ["*"] if not self.security.cors_origins else self.security.cors_origins,
                "credentials": True,
                "methods": ["*"],
                "headers": ["*"]
            }


# Global settings instance
settings = Settings()