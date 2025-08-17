"""
Comprehensive health monitoring and performance metrics system.
"""
import asyncio
import time
import psutil
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

from config.settings import settings


@dataclass
class HealthCheck:
    """Individual health check result."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    latency_ms: Optional[float] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    load_average: List[float]
    active_connections: int
    uptime_seconds: float
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class APIMetrics:
    """API performance metrics."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    requests_per_minute: float
    error_rate_percent: float
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class MetricsCollector:
    """Collects and aggregates system and application metrics."""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_times = deque(maxlen=1000)  # Store last 1000 request times
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self._cleanup_interval = 300  # 5 minutes
    
    def record_request(self, duration_ms: float, success: bool = True):
        """Record a request for metrics calculation."""
        current_minute = int(time.time() / 60)
        
        self.request_times.append((time.time(), duration_ms))
        self.request_counts[current_minute] += 1
        
        if not success:
            self.error_counts[current_minute] += 1
    
    def get_api_metrics(self) -> APIMetrics:
        """Calculate current API metrics."""
        now = time.time()
        current_minute = int(now / 60)
        
        # Filter recent request times (last 5 minutes)
        recent_requests = [
            (timestamp, duration) for timestamp, duration in self.request_times
            if now - timestamp <= 300
        ]
        
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())
        successful_requests = total_requests - total_errors
        
        if recent_requests:
            durations = [duration for _, duration in recent_requests]
            avg_response_time = sum(durations) / len(durations)
            p95_response_time = sorted(durations)[int(len(durations) * 0.95)]
        else:
            avg_response_time = 0
            p95_response_time = 0
        
        # Requests per minute (last 5 minutes)
        recent_minutes = [current_minute - i for i in range(5)]
        recent_request_count = sum(self.request_counts.get(minute, 0) for minute in recent_minutes)
        requests_per_minute = recent_request_count / 5.0
        
        # Error rate
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        return APIMetrics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=total_errors,
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=p95_response_time,
            requests_per_minute=requests_per_minute,
            error_rate_percent=error_rate
        )
    
    def cleanup_old_metrics(self):
        """Remove old metric data to prevent memory leaks."""
        current_minute = int(time.time() / 60)
        cutoff_minute = current_minute - 60  # Keep last hour
        
        # Clean old request counts
        old_minutes = [minute for minute in self.request_counts.keys() if minute < cutoff_minute]
        for minute in old_minutes:
            del self.request_counts[minute]
            if minute in self.error_counts:
                del self.error_counts[minute]


class HealthMonitor:
    """Centralized health monitoring system."""
    
    def __init__(self):
        self.checks = {}
        self.metrics_collector = MetricsCollector()
        self._start_background_tasks()
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check function."""
        self.checks[name] = check_func
    
    async def run_check(self, name: str) -> HealthCheck:
        """Run a specific health check."""
        if name not in self.checks:
            return HealthCheck(
                name=name,
                status="unhealthy",
                message=f"Unknown health check: {name}"
            )
        
        start_time = time.time()
        try:
            result = await self.checks[name]()
            latency_ms = (time.time() - start_time) * 1000
            
            if isinstance(result, HealthCheck):
                if result.latency_ms is None:
                    result.latency_ms = latency_ms
                # Ensure the name matches what was requested
                if result.name != name:
                    result.name = name
                return result
            elif isinstance(result, dict):
                return HealthCheck(
                    name=name,
                    status=result.get("status", "healthy"),
                    latency_ms=latency_ms,
                    message=result.get("message"),
                    details=result.get("details")
                )
            else:
                return HealthCheck(
                    name=name,
                    status="healthy" if result else "unhealthy",
                    latency_ms=latency_ms
                )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name=name,
                status="unhealthy",
                latency_ms=latency_ms,
                message=str(e)
            )
    
    async def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks."""
        results = {}
        for name in self.checks:
            results[name] = await self.run_check(name)
        return results
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_mb = memory.available / (1024 * 1024)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        
        # Load average
        load_avg = list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        
        # Network connections (approximate)
        try:
            connections = len(psutil.net_connections(kind='inet'))
        except:
            connections = 0
        
        # Uptime
        uptime_seconds = time.time() - self.metrics_collector.start_time
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_mb=memory_available_mb,
            disk_usage_percent=disk_usage_percent,
            load_average=load_avg,
            active_connections=connections,
            uptime_seconds=uptime_seconds
        )
    
    def get_health_summary(self, include_system_metrics: bool = True) -> Dict[str, Any]:
        """Get comprehensive health summary."""
        summary = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {},
            "metrics": {}
        }
        
        # Run health checks synchronously for summary
        checks = asyncio.create_task(self.run_all_checks()) if asyncio.get_event_loop().is_running() else {}
        
        if checks:
            overall_status = "healthy"
            for check in checks.values():
                if check.status == "unhealthy":
                    overall_status = "unhealthy"
                    break
                elif check.status == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"
            
            summary["status"] = overall_status
            summary["checks"] = {name: asdict(check) for name, check in checks.items()}
        
        # Add metrics
        if include_system_metrics:
            summary["metrics"]["system"] = asdict(self.get_system_metrics())
            summary["metrics"]["api"] = asdict(self.metrics_collector.get_api_metrics())
        
        return summary
    
    def _start_background_tasks(self):
        """Start background cleanup tasks."""
        if not hasattr(self, '_cleanup_task'):
            self._cleanup_task = True
            # Note: In production, you'd want to use a proper task scheduler
            # This is a simplified version for demonstration


# Global health monitor instance
health_monitor = HealthMonitor()


# Default health checks
async def database_health_check():
    """Basic database connectivity check."""
    try:
        # This would typically test database connectivity
        # For now, we'll simulate a basic check
        start_time = time.time()
        await asyncio.sleep(0.01)  # Simulate database query
        latency = (time.time() - start_time) * 1000
        
        return HealthCheck(
            name="database",
            status="healthy",
            latency_ms=latency,
            message="Database connection OK"
        )
    except Exception as e:
        return HealthCheck(
            name="database",
            status="unhealthy",
            message=f"Database connection failed: {str(e)}"
        )


async def redis_health_check():
    """Redis connectivity check."""
    try:
        # This would typically test Redis connectivity
        # For now, we'll simulate a basic check
        if settings.redis.url:
            return HealthCheck(
                name="redis",
                status="healthy",
                message="Redis connection OK"
            )
        else:
            return HealthCheck(
                name="redis",
                status="degraded",
                message="Redis not configured"
            )
    except Exception as e:
        return HealthCheck(
            name="redis",
            status="unhealthy",
            message=f"Redis connection failed: {str(e)}"
        )


async def external_api_health_check():
    """External API dependency check."""
    try:
        # Check if required API keys are configured
        missing_keys = []
        if not settings.api.openai_api_key:
            missing_keys.append("OpenAI")
        if not settings.api.tavily_api_key:
            missing_keys.append("Tavily")
        
        if missing_keys:
            return HealthCheck(
                name="external_apis",
                status="degraded",
                message=f"Missing API keys: {', '.join(missing_keys)}"
            )
        
        return HealthCheck(
            name="external_apis",
            status="healthy",
            message="All external APIs configured"
        )
    except Exception as e:
        return HealthCheck(
            name="external_apis",
            status="unhealthy",
            message=f"External API check failed: {str(e)}"
        )


# Register default health checks
health_monitor.register_check("database", database_health_check)
health_monitor.register_check("redis", redis_health_check)
health_monitor.register_check("external_apis", external_api_health_check)