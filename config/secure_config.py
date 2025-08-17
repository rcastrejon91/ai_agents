import os
import secrets
from typing import Dict, Any
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._encryption_key = os.getenv('ENCRYPTION_KEY') or Fernet.generate_key()
        self._fernet = Fernet(self._encryption_key)
        
    def load_env(self):
        required_vars = [
            'JWT_SECRET',
            'ADMIN_PASSWORD',
            'DATABASE_URL',
            'API_KEYS'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                raise ValueError(f"Missing required environment variable: {var}")
            self._config[var] = self._encrypt_value(value)
            
    def get(self, key: str) -> str:
        encrypted_value = self._config.get(key)
        if not encrypted_value:
            raise KeyError(f"Configuration key not found: {key}")
        return self._decrypt_value(encrypted_value)
        
    def _encrypt_value(self, value: str) -> bytes:
        return self._fernet.encrypt(value.encode())
        
    def _decrypt_value(self, encrypted: bytes) -> str:
        return self._fernet.decrypt(encrypted).decode()