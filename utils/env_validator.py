import os
from dataclasses import dataclass
from typing import List, Optional
import re

@dataclass
class EnvValidation:
    name: str
    pattern: Optional[str] = None
    required: bool = True
    
    def validate(self, value: str) -> bool:
        if not value and self.required:
            return False
        if self.pattern and not re.match(self.pattern, value):
            return False
        return True

class EnvironmentValidator:
    def __init__(self):
        self.validations = [
            EnvValidation("JWT_SECRET", r"^[A-Za-z0-9+/=]{32,}$"),  # Base64-like string, at least 32 chars
            EnvValidation("DATABASE_URL", r"^[A-Za-z]+:\/\/[A-Za-z0-9-_]+:[A-Za-z0-9-_]+@[A-Za-z0-9-_.]+:\d+\/[A-Za-z0-9-_]+$"),
            EnvValidation("API_KEYS", r"^[A-Za-z0-9-_,]+$"),
            EnvValidation("ADMIN_PASSWORD", r"^[A-Za-z0-9+/=]{8,}$")  # Base64-like string, at least 8 chars (for generated passwords)
        ]
    
    def validate_all(self) -> List[str]:
        errors = []
        for validation in self.validations:
            value = os.getenv(validation.name)
            if not validation.validate(value):
                errors.append(f"Invalid environment variable: {validation.name}")
        return errors