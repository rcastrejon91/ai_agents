import logging
from datetime import datetime, timezone
import json
import sys
from typing import Dict, Any, Optional
from flask import request, has_request_context
import uuid


class CustomJSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'logger': record.name
        }
        
        # Add request context if available
        if has_request_context():
            log_record.update({
                'request_id': getattr(request, 'request_id', None),
                'remote_addr': request.remote_addr,
                'method': request.method,
                'path': request.path,
                'user_agent': request.headers.get('User-Agent', ''),
            })
        
        # Add custom attributes from the record
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
            
        if hasattr(record, 'session_id'):
            log_record['session_id'] = record.session_id
            
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        # Add stack info if present
        if hasattr(record, 'stack_info') and record.stack_info:
            log_record['stack_info'] = record.stack_info
            
        return json.dumps(log_record, default=str)


class SecurityLogger:
    """Specialized logger for security events"""
    
    def __init__(self, name='security'):
        self.logger = logging.getLogger(name)
        
    def log_authentication_attempt(self, username: str, success: bool, ip_address: str, user_agent: str = ''):
        """Log authentication attempts"""
        self.logger.info(
            'Authentication attempt',
            extra={
                'event_type': 'authentication',
                'username': username,
                'success': success,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
    
    def log_rate_limit_violation(self, ip_address: str, endpoint: str, limit: int):
        """Log rate limit violations"""
        self.logger.warning(
            'Rate limit exceeded',
            extra={
                'event_type': 'rate_limit_violation',
                'ip_address': ip_address,
                'endpoint': endpoint,
                'limit': limit,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
    
    def log_input_validation_failure(self, field: str, value: str, ip_address: str):
        """Log input validation failures"""
        self.logger.warning(
            'Input validation failed',
            extra={
                'event_type': 'input_validation_failure',
                'field': field,
                'value': value[:100],  # Truncate for security
                'ip_address': ip_address,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
    
    def log_security_violation(self, violation_type: str, details: Dict[str, Any], ip_address: str):
        """Log general security violations"""
        self.logger.error(
            f'Security violation: {violation_type}',
            extra={
                'event_type': 'security_violation',
                'violation_type': violation_type,
                'details': details,
                'ip_address': ip_address,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )


class RequestLogger:
    """Logger for HTTP requests with correlation tracking"""
    
    def __init__(self, name='requests'):
        self.logger = logging.getLogger(name)
    
    def log_request(self, method: str, path: str, status_code: int, 
                   response_time: float, request_id: str, ip_address: str):
        """Log HTTP request details"""
        self.logger.info(
            f'{method} {path} {status_code}',
            extra={
                'event_type': 'http_request',
                'method': method,
                'path': path,
                'status_code': status_code,
                'response_time': response_time,
                'request_id': request_id,
                'ip_address': ip_address,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )


def setup_logging(level: str = 'INFO', 
                 log_file: Optional[str] = None,
                 json_format: bool = True,
                 include_security_logger: bool = True):
    """Setup comprehensive logging system"""
    
    # Set logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatters
    if json_format:
        formatter = CustomJSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Setup specialized loggers
    if include_security_logger:
        security_logger = logging.getLogger('security')
        security_logger.setLevel(log_level)
        
        request_logger = logging.getLogger('requests')
        request_logger.setLevel(log_level)
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logging.info('Logging system initialized', extra={
        'level': level,
        'json_format': json_format,
        'log_file': log_file,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })


def add_request_id_middleware(app):
    """Flask middleware to add request ID to all requests"""
    
    @app.before_request
    def before_request():
        request.request_id = str(uuid.uuid4())
        request.start_time = datetime.now(timezone.utc)
    
    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            response_time = (datetime.now(timezone.utc) - request.start_time).total_seconds()
            
            # Log the request
            request_logger = RequestLogger()
            request_logger.log_request(
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                response_time=response_time,
                request_id=getattr(request, 'request_id', 'unknown'),
                ip_address=request.remote_addr or 'unknown'
            )
        
        # Add request ID to response headers for tracing
        if hasattr(request, 'request_id'):
            response.headers['X-Request-ID'] = request.request_id
        
        return response


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)


def log_with_context(logger: logging.Logger, level: str, message: str, 
                    user_id: Optional[str] = None, 
                    session_id: Optional[str] = None,
                    correlation_id: Optional[str] = None,
                    **kwargs):
    """Log with additional context"""
    extra = kwargs.copy()
    
    if user_id:
        extra['user_id'] = user_id
    if session_id:
        extra['session_id'] = session_id
    if correlation_id:
        extra['correlation_id'] = correlation_id
    
    if has_request_context() and hasattr(request, 'request_id'):
        extra['request_id'] = request.request_id
    
    getattr(logger, level.lower())(message, extra=extra)


# Global instances for easy access
security_logger = SecurityLogger()
request_logger = RequestLogger()