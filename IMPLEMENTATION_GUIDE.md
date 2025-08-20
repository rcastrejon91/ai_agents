# Security, Testing and Infrastructure Improvements - Usage Guide

This document provides comprehensive usage instructions for all the newly implemented security, testing, and infrastructure improvements.

## 🔒 Enhanced Security Middleware

### Basic Usage

```python
from middleware.security import comprehensive_security, validate_input, rate_limit, csrf_protect

# Apply comprehensive security to a Flask route
@app.route('/api/secure-endpoint', methods=['POST'])
@comprehensive_security(
    rate_limit_per_minute=30,
    burst_limit=10,
    require_csrf=True,
    check_user_agent=True,
    apply_security_headers=True
)
def secure_endpoint():
    return jsonify({"status": "success"})

# Individual security decorators
@app.route('/api/validate-only')
@validate_input
def validate_only():
    return jsonify({"status": "validated"})

@app.route('/api/rate-limited')
@rate_limit(limit_per_minute=100, burst_limit=20, block_duration=600)
def rate_limited():
    return jsonify({"status": "within limits"})
```

### Advanced Security Features

```python
from middleware.security import (
    require_csrf_rotation, require_csrf_for_get,
    session_security, file_upload_security,
    get_security_metrics
)

# CSRF protection with token rotation
@app.route('/api/sensitive-operation', methods=['POST'])
@require_csrf_rotation
@csrf_protect
def sensitive_operation():
    return jsonify({"status": "token rotated"})

# File upload with security
@app.route('/api/upload', methods=['POST'])
@file_upload_security(allowed_extensions=['.jpg', '.png', '.pdf'])
def upload_file():
    return jsonify({"status": "file uploaded safely"})

# Get security metrics
@app.route('/api/security-metrics')
def security_metrics():
    return jsonify(get_security_metrics())
```

## 🧪 Comprehensive Testing Suite

### Running Security Tests

```bash
# Run all security tests
python tests/test_security.py

# Run with pytest (if available)
pytest tests/test_security.py -v

# Run specific test classes
python -c "
from tests.test_security import TestSecurityMiddleware
test = TestSecurityMiddleware()
test.test_validate_input_valid_data()
print('✅ Validation test passed')
"
```

### Test Coverage

The test suite includes:
- **Security Middleware Tests**: Rate limiting, CSRF, input validation
- **Logging Tests**: JSON formatting, request context, exception handling
- **Integration Tests**: Multiple decorators working together
- **Edge Case Tests**: Error conditions and boundary cases

## 📝 Enhanced Logging System

### Basic Logging Setup

```python
from utils.logging import setup_logging, log_security_event, performance_timer

# Setup enhanced logging
logger, perf_logger = setup_logging(
    log_level="INFO",
    enable_file_logging=True
)

# Log security events
log_security_event("suspicious_activity", {
    "ip": "192.168.1.100",
    "user_agent": "suspicious-bot",
    "endpoint": "/api/admin"
}, severity="high")

# Performance timing
with performance_timer("database_query"):
    # Your database operation here
    result = db.query("SELECT * FROM users")
```

### Advanced Logging Features

```python
from utils.logging import (
    CustomJSONFormatter, SecurityAuditFormatter,
    PerformanceLogger, log_request_completion
)

# Custom formatter with sanitization
formatter = CustomJSONFormatter(
    include_request_data=True,
    sanitize_sensitive_data=True
)

# Performance logging
perf_logger = PerformanceLogger(logger)
perf_logger.log_request_timing("/api/users", 0.245, 200)
perf_logger.log_database_query("SELECT", 0.123, 50)
perf_logger.log_cache_operation("GET", "user:123", hit=True)
```

## ⚡ Frontend Optimization Engine

### Basic Usage

Include the optimization script in your HTML:

```html
<script src="/static/js/optimization.js"></script>
<script>
    // The engine auto-initializes
    // Access global functions:
    
    // Optimized fetch with caching
    optimizedFetch('/api/data')
        .then(data => console.log('Cached data:', data));
    
    // Optimized DOM updates
    optimizedDOMUpdate(() => {
        document.getElementById('content').innerHTML = 'Updated!';
    });
    
    // Get performance metrics
    const metrics = getPerformanceMetrics();
    console.log('Performance:', metrics);
</script>
```

### Advanced Features

```html
<!-- Lazy loading images -->
<img data-src="/path/to/image.jpg" alt="Lazy loaded image">

<!-- Lazy loading triggers -->
<button data-lazy-trigger>Load More Content</button>

<!-- Cache management -->
<button data-clear-cache>Clear Cache</button>

<script>
    // Access the optimization engine directly
    const engine = window.OptimizationEngine;
    
    // Configure settings
    engine.config.lazyLoadOffset = 100;
    engine.config.throttleDelay = 8; // ~120fps
    
    // Manual cache operations
    engine.setCache('user_data', userData, 60000); // 1 minute
    const cached = engine.getCache('user_data');
    
    // Export metrics for monitoring
    const metrics = engine.exportMetrics();
    console.log('Cache hits:', metrics.cacheHits);
    console.log('Network requests:', metrics.networkRequests);
</script>
```

## 🛡️ Enhanced ErrorBoundary Component

### Basic Usage

```tsx
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary 
      componentName="MainApp"
      maxRetries={3}
      enableMetrics={true}
      onError={(error, errorInfo) => {
        console.log('Custom error handler:', error);
      }}
    >
      <YourComponent />
    </ErrorBoundary>
  );
}
```

### Advanced Features

```tsx
import { ErrorBoundary, ChatErrorFallback } from './components/ErrorBoundary';

// Custom fallback component
const CustomFallback = ({ error, resetError }) => (
  <div>
    <h2>Custom Error UI</h2>
    <button onClick={resetError}>Try Again</button>
  </div>
);

// Chat interface with specialized error boundary
function ChatApp() {
  return (
    <ErrorBoundary 
      componentName="ChatInterface"
      fallback={ChatErrorFallback}
      maxRetries={5}
      enableMetrics={true}
    >
      <ChatComponent />
    </ErrorBoundary>
  );
}
```

## 🚀 Railway Deployment Configuration

### Enhanced Services

The updated `railway.yaml` includes:

```yaml
services:
  web:
    # Enhanced environment variables
    env:
      - SECURITY_ENABLED=true
      - RATE_LIMIT_ENABLED=true
      - LOG_LEVEL=info
      - CORS_ENABLED=true
    
    # Advanced health checks
    healthcheck:
      path: /health
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # Scaling configuration
    deploy:
      strategy: rolling
      max_replicas: 3
      min_replicas: 1

  redis:
    # Optimized Redis configuration
    command: redis-server --maxmemory 200mb --maxmemory-policy allkeys-lru
    
  monitoring:
    # Prometheus monitoring
    image: prom/prometheus:latest
```

### Health Check Endpoints

```python
@app.route('/health')
def health_check():
    return jsonify({
        "ok": True,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("NODE_ENV", "development"),
        "version": "1.0.0",
        "services": {
            "redis": check_redis_connection(),
            "database": check_database_connection()
        }
    })

@app.route('/ready')
def readiness_check():
    # Readiness check for deployment platforms
    return jsonify({"ready": True})
```

## 📊 Monitoring and Metrics

### Security Metrics

```python
from middleware.security import get_security_metrics

@app.route('/api/admin/security-metrics')
@comprehensive_security(rate_limit_per_minute=10)
def admin_security_metrics():
    metrics = get_security_metrics()
    return jsonify({
        "security": metrics,
        "timestamp": time.time()
    })
```

### Performance Monitoring

```javascript
// Frontend performance monitoring
setInterval(() => {
    const metrics = getPerformanceMetrics();
    
    // Send to monitoring service
    fetch('/api/metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metrics)
    });
}, 60000); // Every minute
```

## 🔧 Configuration Options

### Security Configuration

```python
# Customize security settings
from middleware.security import SECURITY_CONFIG

SECURITY_CONFIG.update({
    "max_request_size": 2 * 1024 * 1024,  # 2MB
    "session_timeout": 60 * 60,  # 1 hour
    "max_login_attempts": 3,
    "lockout_duration": 30 * 60,  # 30 minutes
})
```

### Logging Configuration

```python
# Setup with custom configuration
logger, perf_logger = setup_logging(
    log_level="DEBUG",  # More verbose logging
    enable_file_logging=True
)

# Custom formatter settings
formatter = CustomJSONFormatter(
    include_request_data=False,  # Disable request data
    sanitize_sensitive_data=True
)
```

## 🚨 Security Best Practices

1. **Always use comprehensive_security** for sensitive endpoints
2. **Enable CSRF protection** for state-changing operations
3. **Configure rate limiting** based on your application needs
4. **Monitor security metrics** regularly
5. **Use sanitized logging** to prevent information leakage
6. **Implement proper error boundaries** in React components
7. **Set up health checks** for deployment monitoring

## 📈 Performance Optimization Tips

1. **Enable lazy loading** for images and resources
2. **Use optimized fetch** with caching for API calls
3. **Implement performance timing** for critical operations
4. **Monitor cache hit rates** and adjust cache expiry
5. **Use event delegation** for efficient event handling
6. **Configure proper resource limits** in Railway deployment

This comprehensive implementation provides production-ready security, testing, and infrastructure improvements for the AI Agents repository.