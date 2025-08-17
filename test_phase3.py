#!/usr/bin/env python3
"""
Test script for Phase 3 backend improvements.
Tests configuration, middleware, health monitoring, and caching.
"""
import asyncio
import time
import json
import requests
import subprocess
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_configuration():
    """Test the centralized configuration system."""
    print("🔧 Testing configuration system...")
    
    try:
        from config.settings import settings
        
        # Test environment loading
        assert hasattr(settings, 'environment')
        assert hasattr(settings, 'security')
        assert hasattr(settings, 'monitoring')
        assert hasattr(settings, 'performance')
        
        # Test CORS configuration
        cors_config = settings.get_cors_config()
        assert 'origins' in cors_config
        assert 'credentials' in cors_config
        
        print("✅ Configuration system working correctly")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_health_monitoring():
    """Test the health monitoring system."""
    print("🏥 Testing health monitoring...")
    
    try:
        from monitoring.health import health_monitor, HealthCheck
        
        # Test health check registration
        async def dummy_check():
            return HealthCheck(name="test", status="healthy", message="Test check")
        
        health_monitor.register_check("test_check", dummy_check)
        
        # Test running checks
        async def run_test():
            result = await health_monitor.run_check("test_check")
            assert result.name == "test_check"
            assert result.status == "healthy"
            
            # Test system metrics
            metrics = health_monitor.get_system_metrics()
            assert hasattr(metrics, 'cpu_percent')
            assert hasattr(metrics, 'memory_percent')
            
            return True
        
        result = asyncio.run(run_test())
        assert result
        
        print("✅ Health monitoring working correctly")
        return True
    except Exception as e:
        print(f"❌ Health monitoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_caching():
    """Test the caching system."""
    print("🗄️ Testing caching system...")
    
    try:
        from utils.cache import cache_manager, cache_result
        
        # Test basic cache operations
        cache_manager.set("test_key", "test_value", ttl=60)
        value = cache_manager.get("test_key")
        assert value == "test_value"
        
        # Test cache deletion
        success = cache_manager.delete("test_key")
        assert success
        
        value = cache_manager.get("test_key")
        assert value is None
        
        # Test decorator
        call_count = 0
        
        @cache_result(ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment
        
        # Test cache stats
        stats = cache_manager.get_stats()
        assert 'backend' in stats
        assert 'memory_cache_size' in stats
        
        print("✅ Caching system working correctly")
        return True
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test the enhanced API endpoints."""
    print("🌐 Testing enhanced API endpoints...")
    
    # Start the FastAPI server in background
    server_process = None
    try:
        print("Starting FastAPI server...")
        server_process = subprocess.Popen(
            [sys.executable, "api_gateway.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_root
        )
        
        # Wait for server to start
        time.sleep(3)
        
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code in [200, 503]  # 503 is OK for degraded health
        health_data = response.json()
        assert 'status' in health_data
        assert 'timestamp' in health_data
        print("✅ Health endpoint working")
        
        # Test metrics endpoint
        response = requests.get(f"{base_url}/metrics", timeout=5)
        assert response.status_code == 200
        metrics_data = response.json()
        assert 'system' in metrics_data
        assert 'api' in metrics_data
        print("✅ Metrics endpoint working")
        
        # Test cache stats endpoint
        response = requests.get(f"{base_url}/cache/stats", timeout=5)
        assert response.status_code == 200
        cache_data = response.json()
        assert 'backend' in cache_data
        print("✅ Cache stats endpoint working")
        
        # Test agents endpoint
        response = requests.get(f"{base_url}/agents", timeout=5)
        assert response.status_code == 200
        agents_data = response.json()
        assert isinstance(agents_data, dict)
        print("✅ Agents endpoint working")
        
        print("✅ API endpoints working correctly")
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False
    finally:
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

def test_typescript_config():
    """Test TypeScript configuration compilation."""
    print("📦 Testing TypeScript compilation...")
    
    try:
        # Check if TypeScript compiled successfully
        dist_path = project_root / "apps" / "companion_api" / "dist" / "companion_api" / "src"
        if dist_path.exists():
            config_js = dist_path / "config.js"
            middleware_js = dist_path / "middleware.js"
            index_js = dist_path / "index.js"
            
            if config_js.exists() and middleware_js.exists() and index_js.exists():
                print("✅ TypeScript compilation successful")
                return True
        
        print("❌ TypeScript compilation incomplete")
        return False
    except Exception as e:
        print(f"❌ TypeScript test failed: {e}")
        return False

def main():
    """Run all tests and provide summary."""
    print("🚀 Running Phase 3 Backend Improvements Tests\n")
    
    tests = [
        ("Configuration System", test_configuration),
        ("Health Monitoring", test_health_monitoring),
        ("Caching System", test_caching),
        ("TypeScript Compilation", test_typescript_config),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} Tests")
        print(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests, {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! Phase 3 backend improvements are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)