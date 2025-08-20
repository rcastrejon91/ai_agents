import json
import logging
import traceback
import uuid
import os
from datetime import datetime
from typing import Dict, Any, Optional

from flask import request, has_request_context


class CustomJSONFormatter(logging.Formatter):
    """Enhanced JSON formatter with security and performance metrics."""
    
    def __init__(self, include_request_data=True, sanitize_sensitive_data=True):
        super().__init__()
        self.include_request_data = include_request_data
        self.sanitize_sensitive_data = sanitize_sensitive_data
        self.sensitive_fields = {
            'password', 'passwd', 'secret', 'token', 'key', 'auth',
            'authorization', 'cookie', 'session', 'csrf'
        }

    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process,
        }

        # Add request ID if available
        request_id = getattr(record, "request_id", None)
        if not request_id and has_request_context():
            request_id = getattr(request, "id", None)
        
        if request_id:
            log_record["request_id"] = request_id

        # Add request context if available and enabled
        if self.include_request_data and has_request_context():
            try:
                request_data = {
                    "method": request.method,
                    "path": request.path,
                    "ip": self._get_real_ip(),
                    "user_agent": request.headers.get('User-Agent', '')[:200],  # Truncate
                    "referrer": request.headers.get('Referer', ''),
                }
                
                # Add query parameters (sanitized)
                if request.args:
                    request_data["query_params"] = dict(request.args)
                    if self.sanitize_sensitive_data:
                        request_data["query_params"] = self._sanitize_data(request_data["query_params"])
                
                # Add form data size (not content for security)
                if request.form:
                    request_data["form_data_size"] = len(request.form)
                
                # Add file upload info
                if request.files:
                    request_data["uploaded_files"] = [
                        {
                            "field_name": field_name,
                            "filename": file.filename,
                            "content_type": file.content_type,
                            "content_length": len(file.read()) if hasattr(file, 'read') else None
                        }
                        for field_name, file in request.files.items()
                    ]
                
                log_record["request"] = request_data
                
            except Exception as e:
                log_record["request_error"] = str(e)

        # Add exception information
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add custom fields from extra
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
                'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'message', 'request_id'
            }:
                if self.sanitize_sensitive_data and any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    log_record[key] = "[SANITIZED]"
                else:
                    log_record[key] = value

        return json.dumps(log_record, default=self._json_default, ensure_ascii=False)

    def _get_real_ip(self) -> str:
        """Get the real IP address, considering proxies."""
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.remote_addr or 'unknown'

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data from request parameters."""
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                sanitized[key] = "[SANITIZED]"
            else:
                sanitized[key] = value
        return sanitized

    def _json_default(self, obj):
        """Handle non-serializable objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)


class SecurityAuditFormatter(CustomJSONFormatter):
    """Specialized formatter for security audit logs."""
    
    def format(self, record):
        log_data = json.loads(super().format(record))
        
        # Add security-specific fields
        log_data["audit_type"] = "security"
        log_data["severity"] = getattr(record, "severity", "medium")
        log_data["threat_type"] = getattr(record, "threat_type", "unknown")
        log_data["client_identifier"] = getattr(record, "client_identifier", None)
        
        # Add geolocation if available
        if hasattr(record, "country") or hasattr(record, "city"):
            log_data["geolocation"] = {
                "country": getattr(record, "country", None),
                "city": getattr(record, "city", None),
                "region": getattr(record, "region", None)
            }
        
        return json.dumps(log_data, default=self._json_default, ensure_ascii=False)


class PerformanceLogger:
    """Logger for performance metrics and profiling."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics = {}
    
    def log_request_timing(self, endpoint: str, duration: float, status_code: int):
        """Log request timing information."""
        self.logger.info(
            f"Request completed: {endpoint}",
            extra={
                "performance_metric": True,
                "endpoint": endpoint,
                "duration_ms": round(duration * 1000, 2),
                "status_code": status_code,
                "metric_type": "request_timing"
            }
        )
    
    def log_database_query(self, query_type: str, duration: float, rows_affected: int = None):
        """Log database query performance."""
        self.logger.info(
            f"Database query: {query_type}",
            extra={
                "performance_metric": True,
                "query_type": query_type,
                "duration_ms": round(duration * 1000, 2),
                "rows_affected": rows_affected,
                "metric_type": "database_query"
            }
        )
    
    def log_cache_operation(self, operation: str, cache_key: str, hit: bool = None):
        """Log cache operations."""
        self.logger.info(
            f"Cache {operation}: {cache_key}",
            extra={
                "performance_metric": True,
                "cache_operation": operation,
                "cache_key": cache_key,
                "cache_hit": hit,
                "metric_type": "cache_operation"
            }
        )


def setup_logging(log_level: str = "INFO", enable_file_logging: bool = True):
    """Enhanced logging setup with multiple handlers and formatters."""
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_formatter = CustomJSONFormatter()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # File handler for application logs
    if enable_file_logging:
        try:
            os.makedirs("logs", exist_ok=True)
            
            # Application logs
            app_handler = logging.FileHandler("logs/app.log")
            app_handler.setFormatter(CustomJSONFormatter())
            app_handler.setLevel(logging.INFO)
            logger.addHandler(app_handler)
            
            # Security audit logs
            security_handler = logging.FileHandler("logs/security.log")
            security_formatter = SecurityAuditFormatter()
            security_handler.setFormatter(security_formatter)
            security_handler.setLevel(logging.WARNING)
            
            # Create security logger
            security_logger = logging.getLogger("security")
            security_logger.addHandler(security_handler)
            security_logger.setLevel(logging.WARNING)
            
            # Error logs
            error_handler = logging.FileHandler("logs/error.log")
            error_handler.setFormatter(CustomJSONFormatter())
            error_handler.setLevel(logging.ERROR)
            logger.addHandler(error_handler)
            
        except Exception as e:
            logger.error(f"Failed to setup file logging: {e}")
    
    # Performance logger
    perf_logger = PerformanceLogger(logger)
    
    return logger, perf_logger


def request_id_middleware():
    """Enhanced request ID middleware with additional context."""
    if has_request_context():
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.id = request_id
        
        # Add start time for performance tracking
        request.start_time = datetime.utcnow()
        
        # Log request start
        logging.getLogger().info(
            f"Request started: {request.method} {request.path}",
            extra={
                "request_id": request_id,
                "event_type": "request_start",
                "client_ip": request.remote_addr,
                "user_agent": request.headers.get('User-Agent', '')[:100]
            }
        )


def log_request_completion(response, duration: float = None):
    """Log request completion with timing information."""
    if has_request_context():
        request_id = getattr(request, 'id', None)
        start_time = getattr(request, 'start_time', None)
        
        if not duration and start_time:
            duration = (datetime.utcnow() - start_time).total_seconds()
        
        logging.getLogger().info(
            f"Request completed: {request.method} {request.path}",
            extra={
                "request_id": request_id,
                "event_type": "request_complete",
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2) if duration else None,
                "response_size": len(response.get_data()) if hasattr(response, 'get_data') else None
            }
        )


def log_security_event(event_type: str, details: Dict[str, Any], severity: str = "medium"):
    """Log security events to dedicated security logger."""
    security_logger = logging.getLogger("security")
    
    security_logger.warning(
        f"Security event: {event_type}",
        extra={
            "event_type": event_type,
            "severity": severity,
            "threat_type": event_type,
            "details": details,
            "client_ip": details.get("ip", request.remote_addr if has_request_context() else None),
            "request_id": getattr(request, 'id', None) if has_request_context() else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def get_logger_metrics():
    """Get logging system metrics."""
    loggers = [logging.getLogger(name) for name in logging.getLogger().manager.loggerDict]
    
    metrics = {
        "total_loggers": len(loggers),
        "handlers_by_logger": {},
        "log_levels": {},
        "file_handlers": []
    }
    
    for logger in loggers:
        metrics["handlers_by_logger"][logger.name] = len(logger.handlers)
        metrics["log_levels"][logger.name] = logging.getLevelName(logger.level)
        
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                metrics["file_handlers"].append({
                    "logger": logger.name,
                    "filename": handler.baseFilename,
                    "level": logging.getLevelName(handler.level)
                })
    
    return metrics


# Context manager for performance logging
class performance_timer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, logger: logging.Logger = None):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(
                f"Operation failed: {self.operation_name}",
                extra={
                    "operation": self.operation_name,
                    "duration_ms": round(duration * 1000, 2),
                    "success": False,
                    "error_type": exc_type.__name__ if exc_type else None
                }
            )
        else:
            self.logger.info(
                f"Operation completed: {self.operation_name}",
                extra={
                    "operation": self.operation_name,
                    "duration_ms": round(duration * 1000, 2),
                    "success": True
                }
            )
