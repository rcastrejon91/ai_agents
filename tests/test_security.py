"""
Basic security test suite focusing on core functionality.
"""

import json
import re
import unittest
from unittest.mock import MagicMock, patch


class TestInputValidationLogic(unittest.TestCase):
    """Test the core input validation logic."""

    def test_valid_input_patterns(self):
        """Test that valid input passes regex validation."""
        # Pattern from middleware/security.py
        pattern = r"^[\w\-\s\.@]+$"
        
        valid_inputs = [
            "john",
            "test@example.com", 
            "user.name@domain.com",
            "valid-name",
            "text with spaces",
            "123",
            "user_name"
        ]
        
        for input_val in valid_inputs:
            with self.subTest(input_val=input_val):
                self.assertTrue(re.match(pattern, input_val), f"'{input_val}' should be valid")

    def test_invalid_input_patterns(self):
        """Test that invalid input fails regex validation."""
        pattern = r"^[\w\-\s\.@]+$"
        
        invalid_inputs = [
            "<script>",
            "john<script>",
            "test'injection",
            'test"injection',
            "test;drop table",
            "test&lt;script&gt;",
            "test%3Cscript%3E"
        ]
        
        for input_val in invalid_inputs:
            with self.subTest(input_val=input_val):
                self.assertFalse(re.match(pattern, input_val), f"'{input_val}' should be invalid")


class TestLoggingModule(unittest.TestCase):
    """Test logging functionality."""

    def test_custom_json_formatter(self):
        """Test custom JSON formatter."""
        import logging
        from utils.logging import CustomJSONFormatter
        
        formatter = CustomJSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add custom attributes
        record.request_id = "test-request-id"
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertIn("timestamp", log_data)
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["request_id"], "test-request-id")
        self.assertEqual(log_data["line"], 42)

    def test_custom_json_formatter_with_exception(self):
        """Test custom JSON formatter with exception."""
        import logging
        from utils.logging import CustomJSONFormatter
        
        formatter = CustomJSONFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
            
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="/test/path.py",
                lineno=42,
                msg="Error occurred",
                args=(),
                exc_info=exc_info
            )
            
            formatted = formatter.format(record)
            log_data = json.loads(formatted)
            
            self.assertIn("exception", log_data)
            self.assertEqual(log_data["exception"]["type"], "ValueError")
            self.assertEqual(log_data["exception"]["message"], "Test exception")
            self.assertIn("traceback", log_data["exception"])

    @patch('utils.logging.logging')
    def test_setup_logging(self, mock_logging):
        """Test logging setup."""
        from utils.logging import setup_logging
        
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger
        mock_handler = MagicMock()
        mock_logging.StreamHandler.return_value = mock_handler
        
        setup_logging()
        
        # Verify logger was configured
        mock_logging.getLogger.assert_called_once()
        mock_logger.addHandler.assert_called_once_with(mock_handler)
        mock_logger.setLevel.assert_called_once_with(mock_logging.INFO)


class TestSecurityImports(unittest.TestCase):
    """Test that security modules can be imported and have expected functions."""

    def test_security_modules_importable(self):
        """Test that all security modules can be imported."""
        try:
            import middleware.security
            import utils.logging
            self.assertTrue(True, "All modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")

    def test_security_functions_exist(self):
        """Test that all expected security functions exist."""
        import middleware.security
        import utils.logging
        
        # Check middleware functions
        self.assertTrue(hasattr(middleware.security, 'validate_input'))
        self.assertTrue(hasattr(middleware.security, 'rate_limit'))
        self.assertTrue(hasattr(middleware.security, 'csrf_protect'))
        
        # Check logging functions
        self.assertTrue(hasattr(utils.logging, 'CustomJSONFormatter'))
        self.assertTrue(hasattr(utils.logging, 'setup_logging'))
        self.assertTrue(hasattr(utils.logging, 'request_id_middleware'))

    def test_redis_client_configured(self):
        """Test that Redis client is configured."""
        import middleware.security
        self.assertTrue(hasattr(middleware.security, 'redis_client'))


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()