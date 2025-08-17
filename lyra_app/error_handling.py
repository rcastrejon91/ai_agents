# Enhanced error handling utilities for Flask Lyra app
import functools
import logging
import os
import time
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
import requests
from flask import jsonify, request


class LyraAPIError(Exception):
    """Base exception for Lyra API errors."""
    
    def __init__(self, message: str, code: str, status_code: int = 500, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ValidationError(LyraAPIError):
    """Raised when request validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "VALIDATION_ERROR", 400, details)


class UpstreamError(LyraAPIError):
    """Raised when upstream service (OpenAI) fails."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "UPSTREAM_ERROR", 502, details)


class TimeoutError(LyraAPIError):
    """Raised when request times out."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "TIMEOUT_ERROR", 504, details)


class RateLimitError(LyraAPIError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", 429, details)


# Timeout configuration
TIMEOUT_CONFIG = {
    "DEFAULT": 30,  # 30 seconds
    "OPENAI": 45,   # 45 seconds for OpenAI calls
    "RETRY_DELAY": 1,  # 1 second
    "MAX_RETRIES": 3,
}

# Rate limiting storage (in production, use Redis or similar)
_rate_limit_storage = {}


def validate_lyra_request(data: Dict) -> Dict:
    """Validate incoming request data."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object")
    
    message = data.get("message", "").strip()
    if not message:
        raise ValidationError("Message is required and cannot be empty")
    
    if len(message) > 10000:
        raise ValidationError("Message too long (max 10,000 characters)")
    
    history = data.get("history", [])
    if not isinstance(history, list):
        raise ValidationError("History must be an array")
    
    if len(history) > 50:
        raise ValidationError("History too long (max 50 messages)")
    
    for i, msg in enumerate(history):
        if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
            raise ValidationError(f"Invalid history message at index {i}")
        
        if msg["role"] not in ["user", "assistant", "system"]:
            raise ValidationError(f"Invalid role '{msg['role']}' at history index {i}")
    
    return {
        "message": message,
        "history": history,
    }


def rate_limit_check(ip: str, limit_per_minute: int = 30) -> bool:
    """Simple rate limiting implementation."""
    now = time.time()
    window = 60  # 1 minute window
    
    if ip not in _rate_limit_storage:
        _rate_limit_storage[ip] = {"count": 1, "window_start": now}
        return True
    
    bucket = _rate_limit_storage[ip]
    
    # Reset window if expired
    if now - bucket["window_start"] >= window:
        bucket["count"] = 1
        bucket["window_start"] = now
        return True
    
    # Check if limit exceeded
    if bucket["count"] >= limit_per_minute:
        return False
    
    bucket["count"] += 1
    return True


def make_request_with_retry(
    method: str,
    url: str,
    timeout: int = TIMEOUT_CONFIG["DEFAULT"],
    max_retries: int = TIMEOUT_CONFIG["MAX_RETRIES"],
    **kwargs
) -> requests.Response:
    """Make HTTP request with retry logic."""
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs
            )
            
            # Don't retry on 4xx client errors (except 429)
            if 400 <= response.status_code < 500 and response.status_code != 429:
                return response
            
            # Return successful responses or on last attempt
            if response.status_code < 400 or attempt == max_retries:
                return response
            
            logging.warning(f"Request attempt {attempt + 1}/{max_retries + 1} failed with status {response.status_code}")
            
        except requests.exceptions.Timeout as e:
            last_error = TimeoutError(f"Request timed out after {timeout}s")
            
        except requests.exceptions.RequestException as e:
            last_error = UpstreamError(f"Request failed: {str(e)}")
        
        # Don't retry on the last attempt
        if attempt < max_retries:
            delay = TIMEOUT_CONFIG["RETRY_DELAY"] * (2 ** attempt)
            time.sleep(delay)
            logging.warning(f"Retrying request in {delay}s...")
    
    if last_error:
        raise last_error
    else:
        raise UpstreamError("Request failed after all retries")


def create_error_response(error: Exception, request_id: str = None) -> Tuple[Dict, int]:
    """Create standardized error response."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    if isinstance(error, LyraAPIError):
        return {
            "error": "API Error",
            "code": error.code,
            "message": error.message,
            "details": error.details,
            "timestamp": timestamp,
            "request_id": request_id,
        }, error.status_code
    else:
        # Don't expose internal error details
        return {
            "error": "Internal Server Error",
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": timestamp,
            "request_id": request_id,
        }, 500


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    error: Optional[Exception] = None,
    request_id: str = None,
    ip: str = None
):
    """Log request details."""
    log_data = {
        "request_id": request_id,
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration * 1000, 2),
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    if error:
        log_data["error"] = {
            "message": str(error),
            "type": type(error).__name__,
        }
        
        if isinstance(error, LyraAPIError):
            log_data["error"]["code"] = error.code
    
    if error:
        logging.error(f"Request failed: {log_data}")
    else:
        logging.info(f"Request completed: {log_data}")


def generate_request_id() -> str:
    """Generate unique request ID."""
    return f"req_{int(time.time() * 1000)}_{hash(time.time()) % 100000:05d}"


def error_handler(f):
    """Decorator for handling API errors consistently."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        request_id = generate_request_id()
        start_time = time.time()
        
        try:
            # Get client IP
            ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # Add request_id to request context if needed
            request.request_id = request_id
            
            result = f(*args, **kwargs)
            
            # Log successful request
            duration = time.time() - start_time
            log_request(
                method=request.method,
                path=request.path,
                status_code=200,  # Assuming success if no exception
                duration=duration,
                request_id=request_id,
                ip=ip
            )
            
            return result
            
        except Exception as error:
            duration = time.time() - start_time
            ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # Log the error
            log_request(
                method=request.method,
                path=request.path,
                status_code=500,  # Will be updated by create_error_response
                duration=duration,
                error=error,
                request_id=request_id,
                ip=ip
            )
            
            # Log full traceback for debugging
            logging.error(f"Request {request_id} failed with traceback: {traceback.format_exc()}")
            
            # Create standardized error response
            error_response, status_code = create_error_response(error, request_id)
            return jsonify(error_response), status_code
    
    return decorated_function


def check_openai_health() -> Dict:
    """Check OpenAI API health."""
    start_time = time.time()
    
    try:
        response = make_request_with_retry(
            method="GET",
            url="https://api.openai.com/v1/models",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            },
            timeout=5,  # Short timeout for health check
            max_retries=1  # No retries for health check
        )
        
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        if response.status_code == 200:
            return {"status": "healthy", "latency_ms": round(latency, 2)}
        else:
            return {
                "status": "degraded",
                "latency_ms": round(latency, 2),
                "error": f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }