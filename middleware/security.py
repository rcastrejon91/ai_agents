"""
Enhanced middleware for FastAPI backend with security, validation, and monitoring.
"""
import json
import time
import uuid
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import logging

from config.settings import settings


# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.monitoring.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware with rate limiting and validation."""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Rate limiting
        if not self.rate_limiter.allow_request(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60
                }
            )
        
        # Request size validation
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.security.max_request_size:
            logger.warning(f"Request too large from IP: {client_ip}, size: {content_length}")
            return JSONResponse(
                status_code=413,
                content={
                    "error": "request_too_large",
                    "message": "Request body too large",
                    "max_size": settings.security.max_request_size
                }
            )
        
        # Add security headers
        response = await call_next(request)
        self._add_security_headers(response)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers."""
        # Check for proxy headers first
        for header in ["x-forwarded-for", "x-real-ip", "cf-connecting-ip"]:
            ip = request.headers.get(header)
            if ip:
                return ip.split(",")[0].strip()
        
        # Fallback to client host
        return getattr(request.client, "host", "unknown")
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response."""
        if settings.is_production():
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Comprehensive request logging and monitoring middleware."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Log request start
        if settings.monitoring.enable_request_logging:
            logger.info(
                "Request started",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": self._get_client_ip(request),
                    "user_agent": request.headers.get("user-agent", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Add request ID to state for later use
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise
        
        # Log successful request completion
        duration = time.time() - start_time
        if settings.monitoring.enable_request_logging:
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "response_size": response.headers.get("content-length", "unknown")
                }
            )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers."""
        for header in ["x-forwarded-for", "x-real-ip", "cf-connecting-ip"]:
            ip = request.headers.get(header)
            if ip:
                return ip.split(",")[0].strip()
        return getattr(request.client, "host", "unknown")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Centralized error handling with structured responses."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            # Let FastAPI handle HTTP exceptions normally
            raise
        except Exception as e:
            # Log unexpected errors
            request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
            logger.exception(
                "Unhandled exception",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            
            # Return structured error response
            error_response = {
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "request_id": request_id
            }
            
            if settings.debug:
                error_response["debug"] = {
                    "error_type": type(e).__name__,
                    "error_details": str(e)
                }
            
            return JSONResponse(
                status_code=500,
                content=error_response
            )


class RateLimiter:
    """Token bucket rate limiter for API endpoints."""
    
    def __init__(self):
        self.buckets: Dict[str, Dict[str, Any]] = {}
        self.rate = settings.security.rate_limit_per_minute
        self.burst = settings.security.rate_limit_burst
    
    def allow_request(self, client_id: str) -> bool:
        """Check if request is allowed for the given client."""
        now = time.time()
        
        if client_id not in self.buckets:
            self.buckets[client_id] = {
                "tokens": self.burst,
                "last_update": now
            }
        
        bucket = self.buckets[client_id]
        
        # Add tokens based on time elapsed
        time_passed = now - bucket["last_update"]
        tokens_to_add = time_passed * (self.rate / 60.0)  # rate per minute to per second
        bucket["tokens"] = min(self.burst, bucket["tokens"] + tokens_to_add)
        bucket["last_update"] = now
        
        # Check if request is allowed
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        
        return False
    
    def cleanup_old_buckets(self, max_age: int = 3600):
        """Remove old bucket entries to prevent memory leaks."""
        now = time.time()
        to_remove = [
            client_id for client_id, bucket in self.buckets.items()
            if now - bucket["last_update"] > max_age
        ]
        for client_id in to_remove:
            del self.buckets[client_id]


def validate_request_json(required_fields: Optional[list] = None) -> callable:
    """Decorator for request JSON validation."""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            try:
                body = await request.json()
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_json",
                        "message": "Request body must be valid JSON"
                    }
                )
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in body]
                if missing_fields:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "missing_fields",
                            "message": "Required fields are missing",
                            "missing_fields": missing_fields
                        }
                    )
            
            return await func(request, body, *args, **kwargs)
        return wrapper
    return decorator