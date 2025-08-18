"""
API utilities for Lyra Flask applications with retry logic and enhanced error handling.
"""

import logging
import time
import requests
from typing import Optional, Dict, Any, Callable
from functools import wraps


def with_retry(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0):
    """
    Decorator to add retry logic to functions.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logging.error(f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logging.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {delay}s: {e}")
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator


class APIClient:
    """Enhanced API client with retry logic and error handling."""
    
    def __init__(self, base_url: str = None, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Lyra-API-Client/1.0',
            'Accept': 'application/json',
        })
    
    @with_retry(max_retries=2, base_delay=1.0)
    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If request fails after retries
        """
        if self.base_url and not url.startswith('http'):
            url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        
        kwargs.setdefault('timeout', self.timeout)
        
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request."""
        return self.make_request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make POST request."""
        return self.make_request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """Make PUT request."""
        return self.make_request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """Make DELETE request."""
        return self.make_request('DELETE', url, **kwargs)


class OpenAIClient:
    """OpenAI API client with retry logic and error handling."""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.api_key = api_key
        self.client = APIClient(base_url="https://api.openai.com/v1")
        self.client.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        })
    
    @with_retry(max_retries=2, base_delay=1.0)
    def chat_completion(
        self, 
        messages: list, 
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create chat completion with retry logic.
        
        Args:
            messages: List of message objects
            model: Model to use
            temperature: Temperature setting
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Chat completion response
            
        Raises:
            requests.RequestException: If API call fails
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        response = self.client.post("chat/completions", json=data)
        return response.json()
    
    def health_check(self) -> bool:
        """
        Check if OpenAI API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Make a minimal request to check API availability
            self.chat_completion(
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            logging.warning(f"OpenAI health check failed: {e}")
            return False


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle common API errors and provide user-friendly responses.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            logging.error(f"API timeout in {func.__name__}")
            return {
                "error": "Service Timeout",
                "message": "The request took too long to complete. Please try again.",
                "code": 408
            }, 408
        except requests.exceptions.ConnectionError:
            logging.error(f"API connection error in {func.__name__}")
            return {
                "error": "Service Unavailable", 
                "message": "Unable to connect to external service. Please try again later.",
                "code": 503
            }, 503
        except requests.exceptions.HTTPError as e:
            logging.error(f"API HTTP error in {func.__name__}: {e}")
            status_code = e.response.status_code if e.response else 500
            return {
                "error": "External Service Error",
                "message": f"External service returned an error: {status_code}",
                "code": status_code
            }, status_code
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}")
            return {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later.",
                "code": 500
            }, 500
    return wrapper


def validate_environment() -> Dict[str, bool]:
    """
    Validate that all required environment variables are set.
    
    Returns:
        Dictionary with validation results
    """
    import os
    
    results = {}
    required_vars = [
        "OPENAI_API_KEY",
        "FLASK_ENV",
    ]
    
    optional_vars = [
        "PORT",
        "DEBUG",
        "CORS_ORIGINS",
    ]
    
    for var in required_vars:
        results[var] = bool(os.getenv(var))
        if not results[var]:
            logging.warning(f"Required environment variable {var} is not set")
    
    for var in optional_vars:
        results[var] = bool(os.getenv(var))
    
    return results


def create_health_check_response() -> Dict[str, Any]:
    """
    Create comprehensive health check response.
    
    Returns:
        Health check response dictionary
    """
    import os
    from datetime import datetime
    
    env_status = validate_environment()
    
    # Check OpenAI API if key is available
    openai_status = False
    if env_status.get("OPENAI_API_KEY"):
        try:
            openai_client = OpenAIClient(os.getenv("OPENAI_API_KEY"))
            openai_status = openai_client.health_check()
        except Exception as e:
            logging.warning(f"OpenAI health check failed: {e}")
    
    return {
        "status": "healthy" if all(env_status[var] for var in ["OPENAI_API_KEY"]) else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "environment": os.getenv("FLASK_ENV", "development"),
        "services": {
            "openai": openai_status,
            "environment": all(env_status[var] for var in ["OPENAI_API_KEY"]),
        },
        "config": {
            "has_openai_key": env_status.get("OPENAI_API_KEY", False),
            "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
            "port": os.getenv("PORT", "5000"),
        }
    }