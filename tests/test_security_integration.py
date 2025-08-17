import os
import pytest
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.secure_config import SecureConfig
from utils.env_validator import EnvironmentValidator

class TestSecurityIntegration:
    
    def test_full_security_workflow(self):
        """Test the complete security workflow: validation -> encryption -> decryption"""
        # Valid environment setup
        test_env = {
            'JWT_SECRET': 'VGVzdFNlY3JldEtleUZvckpXVEF1dGhlbnRpY2F0aW9u',
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/dbname',
            'API_KEYS': 'key1,key2,key3',
            'ADMIN_PASSWORD': 'SecurePass123',
            'ENCRYPTION_KEY': 'gwOTsLfhqYdFBxFO8qybsztnK/QKBAMcE2sVp419PWQ='
        }
        
        with patch.dict(os.environ, test_env):
            # Step 1: Validate environment
            validator = EnvironmentValidator()
            errors = validator.validate_all()
            assert errors == [], f"Environment validation failed: {errors}"
            
            # Step 2: Load and encrypt configuration
            config = SecureConfig()
            config.load_env()
            
            # Step 3: Verify all values can be retrieved and decrypted
            assert config.get('JWT_SECRET') == test_env['JWT_SECRET']
            assert config.get('DATABASE_URL') == test_env['DATABASE_URL']
            assert config.get('API_KEYS') == test_env['API_KEYS']
            assert config.get('ADMIN_PASSWORD') == test_env['ADMIN_PASSWORD']
    
    def test_invalid_environment_fails_validation(self):
        """Test that invalid environment variables are caught by validation"""
        invalid_env = {
            'JWT_SECRET': 'too-short',  # Too short
            'DATABASE_URL': 'not-a-url',  # Invalid format
            'API_KEYS': 'key with spaces',  # Invalid characters
            'ADMIN_PASSWORD': 'weak'  # Too weak
        }
        
        with patch.dict(os.environ, invalid_env, clear=True):
            validator = EnvironmentValidator()
            errors = validator.validate_all()
            
            # Should have errors for all variables
            assert len(errors) == 4
            assert all("Invalid environment variable" in error for error in errors)
    
    def test_secure_config_without_validation_protection(self):
        """Test that SecureConfig itself fails gracefully with invalid env"""
        invalid_env = {
            'JWT_SECRET': 'valid-secret-that-passes-encryption-test',
            'ADMIN_PASSWORD': 'validpass123',
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/db',
            # Missing API_KEYS - should raise ValueError
        }
        
        with patch.dict(os.environ, invalid_env, clear=True):
            config = SecureConfig()
            with pytest.raises(ValueError, match="Missing required environment variable: API_KEYS"):
                config.load_env()