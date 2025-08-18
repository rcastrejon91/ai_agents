from functools import wraps
from flask import request, abort, current_app
import re
import time
from typing import Dict, Any


class SimpleCache:
    """Simple in-memory cache for rate limiting"""
    def __init__(self):
        self._data: Dict[str, Any] = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        item = self._data.get(key)
        if item is None:
            return default
        
        # Check if expired
        if time.time() > item['expires']:
            del self._data[key]
            return default
        
        return item['value']
    
    def set(self, key: str, value: Any, expire_time: int = 60) -> None:
        self._data[key] = {
            'value': value,
            'expires': time.time() + expire_time
        }
    
    def incr(self, key: str) -> int:
        current = self.get(key, 0)
        new_value = current + 1
        # Keep the same expiration time if it exists
        item = self._data.get(key)
        expire_time = 60
        if item and 'expires' in item:
            expire_time = int(item['expires'] - time.time())
        self.set(key, new_value, max(expire_time, 1))
        return new_value
    
    def expire(self, key: str, seconds: int) -> None:
        if key in self._data:
            self._data[key]['expires'] = time.time() + seconds


# Global cache instance
cache = SimpleCache()


def validate_input(f):
    """Decorator to validate input parameters against XSS and injection attacks"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Validate request parameters
        for key, value in request.values.items():
            if not re.match(r'^[\w\-\s\.@]+$', str(value)):
                current_app.logger.warning(f'Invalid input detected: {key}={value}')
                abort(400, 'Invalid input')
        
        # Validate JSON body if present
        if request.is_json and request.json:
            for key, value in request.json.items():
                if isinstance(value, str) and not re.match(r'^[\w\-\s\.@,!?]+$', value):
                    current_app.logger.warning(f'Invalid JSON input detected: {key}={value}')
                    abort(400, 'Invalid input')
        
        return f(*args, **kwargs)
    return decorated


def rate_limit(limit_per_minute=60):
    """Decorator to implement rate limiting based on IP address"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get client IP
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip:
                ip = ip.split(',')[0].strip()
            else:
                ip = 'unknown'
            
            # Implement rate limiting logic
            key = f'{ip}:{f.__name__}'
            current = cache.get(key, 0)
            
            if current >= limit_per_minute:
                current_app.logger.warning(f'Rate limit exceeded for IP {ip} on endpoint {f.__name__}')
                abort(429, 'Too many requests')
            
            cache.incr(key)
            cache.expire(key, 60)
            
            return f(*args, **kwargs)
        return decorated
    return decorator


def security_headers(f):
    """Decorator to add security headers to responses"""
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import make_response
        
        response = f(*args, **kwargs)
        
        # Convert to response object if needed
        if not hasattr(response, 'headers'):
            response = make_response(response)
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        return response
    return decorated


def validate_content_length(max_length=1048576):  # 1MB default
    """Decorator to validate request content length"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            content_length = request.content_length
            if content_length and content_length > max_length:
                current_app.logger.warning(f'Request content too large: {content_length} bytes')
                abort(413, 'Request entity too large')
            return f(*args, **kwargs)
        return decorated
    return decorator


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal attacks"""
    # Remove path components and keep only the filename
    filename = filename.split('/')[-1].split('\\')[-1]
    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    return filename


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Accept various phone formats
    pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
    return bool(re.match(pattern, phone))