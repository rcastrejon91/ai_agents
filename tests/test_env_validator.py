import os
import pytest
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.env_validator import EnvValidation, EnvironmentValidator

class TestEnvValidation:
    
    def test_validate_required_present(self):
        """Test validation passes when required value is present"""
        validation = EnvValidation("TEST_VAR", required=True)
        assert validation.validate("some_value") is True
    
    def test_validate_required_missing(self):
        """Test validation fails when required value is missing"""
        validation = EnvValidation("TEST_VAR", required=True)
        assert validation.validate("") is False
        assert validation.validate(None) is False
    
    def test_validate_optional_missing(self):
        """Test validation passes when optional value is missing"""
        validation = EnvValidation("TEST_VAR", required=False)
        assert validation.validate("") is True
        assert validation.validate(None) is True
    
    def test_validate_pattern_match(self):
        """Test validation passes when pattern matches"""
        validation = EnvValidation("TEST_VAR", pattern=r"^[A-Za-z]+$")
        assert validation.validate("HelloWorld") is True
    
    def test_validate_pattern_no_match(self):
        """Test validation fails when pattern doesn't match"""
        validation = EnvValidation("TEST_VAR", pattern=r"^[A-Za-z]+$")
        assert validation.validate("Hello123") is False
    
    def test_validate_pattern_and_required(self):
        """Test validation with both pattern and required constraints"""
        validation = EnvValidation("TEST_VAR", pattern=r"^[A-Za-z]+$", required=True)
        assert validation.validate("HelloWorld") is True
        assert validation.validate("Hello123") is False
        assert validation.validate("") is False

class TestEnvironmentValidator:
    
    def test_jwt_secret_pattern(self):
        """Test JWT secret pattern validation"""
        validator = EnvironmentValidator()
        jwt_validation = next(v for v in validator.validations if v.name == "JWT_SECRET")
        
        # Valid JWT secrets (base64-like, at least 32 chars)
        assert jwt_validation.validate("abcdefghijklmnopqrstuvwxyzABCDEF") is True
        assert jwt_validation.validate("VGVzdFNlY3JldEtleUZvckpXVEF1dGhlbnRpY2F0aW9u") is True
        assert jwt_validation.validate("a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9") is True
        
        # Invalid formats
        assert jwt_validation.validate("just-a-string") is False  # too short
        assert jwt_validation.validate("short") is False  # too short
        assert jwt_validation.validate("has@invalid#chars") is False  # invalid chars
    
    def test_database_url_pattern(self):
        """Test database URL pattern validation"""
        validator = EnvironmentValidator()
        db_validation = next(v for v in validator.validations if v.name == "DATABASE_URL")
        
        # Valid database URLs
        assert db_validation.validate("postgresql://user:pass@localhost:5432/dbname") is True
        assert db_validation.validate("mysql://admin:secret@db.example.com:3306/mydb") is True
        
        # Invalid formats
        assert db_validation.validate("not-a-url") is False
        assert db_validation.validate("http://example.com") is False
        assert db_validation.validate("postgresql://user@localhost") is False  # missing port/db
    
    def test_api_keys_pattern(self):
        """Test API keys pattern validation"""
        validator = EnvironmentValidator()
        api_validation = next(v for v in validator.validations if v.name == "API_KEYS")
        
        # Valid API key formats
        assert api_validation.validate("key1,key2,key3") is True
        assert api_validation.validate("single-key") is True
        assert api_validation.validate("key_with_underscore") is True
        
        # Invalid formats
        assert api_validation.validate("key with spaces") is False
        assert api_validation.validate("key@invalid") is False
    
    def test_admin_password_pattern(self):
        """Test admin password pattern validation"""
        validator = EnvironmentValidator()
        pwd_validation = next(v for v in validator.validations if v.name == "ADMIN_PASSWORD")
        
        # Valid passwords (at least 8 chars, at least 1 letter and 1 digit)
        assert pwd_validation.validate("password123") is True
        assert pwd_validation.validate("MyPass99") is True
        assert pwd_validation.validate("a1b2c3d4") is True
        
        # Invalid passwords
        assert pwd_validation.validate("short1") is False  # too short
        assert pwd_validation.validate("nouppercase123") is True  # still valid (has letter+digit)
        assert pwd_validation.validate("NoDigitsHere") is False  # no digits
        assert pwd_validation.validate("12345678") is False  # no letters
    
    def test_validate_all_success(self):
        """Test validate_all with all valid environment variables"""
        test_env = {
            'JWT_SECRET': 'VGVzdFNlY3JldEtleUZvckpXVEF1dGhlbnRpY2F0aW9u',  # Valid base64-like string
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/dbname',
            'API_KEYS': 'key1,key2,key3',
            'ADMIN_PASSWORD': 'SecurePass123'
        }
        
        with patch.dict(os.environ, test_env):
            validator = EnvironmentValidator()
            errors = validator.validate_all()
            assert errors == []
    
    def test_validate_all_with_errors(self):
        """Test validate_all with invalid environment variables"""
        test_env = {
            'JWT_SECRET': 'invalid-jwt',  # doesn't match pattern
            'DATABASE_URL': 'not-a-url',  # doesn't match pattern
            'API_KEYS': 'key with spaces',  # doesn't match pattern
            'ADMIN_PASSWORD': 'short'  # too short and no digits
        }
        
        with patch.dict(os.environ, test_env):
            validator = EnvironmentValidator()
            errors = validator.validate_all()
            
            assert len(errors) == 4
            assert "Invalid environment variable: JWT_SECRET" in errors
            assert "Invalid environment variable: DATABASE_URL" in errors
            assert "Invalid environment variable: API_KEYS" in errors
            assert "Invalid environment variable: ADMIN_PASSWORD" in errors
    
    def test_validate_all_missing_vars(self):
        """Test validate_all with missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            validator = EnvironmentValidator()
            errors = validator.validate_all()
            
            # Should have errors for all required variables
            assert len(errors) == 4
            for error in errors:
                assert "Invalid environment variable:" in error