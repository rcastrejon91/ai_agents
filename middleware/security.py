import re
from functools import wraps

import redis
from flask import abort, current_app, request

# Redis connection for rate limiting
redis_client = redis.Redis(host="localhost", port=6379, db=0)


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
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-CSRF-Token")
        stored_token = request.session.get("csrf_token")

        if not token or not stored_token or token != stored_token:
            current_app.logger.error(
                "CSRF token validation failed", extra={"request_id": request.id}
            )
            abort(403, "CSRF validation failed")
        return f(*args, **kwargs)

    return decorated
