import re
import hashlib
import time
from functools import wraps
from typing import Dict, List, Optional, Any

import redis
from flask import abort, current_app, request, session, jsonify

# Redis connection for rate limiting and security tracking
redis_client = redis.Redis(host="localhost", port=6379, db=0)

# Security configuration
SECURITY_CONFIG = {
    "max_request_size": 1024 * 1024,  # 1MB
    "session_timeout": 30 * 60,  # 30 minutes
    "max_login_attempts": 5,
    "lockout_duration": 15 * 60,  # 15 minutes
    "allowed_file_types": [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt"],
    "blocked_user_agents": ["curl", "wget", "python-requests"],
    "honeypot_fields": ["email_confirm", "phone_backup"],
}

# Threat tracking
class ThreatTracker:
    def __init__(self):
        self.threats = {}
    
    def record_threat(self, ip: str, threat_type: str, severity: str = "medium"):
        key = f"threat:{ip}"
        threat_data = {
            "type": threat_type,
            "severity": severity,
            "timestamp": time.time(),
            "count": 1
        }
        
        # Get existing threats
        existing = redis_client.hgetall(key)
        if existing:
            threat_data["count"] = int(existing.get(b"count", 0)) + 1
        
        # Store threat data
        redis_client.hmset(key, threat_data)
        redis_client.expire(key, 24 * 60 * 60)  # 24 hours
        
        # Log threat
        current_app.logger.warning(
            f"Security threat detected: {threat_type}",
            extra={
                "ip": ip,
                "severity": severity,
                "count": threat_data["count"],
                "request_id": getattr(request, "id", None)
            }
        )

threat_tracker = ThreatTracker()


def validate_input(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Enhanced input validation
        for key, value in request.values.items():
            # Strict input validation pattern
            if not re.match(r"^[\w\-\s\.@]+$", str(value)):
                current_app.logger.warning(
                    f"Invalid input detected: {key}={value}",
                    extra={"request_id": request.id},
                )
                abort(400, "Invalid input detected")
        return f(*args, **kwargs)

    return decorated


def rate_limit(limit_per_minute=60):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            key = f"ratelimit:{request.remote_addr}:{f.__name__}"
            current = redis_client.get(key)

            if current and int(current) >= limit_per_minute:
                current_app.logger.warning(
                    f"Rate limit exceeded for {request.remote_addr}",
                    extra={"request_id": request.id},
                )
                abort(429, "Rate limit exceeded")

            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)
            pipe.execute()

            return f(*args, **kwargs)

        return decorated

    return decorator


def csrf_protect(f):
    """Enhanced CSRF protection with token rotation."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Skip CSRF for GET requests (unless explicitly required)
        if request.method == "GET" and not getattr(f, '_csrf_required_for_get', False):
            return f(*args, **kwargs)
        
        token = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
        stored_token = session.get("csrf_token")

        if not token or not stored_token or token != stored_token:
            threat_tracker.record_threat(request.remote_addr, "csrf_violation", "high")
            current_app.logger.error(
                "CSRF token validation failed",
                extra={
                    "request_id": getattr(request, "id", None),
                    "has_token": bool(token),
                    "has_stored_token": bool(stored_token),
                    "tokens_match": token == stored_token if token and stored_token else False
                }
            )
            abort(403, "CSRF validation failed")
        
        # Rotate CSRF token after successful validation (for high-security operations)
        if getattr(f, '_rotate_csrf_token', False):
            session["csrf_token"] = hashlib.sha256(
                f"{time.time()}:{request.remote_addr}".encode()
            ).hexdigest()[:32]
        
        return f(*args, **kwargs)
    return decorated


def require_csrf_rotation(f):
    """Decorator to mark functions that should rotate CSRF tokens."""
    f._rotate_csrf_token = True
    return f


def require_csrf_for_get(f):
    """Decorator to require CSRF protection even for GET requests."""
    f._csrf_required_for_get = True
    return f


def session_security(f):
    """Enhanced session security checks."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check session timeout
        if "created_at" in session:
            session_age = time.time() - session["created_at"]
            if session_age > SECURITY_CONFIG["session_timeout"]:
                session.clear()
                threat_tracker.record_threat(request.remote_addr, "session_timeout", "low")
                abort(401, "Session expired")
        else:
            session["created_at"] = time.time()
        
        # Check for session hijacking indicators
        stored_ip = session.get("ip_address")
        current_ip = request.remote_addr
        
        if stored_ip and stored_ip != current_ip:
            # Allow for reasonable IP changes (mobile networks, etc.)
            # But log suspicious changes
            current_app.logger.warning(
                f"Session IP change detected: {stored_ip} -> {current_ip}",
                extra={"request_id": getattr(request, "id", None)}
            )
            # Optionally, you could invalidate the session here for high-security apps
        
        session["ip_address"] = current_ip
        session["last_activity"] = time.time()
        
        return f(*args, **kwargs)
    return decorated


def comprehensive_security(
    rate_limit_per_minute=60,
    burst_limit=None,
    require_csrf=True,
    check_user_agent=True,
    apply_security_headers=True
):
    """Comprehensive security decorator combining multiple protections."""
    def decorator(f):
        # Apply all security layers
        secured_func = f
        
        if apply_security_headers:
            secured_func = security_headers(secured_func)
        
        if check_user_agent:
            secured_func = user_agent_check(secured_func)
        
        if require_csrf:
            secured_func = csrf_protect(secured_func)
        
        secured_func = advanced_rate_limit(rate_limit_per_minute, burst_limit)(secured_func)
        secured_func = validate_input(secured_func)
        secured_func = session_security(secured_func)
        
        return secured_func
    return decorator


def get_security_metrics():
    """Get security metrics for monitoring."""
    try:
        # Get threat counts by type
        threat_keys = redis_client.keys("threat:*")
        threats_by_type = {}
        total_threats = 0
        
        for key in threat_keys:
            threat_data = redis_client.hgetall(key)
            if threat_data:
                threat_type = threat_data.get(b"type", b"unknown").decode()
                count = int(threat_data.get(b"count", 0))
                threats_by_type[threat_type] = threats_by_type.get(threat_type, 0) + count
                total_threats += count
        
        # Get rate limit stats
        rate_limit_keys = redis_client.keys("ratelimit:*")
        active_rate_limits = len(rate_limit_keys)
        
        # Get blocked IPs
        blocked_keys = redis_client.keys("blocked:*")
        blocked_count = len(blocked_keys)
        
        return {
            "total_threats": total_threats,
            "threats_by_type": threats_by_type,
            "active_rate_limits": active_rate_limits,
            "blocked_ips": blocked_count,
            "timestamp": time.time()
        }
    except Exception as e:
        current_app.logger.error(f"Failed to get security metrics: {e}")
        return {"error": "Failed to retrieve metrics"}
