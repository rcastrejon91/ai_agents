import os
import pytest
from unittest.mock import patch
from cryptography.fernet import Fernet

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.secure_config import SecureConfig

class TestSecureConfig:
    
    def test_init_with_env_key(self):
        """Test initialization with environment encryption key"""
        test_key = Fernet.generate_key()
        with patch.dict(os.environ, {'ENCRYPTION_KEY': test_key.decode()}):
            config = SecureConfig()
            assert config._encryption_key == test_key.decode()
    
    def test_init_without_env_key(self):
        """Test initialization without environment encryption key generates new one"""
        with patch.dict(os.environ, {}, clear=True):
            config = SecureConfig()
            assert config._encryption_key is not None
            # Should be able to create a Fernet instance with it
            Fernet(config._encryption_key)
    
    def test_load_env_success(self):
        """Test successful loading of required environment variables"""
        test_env = {
            'JWT_SECRET': 'test.jwt.secret',
            'ADMIN_PASSWORD': 'testpass123',
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/db',
            'API_KEYS': 'key1,key2,key3'
        }
        
        with patch.dict(os.environ, test_env):
            config = SecureConfig()
            config.load_env()
            
            # All keys should be encrypted and stored
            assert len(config._config) == 4
            for key in test_env.keys():
                assert key in config._config
                # Values should be encrypted (bytes)
                assert isinstance(config._config[key], bytes)
    
    def test_load_env_missing_required_var(self):
        """Test that missing required environment variable raises ValueError"""
        incomplete_env = {
            'JWT_SECRET': 'test.jwt.secret',
            'ADMIN_PASSWORD': 'testpass123',
            # Missing DATABASE_URL and API_KEYS
        }
        
        with patch.dict(os.environ, incomplete_env, clear=True):
            config = SecureConfig()
            with pytest.raises(ValueError, match="Missing required environment variable: DATABASE_URL"):
                config.load_env()
    
    def test_get_existing_key(self):
        """Test getting an existing configuration key"""
        test_env = {
            'JWT_SECRET': 'test.jwt.secret',
            'ADMIN_PASSWORD': 'testpass123',
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/db',
            'API_KEYS': 'key1,key2,key3'
        }
        
        with patch.dict(os.environ, test_env):
            config = SecureConfig()
            config.load_env()
            
            # Should decrypt and return original value
            assert config.get('JWT_SECRET') == 'test.jwt.secret'
            assert config.get('ADMIN_PASSWORD') == 'testpass123'
    
    def test_get_missing_key(self):
        """Test that getting a missing key raises KeyError"""
        config = SecureConfig()
        with pytest.raises(KeyError, match="Configuration key not found: MISSING_KEY"):
            config.get('MISSING_KEY')
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption and decryption work correctly"""
        config = SecureConfig()
        test_value = "test_secret_value"
        
        encrypted = config._encrypt_value(test_value)
        decrypted = config._decrypt_value(encrypted)
        
        assert isinstance(encrypted, bytes)
        assert decrypted == test_value