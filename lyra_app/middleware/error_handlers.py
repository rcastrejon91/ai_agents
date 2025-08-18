"""
Error handlers for Lyra Flask applications.

Provides centralized error handling with proper logging and user-friendly responses.
"""

import logging
import traceback
from typing import Any, Dict, Tuple

from flask import jsonify, request
from werkzeug.exceptions import HTTPException


def register_error_handlers(app) -> None:
    """
    Register error handlers for the Flask application.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(400)
    def handle_bad_request(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handle 400 Bad Request errors."""
        app.logger.warning(f"Bad request: {error.description} - {request.url}")

        response = {
            "error": "Bad Request",
            "message": error.description or "Invalid request data",
            "code": 400,
            "request_id": getattr(request, 'request_id', None),
        }

        if request.is_json:
            return jsonify(response), 400
        else:
            return response, 400

    @app.errorhandler(401)
    def handle_unauthorized(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handle 401 Unauthorized errors."""
        app.logger.warning(
            f'Unauthorized access attempt: {request.url} - IP: {request.environ.get("REMOTE_ADDR")}'
        )

        response = {
            "error": "Unauthorized",
            "message": "Authentication required",
            "code": 401,
            "request_id": getattr(request, 'request_id', None),
        }

        if request.is_json:
            return jsonify(response), 401
        else:
            return response, 401

    @app.errorhandler(403)
    def handle_forbidden(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handle 403 Forbidden errors."""
        app.logger.warning(
            f'Forbidden access attempt: {request.url} - IP: {request.environ.get("REMOTE_ADDR")}'
        )

        response = {
            "error": "Forbidden",
            "message": error.description or "Access denied",
            "code": 403,
        }

        if request.is_json:
            return jsonify(response), 403
        else:
            return response, 403

    @app.errorhandler(404)
    def handle_not_found(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handle 404 Not Found errors."""
        app.logger.info(f"Not found: {request.url}")

        response = {
            "error": "Not Found",
            "message": "The requested resource was not found",
            "code": 404,
        }

        if request.is_json:
            return jsonify(response), 404
        else:
            return response, 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handle 405 Method Not Allowed errors."""
        app.logger.warning(f"Method not allowed: {request.method} {request.url}")

        response = {
            "error": "Method Not Allowed",
            "message": f"Method {request.method} not allowed for this endpoint",
            "code": 405,
        }

        if request.is_json:
            return jsonify(response), 405
        else:
            return response, 405

    @app.errorhandler(429)
    def handle_rate_limit(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handle 429 Too Many Requests errors."""
        app.logger.warning(
            f'Rate limit exceeded: {request.url} - IP: {request.environ.get("REMOTE_ADDR")}'
        )

        response = {
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Please try again later.",
            "code": 429,
        }

        if request.is_json:
            return jsonify(response), 429
        else:
            return response, 429

    @app.errorhandler(500)
    def handle_internal_error(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handle 500 Internal Server Error."""
        app.logger.error(f"Internal server error: {request.url}", exc_info=True)

        response = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "code": 500,
        }

        # Don't expose internal error details in production
        if app.debug:
            response["debug_info"] = str(error)

        if request.is_json:
            return jsonify(response), 500
        else:
            return response, 500

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handle all other HTTP exceptions."""
        app.logger.warning(
            f"HTTP error {error.code}: {error.description} - {request.url}"
        )

        response = {
            "error": error.name,
            "message": error.description or "An error occurred",
            "code": error.code,
        }

        if request.is_json:
            return jsonify(response), error.code
        else:
            return response, error.code

    @app.errorhandler(Exception)
    def handle_generic_error(error: Exception) -> Tuple[Dict[str, Any], int]:
        """Handle all other exceptions."""
        # Check for specific API-related errors
        error_name = type(error).__name__
        
        if 'timeout' in error_name.lower() or 'ConnectionTimeout' in error_name:
            app.logger.warning(f"API timeout error: {error}")
            response = {
                "error": "Service Timeout",
                "message": "The request took too long to complete. Please try again.",
                "code": 408,
                "request_id": getattr(request, 'request_id', None),
            }
            return jsonify(response), 408
        
        if 'connection' in error_name.lower() or 'ConnectionError' in error_name:
            app.logger.warning(f"API connection error: {error}")
            response = {
                "error": "Service Unavailable",
                "message": "Unable to connect to external service. Please try again later.",
                "code": 503,
                "request_id": getattr(request, 'request_id', None),
            }
            return jsonify(response), 503
        
        # Log the full traceback for debugging
        app.logger.error(f"Unhandled exception: {str(error)}", exc_info=True)

        response = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "code": 500,
            "request_id": getattr(request, 'request_id', None),
        }

        # Include debug information in development mode
        if app.debug:
            response["debug_info"] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }

        if request.is_json:
            return jsonify(response), 500
        else:
            return response, 500


def setup_logging(app, log_level: str = "INFO") -> None:
    """
    Set up logging configuration for the Flask application.

    Args:
        app: Flask application instance
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Set up logging format
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # Configure the application logger
    if not app.debug:
        # In production, use a more robust logging setup
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        level = getattr(logging, log_level.upper(), logging.INFO)
        handler.setLevel(level)
        app.logger.setLevel(level)
        app.logger.addHandler(handler)

    # Log application startup
    app.logger.info(f"Lyra application starting up - Debug mode: {app.debug}")


def log_request_info(app) -> None:
    """
    Set up request logging middleware.

    Args:
        app: Flask application instance
    """

    @app.before_request
    def log_request():
        """Log incoming requests."""
        if not app.debug:  # Only log in production to avoid noise
            app.logger.info(
                f'{request.method} {request.url} - IP: {request.environ.get("REMOTE_ADDR")}'
            )

    @app.after_request
    def log_response(response):
        """Log outgoing responses."""
        if not app.debug and response.status_code >= 400:
            app.logger.warning(
                f"Response {response.status_code} for {request.method} {request.url}"
            )
        return response
