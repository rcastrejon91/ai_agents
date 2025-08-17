import os
import sys

# Add parent directory to sys.path to import our security modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.secure_config import SecureConfig
from utils.env_validator import EnvironmentValidator

# Validate environment variables on import
validator = EnvironmentValidator()
env_errors = validator.validate_all()

# If there are validation errors, print warnings but don't fail completely
# This allows for graceful degradation during development
if env_errors:
    print("Warning: Environment validation errors found:")
    for error in env_errors:
        print(f"  - {error}")
    print("Consider running setup_env.sh to generate secure values")

# Initialize secure config if possible
secure_config = None
try:
    secure_config = SecureConfig()
    secure_config.load_env()
    print("Secure configuration loaded successfully")
except Exception as e:
    print(f"Warning: Could not load secure configuration: {e}")
    print("Falling back to basic configuration")

# Function to get configuration value with fallback
def get_config(key: str, fallback: str = "") -> str:
    """Get configuration value from secure config with fallback to environment"""
    if secure_config:
        try:
            return secure_config.get(key)
        except KeyError:
            pass
    return os.getenv(key, fallback)

# Configuration values with secure fallbacks
SECRET_KEY = get_config("JWT_SECRET", os.getenv("SECRET_KEY", "dev-key"))
ADMIN_PASSWORD = get_config("ADMIN_PASSWORD", os.getenv("ADMIN_PASSWORD", "admin"))
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASS = os.getenv("GMAIL_PASS", "")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "")
OWNER_NAME = os.getenv("OWNER_NAME", "")

# Additional secure configuration
DATABASE_URL = get_config("DATABASE_URL", os.getenv("DATABASE_URL", ""))
API_KEYS = get_config("API_KEYS", os.getenv("API_KEYS", ""))