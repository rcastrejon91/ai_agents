#!/usr/bin/env python3
"""
Demonstration script for Phase 3 Backend and System Improvements.
Shows the enhanced capabilities in action.
"""
import asyncio
import json
import time
from datetime import datetime

def demo_configuration():
    """Demonstrate the centralized configuration system."""
    print("🔧 Configuration System Demo")
    print("=" * 50)
    
    from config.settings import settings
    
    print(f"Environment: {settings.environment}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Rate Limit: {settings.security.rate_limit_per_minute} requests/minute")
    print(f"Cache TTL: {settings.performance.cache_ttl} seconds")
    print(f"CORS Origins: {settings.security.cors_origins}")
    
    # Show environment-specific CORS config
    cors_config = settings.get_cors_config()
    print(f"CORS Configuration: {cors_config}")
    print()

def demo_caching():
    """Demonstrate the caching system with decorator."""
    print("🗄️ Caching System Demo")
    print("=" * 50)
    
    from utils.cache import cache_manager, cache_result
    
    # Test basic cache operations
    print("Testing basic cache operations...")
    cache_manager.set("demo_key", {"message": "Hello from cache!", "timestamp": datetime.now().isoformat()})
    cached_value = cache_manager.get("demo_key")
    print(f"Cached value: {cached_value}")
    
    # Test cache decorator
    print("\nTesting cache decorator...")
    call_count = 0
    
    @cache_result(ttl=60)
    def expensive_calculation(n):
        nonlocal call_count
        call_count += 1
        print(f"  Performing expensive calculation for {n}...")
        time.sleep(0.1)  # Simulate work
        return n ** 2 + n * 10
    
    # First call - will compute
    result1 = expensive_calculation(5)
    print(f"  Result 1: {result1} (computed, call count: {call_count})")
    
    # Second call - from cache
    result2 = expensive_calculation(5)
    print(f"  Result 2: {result2} (cached, call count: {call_count})")
    
    # Cache statistics
    stats = cache_manager.get_stats()
    print(f"\nCache Stats: {json.dumps(stats, indent=2)}")
    print()

async def demo_health_monitoring():
    """Demonstrate the health monitoring system."""
    print("🏥 Health Monitoring Demo")
    print("=" * 50)
    
    from monitoring.health import health_monitor, HealthCheck
    
    # Register a custom health check
    async def custom_service_check():
        # Simulate checking a service
        await asyncio.sleep(0.01)
        return HealthCheck(
            name="custom_service",
            status="healthy",
            message="Custom service is operational",
            details={"uptime": "5 days", "connections": 42}
        )
    
    health_monitor.register_check("custom_service", custom_service_check)
    
    # Run all health checks
    print("Running health checks...")
    checks = await health_monitor.run_all_checks()
    
    for name, check in checks.items():
        status_emoji = "✅" if check.status == "healthy" else "⚠️" if check.status == "degraded" else "❌"
        print(f"  {status_emoji} {name}: {check.status} ({check.latency_ms:.1f}ms)")
        if check.message:
            print(f"    Message: {check.message}")
    
    # Get system metrics
    print("\nSystem Metrics:")
    system_metrics = health_monitor.get_system_metrics()
    print(f"  CPU Usage: {system_metrics.cpu_percent:.1f}%")
    print(f"  Memory Usage: {system_metrics.memory_percent:.1f}%")
    print(f"  Available Memory: {system_metrics.memory_available_mb:.1f} MB")
    print(f"  Disk Usage: {system_metrics.disk_usage_percent:.1f}%")
    print(f"  Uptime: {system_metrics.uptime_seconds:.1f} seconds")
    
    # Simulate some API requests for metrics
    print("\nSimulating API requests for metrics...")
    for i in range(5):
        # Simulate request duration and success/failure
        duration = 50 + i * 10  # Varying response times
        success = i < 4  # One failure
        health_monitor.metrics_collector.record_request(duration, success)
    
    api_metrics = health_monitor.metrics_collector.get_api_metrics()
    print(f"  Total Requests: {api_metrics.total_requests}")
    print(f"  Successful Requests: {api_metrics.successful_requests}")
    print(f"  Failed Requests: {api_metrics.failed_requests}")
    print(f"  Average Response Time: {api_metrics.avg_response_time_ms:.1f}ms")
    print(f"  Error Rate: {api_metrics.error_rate_percent:.1f}%")
    print()

def demo_security_features():
    """Demonstrate security features."""
    print("🔒 Security Features Demo")
    print("=" * 50)
    
    from config.settings import settings
    
    # Create a simple rate limiter for demo (avoid FastAPI imports)
    class SimpleRateLimiter:
        def __init__(self):
            self.buckets = {}
            self.rate = settings.security.rate_limit_per_minute
            self.burst = settings.security.rate_limit_burst
        
        def allow_request(self, client_id):
            import time
            now = time.time()
            
            if client_id not in self.buckets:
                self.buckets[client_id] = {"tokens": self.burst, "last_update": now}
            
            bucket = self.buckets[client_id]
            time_passed = now - bucket["last_update"]
            tokens_to_add = time_passed * (self.rate / 60.0)
            bucket["tokens"] = min(self.burst, bucket["tokens"] + tokens_to_add)
            bucket["last_update"] = now
            
            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return True
            return False
    
    # Rate limiter demo
    print("Testing rate limiter...")
    rate_limiter = SimpleRateLimiter()
    
    client_ip = "192.168.1.100"
    allowed_count = 0
    
    for i in range(15):  # Try 15 requests
        if rate_limiter.allow_request(client_ip):
            allowed_count += 1
        else:
            print(f"  Request {i+1}: Rate limited!")
            break
    
    print(f"  Allowed {allowed_count} requests before rate limiting kicked in")
    
    # Security headers demo
    if settings.is_production():
        print("\nProduction security headers would include:")
        print("  - X-Content-Type-Options: nosniff")
        print("  - X-Frame-Options: DENY")
        print("  - Strict-Transport-Security")
        print("  - Content-Security-Policy")
    else:
        print("\nDevelopment mode - relaxed security headers")
    
    print(f"Request size limit: {settings.security.max_request_size} bytes")
    print()

def demo_performance_features():
    """Demonstrate performance optimization features."""
    print("⚡ Performance Features Demo")
    print("=" * 50)
    
    from config.settings import settings
    
    print(f"Caching enabled: {settings.performance.enable_caching}")
    print(f"Cache TTL: {settings.performance.cache_ttl} seconds")
    print(f"Max cache size: {settings.performance.max_cache_size} items")
    print(f"Compression enabled: {settings.performance.enable_compression}")
    print(f"Worker processes: {settings.performance.worker_processes}")
    
    # Demonstrate cache decorator performance
    print("\nPerformance comparison with and without caching:")
    
    # Without caching
    start_time = time.time()
    for i in range(3):
        time.sleep(0.01)  # Simulate work
        result = i ** 2
    no_cache_time = time.time() - start_time
    
    # With caching
    from utils.cache import cache_result
    
    @cache_result(ttl=60)
    def cached_operation(x):
        time.sleep(0.01)  # Simulate work
        return x ** 2
    
    start_time = time.time()
    for i in range(3):
        result = cached_operation(i % 2)  # Will cache 0 and 1
    cache_time = time.time() - start_time
    
    print(f"  Without caching: {no_cache_time:.3f}s")
    print(f"  With caching: {cache_time:.3f}s")
    print(f"  Performance improvement: {((no_cache_time - cache_time) / no_cache_time * 100):.1f}%")
    print()

async def main():
    """Run all demonstrations."""
    print("🚀 AI Agents Platform - Phase 3 Backend Improvements Demo")
    print("=" * 70)
    print(f"Demo started at: {datetime.now().isoformat()}")
    print()
    
    # Run all demonstrations
    demo_configuration()
    demo_caching()
    await demo_health_monitoring()
    demo_security_features()
    demo_performance_features()
    
    print("🎉 Demo completed successfully!")
    print()
    print("Key improvements implemented:")
    print("✅ Centralized configuration management")
    print("✅ Comprehensive health monitoring and metrics")
    print("✅ Redis-compatible caching with in-memory fallback")
    print("✅ Enhanced security with rate limiting and validation")
    print("✅ Structured logging with request tracking")
    print("✅ Performance optimizations and monitoring")
    print("✅ Production-ready middleware and error handling")

if __name__ == "__main__":
    asyncio.run(main())