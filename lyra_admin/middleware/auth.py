"""
Authentication and security middleware for Lyra Flask applications.

This module provides:
- Authentication decorators
- CSRF protection utilities  
- Input sanitization helpers
- Secure session management
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify, current_app
import hmac
import secrets
import hashlib
import re
import html
from typing import Any, Callable, Optional


def require_auth(f: Callable) -> Callable:
    """
    Decorator to require authentication for admin routes.
    
    Redirects to login if not authenticated, otherwise allows access.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def generate_csrf_token() -> str:
    """Generate a CSRF token and store it in the session."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']


def verify_csrf_token(token: str) -> bool:
    """Verify a CSRF token against the session token."""
    session_token = session.get('csrf_token', '')
    if not session_token or not token:
        return False
    return hmac.compare_digest(token, session_token)


def require_csrf(f: Callable) -> Callable:
    """
    Decorator to require CSRF token for POST/PUT/DELETE requests.
    
    Checks for CSRF token in form data or X-CSRF-Token header.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE']:
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            if not verify_csrf_token(token):
                if request.is_json:
                    return jsonify({'error': 'CSRF token missing or invalid'}), 403
                return 'CSRF token missing or invalid', 403
        return f(*args, **kwargs)
    return decorated


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input by escaping HTML and limiting length.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Limit length
    text = text[:max_length]
    
    # Escape HTML
    text = html.escape(text)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text.strip()


def sanitize_terminal_command(command: str) -> str:
    """
    Sanitize terminal commands to prevent injection attacks.
    
    Args:
        command: Terminal command to sanitize
        
    Returns:
        Sanitized command or empty string if dangerous
        
    Raises:
        ValueError: If command contains dangerous patterns
    """
    if not isinstance(command, str):
        raise ValueError("Command must be a string")
    
    command = command.strip()
    if not command:
        return ""
    
    # Block dangerous commands and patterns
    dangerous_patterns = [
        r';',           # Command chaining
        r'\|',          # Pipes
        r'&',           # Background execution
        r'\$\(',        # Command substitution
        r'`',           # Backticks
        r'rm\s',        # File deletion
        r'sudo\s',      # Privilege escalation
        r'su\s',        # User switching
        r'chmod\s',     # Permission changes
        r'chown\s',     # Ownership changes
        r'wget\s',      # Network downloads
        r'curl\s.*-o',  # File downloads
        r'nc\s',        # Netcat
        r'>/dev/',      # Device access
        r'</dev/',      # Device access
        r'mkdir.*\.\.',  # Directory traversal
        r'cd.*\.\.',    # Directory traversal
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            raise ValueError(f"Command contains dangerous pattern: {pattern}")
    
    # Allow only specific safe commands
    allowed_commands = [
        'ls', 'pwd', 'whoami', 'date', 'uptime', 'df', 'free', 
        'ps', 'top', 'htop', 'cat', 'head', 'tail', 'grep',
        'find', 'which', 'echo', 'wc', 'sort', 'uniq'
    ]
    
    command_parts = command.split()
    if command_parts:
        base_command = command_parts[0]
        if base_command not in allowed_commands:
            raise ValueError(f"Command not allowed: {base_command}")
    
    return command


def secure_session_config(app) -> None:
    """
    Configure secure session settings for Flask app.
    
    Args:
        app: Flask application instance
    """
    # Generate secure secret key if not set
    if not app.secret_key:
        app.secret_key = secrets.token_hex(32)
        app.logger.warning("Generated random secret key. Set SECRET_KEY env var for production.")
    
    # Secure session cookies
    app.config.update(
        SESSION_COOKIE_SECURE=True,      # HTTPS only
        SESSION_COOKIE_HTTPONLY=True,    # No JavaScript access
        SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
        PERMANENT_SESSION_LIFETIME=3600, # 1 hour timeout
    )


def rate_limit_key(identifier: str) -> str:
    """Generate a rate limiting key for the given identifier."""
    return f"rate_limit:{hashlib.sha256(identifier.encode()).hexdigest()}"


def check_rate_limit(identifier: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
    """
    Simple in-memory rate limiting check.
    
    Args:
        identifier: Unique identifier (IP, user ID, etc.)
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        
    Returns:
        True if request is allowed, False if rate limited
        
    Note: This is a simple implementation. For production, use Redis or similar.
    """
    import time
    
    if not hasattr(current_app, '_rate_limits'):
        current_app._rate_limits = {}
    
    key = rate_limit_key(identifier)
    now = time.time()
    
    # Clean up old entries
    current_app._rate_limits = {
        k: v for k, v in current_app._rate_limits.items() 
        if now - v['first_request'] < window_seconds
    }
    
    if key not in current_app._rate_limits:
        current_app._rate_limits[key] = {
            'count': 1,
            'first_request': now
        }
        return True
    
    rate_data = current_app._rate_limits[key]
    if now - rate_data['first_request'] >= window_seconds:
        # Reset window
        rate_data['count'] = 1
        rate_data['first_request'] = now
        return True
    
    if rate_data['count'] >= max_requests:
        return False
    
    rate_data['count'] += 1
    return True


def rate_limited(max_requests: int = 10, window_seconds: int = 60):
    """
    Decorator to add rate limiting to routes.
    
    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # Use IP address as identifier
            identifier = request.environ.get('REMOTE_ADDR', 'unknown')
            
            if not check_rate_limit(identifier, max_requests, window_seconds):
                if request.is_json:
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                return 'Rate limit exceeded', 429
            
            return f(*args, **kwargs)
        return decorated
    return decorator


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(email, str) or not email:
        return False
    
    # Simple email validation regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= 254


def log_security_event(event_type: str, details: dict, level: str = 'WARNING') -> None:
    """
    Log security-related events.
    
    Args:
        event_type: Type of security event
        details: Additional details about the event
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    import logging
    
    logger = current_app.logger if current_app else logging.getLogger(__name__)
    
    log_data = {
        'event_type': event_type,
        'timestamp': secrets.token_hex(8),  # Simple timestamp ID
        'ip': request.environ.get('REMOTE_ADDR', 'unknown') if request else 'unknown',
        'user_agent': request.headers.get('User-Agent', 'unknown') if request else 'unknown',
        **details
    }
    
    message = f"Security Event: {event_type} - {log_data}"
    
    if level == 'DEBUG':
        logger.debug(message)
    elif level == 'INFO':
        logger.info(message)
    elif level == 'WARNING':
        logger.warning(message)
    elif level == 'ERROR':
        logger.error(message)
    else:  # CRITICAL
        logger.critical(message)