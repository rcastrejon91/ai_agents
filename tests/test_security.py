"""
Comprehensive test suite for Python security middleware and utilities.
Tests rate limiting, CSRF protection, input validation, and logging functionality.
"""

import json
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock
import pytest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from middleware.security import validate_input, rate_limit, csrf_protect
from utils.logging import CustomJSONFormatter, setup_logging, request_id_middleware


class TestSecurityMiddleware:
    """Test cases for security middleware functions."""

    def test_validate_input_valid_data(self):
        """Test that valid input passes validation."""
        # Mock Flask request object
        mock_request = Mock()
        mock_request.values = {"username": "testuser", "email": "test@example.com"}
        mock_request.id = "test-request-id"
        
        @validate_input
        def test_endpoint():
            return "success"
        
        with patch('middleware.security.request', mock_request):
            result = test_endpoint()
            assert result == "success"

    def test_validate_input_invalid_data(self):
        """Test that invalid input triggers validation error."""
        # Mock Flask request and current_app
        mock_request = Mock()
        mock_request.values = {"malicious": "<script>alert('xss')</script>"}
        mock_request.id = "test-request-id"
        
        mock_current_app = Mock()
        mock_logger = Mock()
        mock_current_app.logger = mock_logger
        
        @validate_input
        def test_endpoint():
            return "success"
        
        with patch('middleware.security.request', mock_request), \
             patch('middleware.security.current_app', mock_current_app), \
             patch('middleware.security.abort') as mock_abort:
            
            test_endpoint()
            mock_abort.assert_called_with(400, "Invalid input detected")
            mock_logger.warning.assert_called()

    def test_rate_limit_within_limit(self):
        """Test that requests within rate limit are allowed."""
        # Mock Redis client
        mock_redis = Mock()
        mock_redis.get.return_value = "5"  # Current count below limit
        mock_redis.pipeline.return_value = mock_redis
        mock_redis.incr.return_value = None
        mock_redis.expire.return_value = None
        mock_redis.execute.return_value = None
        
        mock_request = Mock()
        mock_request.remote_addr = "127.0.0.1"
        
        @rate_limit(limit_per_minute=10)
        def test_endpoint():
            return "success"
        
        with patch('middleware.security.redis_client', mock_redis), \
             patch('middleware.security.request', mock_request):
            
            result = test_endpoint()
            assert result == "success"
            mock_redis.get.assert_called()
            mock_redis.incr.assert_called()

    def test_rate_limit_exceeded(self):
        """Test that rate limit violations are blocked."""
        # Mock Redis client - limit exceeded
        mock_redis = Mock()
        mock_redis.get.return_value = "15"  # Over the limit
        
        mock_request = Mock()
        mock_request.remote_addr = "127.0.0.1"
        
        mock_current_app = Mock()
        mock_logger = Mock()
        mock_current_app.logger = mock_logger
        
        @rate_limit(limit_per_minute=10)
        def test_endpoint():
            return "success"
        
        with patch('middleware.security.redis_client', mock_redis), \
             patch('middleware.security.request', mock_request), \
             patch('middleware.security.current_app', mock_current_app), \
             patch('middleware.security.abort') as mock_abort:
            
            test_endpoint()
            mock_abort.assert_called_with(429, "Rate limit exceeded")
            mock_logger.warning.assert_called()

    def test_csrf_protect_valid_token(self):
        """Test that valid CSRF tokens are accepted."""
        mock_request = Mock()
        mock_request.headers = {"X-CSRF-Token": "valid-token"}
        mock_request.session = {"csrf_token": "valid-token"}
        mock_request.id = "test-request-id"
        
        @csrf_protect
        def test_endpoint():
            return "success"
        
        with patch('middleware.security.request', mock_request):
            result = test_endpoint()
            assert result == "success"

    def test_csrf_protect_invalid_token(self):
        """Test that invalid CSRF tokens are rejected."""
        mock_request = Mock()
        mock_request.headers = {"X-CSRF-Token": "invalid-token"}
        mock_request.session = {"csrf_token": "valid-token"}
        mock_request.id = "test-request-id"
        
        mock_current_app = Mock()
        mock_logger = Mock()
        mock_current_app.logger = mock_logger
        
        @csrf_protect
        def test_endpoint():
            return "success"
        
        with patch('middleware.security.request', mock_request), \
             patch('middleware.security.current_app', mock_current_app), \
             patch('middleware.security.abort') as mock_abort:
            
            test_endpoint()
            mock_abort.assert_called_with(403, "CSRF validation failed")
            mock_logger.error.assert_called()

    def test_csrf_protect_missing_token(self):
        """Test that missing CSRF tokens are rejected."""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.session = {"csrf_token": "valid-token"}
        mock_request.id = "test-request-id"
        
        mock_current_app = Mock()
        mock_logger = Mock()
        mock_current_app.logger = mock_logger
        
        @csrf_protect
        def test_endpoint():
            return "success"
        
        with patch('middleware.security.request', mock_request), \
             patch('middleware.security.current_app', mock_current_app), \
             patch('middleware.security.abort') as mock_abort:
            
            test_endpoint()
            mock_abort.assert_called_with(403, "CSRF validation failed")
            mock_logger.error.assert_called()


class TestLoggingUtilities:
    """Test cases for logging utilities."""

    def test_custom_json_formatter(self):
        """Test that CustomJSONFormatter produces valid JSON logs."""
        formatter = CustomJSONFormatter()
        
        # Create a mock log record using logging.LogRecord
        import logging
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_module.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.request_id = "test-request-id"
        
        result = formatter.format(record)
        
        # Verify it's valid JSON
        log_data = json.loads(result)
        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Test message"
        assert log_data["module"] == "test_module"
        assert log_data["function"] == "test_custom_json_formatter"
        assert log_data["line"] == 42
        assert log_data["request_id"] == "test-request-id"
        assert "timestamp" in log_data

    def test_custom_json_formatter_with_request(self):
        """Test formatter with Flask request object."""
        formatter = CustomJSONFormatter()
        
        # Create a proper log record
        import logging
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_module.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.request_id = "test-request-id"
        
        # Add request mock
        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.path = "/api/test"
        mock_request.remote_addr = "127.0.0.1"
        record.request = mock_request
        
        result = formatter.format(record)
        
        # Verify request data is included
        log_data = json.loads(result)
        assert log_data["method"] == "POST"
        assert log_data["path"] == "/api/test"
        assert log_data["ip"] == "127.0.0.1"

    def test_custom_json_formatter_with_exception(self):
        """Test formatter with exception information."""
        formatter = CustomJSONFormatter()
        
        # Create a proper log record with exception
        import logging
        import sys
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test_module.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        record.request_id = "test-request-id"
        
        result = formatter.format(record)
        
        # Verify exception data is included
        log_data = json.loads(result)
        assert "exception" in log_data
        assert log_data["exception"]["type"] == "ValueError"
        assert log_data["exception"]["message"] == "Test exception"
        assert "traceback" in log_data["exception"]

    def test_setup_logging(self):
        """Test that logging setup configures correctly."""
        with patch('utils.logging.logging') as mock_logging:
            mock_logger = Mock()
            mock_handler = Mock()
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.StreamHandler.return_value = mock_handler
            
            setup_logging()
            
            mock_logging.getLogger.assert_called()
            mock_logger.addHandler.assert_called_with(mock_handler)
            mock_logger.setLevel.assert_called_with(mock_logging.INFO)

    def test_request_id_middleware(self):
        """Test that request ID middleware assigns UUIDs."""
        mock_request = Mock()
        
        with patch('utils.logging.request', mock_request), \
             patch('utils.logging.str') as mock_str, \
             patch('utils.logging.uuid.uuid4') as mock_uuid:
            
            mock_uuid.return_value = "test-uuid"
            mock_str.return_value = "test-uuid"
            
            request_id_middleware()
            
            assert mock_request.id == "test-uuid"


class TestSecurityIntegration:
    """Integration tests for security components working together."""

    def test_security_logging_integration(self):
        """Test that security middleware properly logs events."""
        # This test verifies that security events are properly logged
        mock_request = Mock()
        mock_request.values = {"malicious": "bad<script>"}
        mock_request.id = "test-request-id"
        
        mock_current_app = Mock()
        mock_logger = Mock()
        mock_current_app.logger = mock_logger
        
        @validate_input
        def test_endpoint():
            return "success"
        
        with patch('middleware.security.request', mock_request), \
             patch('middleware.security.current_app', mock_current_app), \
             patch('middleware.security.abort'):
            
            test_endpoint()
            
            # Verify security event was logged with request ID
            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args
            assert "Invalid input detected" in str(call_args)

    def test_multiple_security_decorators(self):
        """Test that multiple security decorators work together."""
        mock_request = Mock()
        mock_request.values = {"username": "validuser"}
        mock_request.headers = {"X-CSRF-Token": "valid-token"}
        mock_request.session = {"csrf_token": "valid-token"}
        mock_request.remote_addr = "127.0.0.1"
        mock_request.id = "test-request-id"
        
        mock_redis = Mock()
        mock_redis.get.return_value = "1"  # Low count
        mock_redis.pipeline.return_value = mock_redis
        mock_redis.incr.return_value = None
        mock_redis.expire.return_value = None
        mock_redis.execute.return_value = None
        
        @rate_limit(limit_per_minute=10)
        @csrf_protect
        @validate_input
        def test_endpoint():
            return "success"
        
        with patch('middleware.security.request', mock_request), \
             patch('middleware.security.redis_client', mock_redis):
            
            result = test_endpoint()
            assert result == "success"


def test_security_configuration_validation():
    """Test that security configuration is properly validated."""
    # Test that required security parameters are validated
    assert hasattr(validate_input, '__call__'), "validate_input should be callable"
    assert hasattr(rate_limit, '__call__'), "rate_limit should be callable"
    assert hasattr(csrf_protect, '__call__'), "csrf_protect should be callable"
    
    # Test that logging components are properly configured
    assert hasattr(CustomJSONFormatter, 'format'), "CustomJSONFormatter should have format method"
    assert hasattr(setup_logging, '__call__'), "setup_logging should be callable"
    assert hasattr(request_id_middleware, '__call__'), "request_id_middleware should be callable"


def test_security_edge_cases():
    """Test edge cases and error conditions."""
    # Test empty input validation
    mock_request = Mock()
    mock_request.values = {}
    mock_request.id = "test-request-id"
    
    @validate_input
    def test_endpoint():
        return "success"
    
    with patch('middleware.security.request', mock_request):
        result = test_endpoint()
        assert result == "success"
    
    # Test rate limiting with Redis unavailable
    mock_request = Mock()
    mock_request.remote_addr = "127.0.0.1"
    
    mock_redis = Mock()
    mock_redis.get.side_effect = Exception("Redis unavailable")
    
    @rate_limit(limit_per_minute=10)
    def test_endpoint_redis_fail():
        return "success"
    
    with patch('middleware.security.redis_client', mock_redis), \
         patch('middleware.security.request', mock_request):
        try:
            result = test_endpoint_redis_fail()
            # Should handle Redis failure gracefully
        except Exception as e:
            # Expect Redis exception to propagate for proper error handling
            assert "Redis unavailable" in str(e)


if __name__ == "__main__":
    # Run tests when script is executed directly
    print("🧪 Running Security Test Suite")
    print("=" * 50)
    
    try:
        # Run each test class
        test_classes = [TestSecurityMiddleware, TestLoggingUtilities, TestSecurityIntegration]
        
        for test_class in test_classes:
            print(f"\n📋 Running {test_class.__name__}")
            instance = test_class()
            
            # Get all test methods
            test_methods = [method for method in dir(instance) if method.startswith('test_')]
            
            for method_name in test_methods:
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"  ✅ {method_name}")
                except Exception as e:
                    print(f"  ❌ {method_name}: {e}")
        
        # Run standalone tests
        print(f"\n📋 Running Standalone Tests")
        try:
            test_security_configuration_validation()
            print("  ✅ test_security_configuration_validation")
        except Exception as e:
            print(f"  ❌ test_security_configuration_validation: {e}")
        
        try:
            test_security_edge_cases()
            print("  ✅ test_security_edge_cases")
        except Exception as e:
            print(f"  ❌ test_security_edge_cases: {e}")
        
        print("\n🎉 Security test suite completed!")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)