# Security Configuration System

This directory contains a comprehensive security configuration system for the AI Agents repository, providing encrypted configuration management and environment validation.

## 🔐 Components

### 1. SecureConfig (`config/secure_config.py`)
Encrypts sensitive configuration data using Fernet encryption from the `cryptography` library.

**Features:**
- Automatic encryption of sensitive environment variables
- Secure storage in memory using Fernet encryption
- Key management with auto-generation
- Validation of required variables

**Usage:**
```python
from config.secure_config import SecureConfig

config = SecureConfig()
config.load_env()

# Access encrypted values
jwt_secret = config.get('JWT_SECRET')
admin_password = config.get('ADMIN_PASSWORD')
```

### 2. EnvironmentValidator (`utils/env_validator.py`)
Validates environment variables using regex patterns to ensure they meet security requirements.

**Validation Rules:**
- `JWT_SECRET`: Base64-like string, minimum 32 characters
- `DATABASE_URL`: Valid database connection string format
- `API_KEYS`: Alphanumeric keys separated by commas
- `ADMIN_PASSWORD`: Base64-like string, minimum 8 characters

**Usage:**
```python
from utils.env_validator import EnvironmentValidator

validator = EnvironmentValidator()
errors = validator.validate_all()

if errors:
    print("Validation errors:", errors)
```

### 3. Environment Setup Script (`setup_env.sh`)
Generates secure random values for environment variables.

**Features:**
- Uses OpenSSL for cryptographically secure random generation
- Creates `.env` file with proper permissions (600)
- Generates JWT secrets, encryption keys, and admin passwords

**Usage:**
```bash
./setup_env.sh
```

## 🚀 Quick Start

1. **Generate secure environment variables:**
   ```bash
   ./setup_env.sh
   ```

2. **Validate your environment:**
   ```bash
   python validate_env.py
   ```

3. **Use in your application:**
   ```python
   from config.secure_config import SecureConfig
   
   config = SecureConfig()
   config.load_env()
   secret = config.get('JWT_SECRET')
   ```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python -m pytest tests/test_secure_config.py tests/test_env_validator.py tests/test_security_integration.py -v
```

Run the demo script:
```bash
python demo_security.py
```

## 📝 Environment Variables

The system manages these security-critical environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET` | Secret for JWT token signing | `VGVzdFNlY3JldEtleUZvckpXVA==` |
| `ENCRYPTION_KEY` | Key for config encryption | `gwOTsLfhqYdFBxFO8qybsztnK/Q=` |
| `ADMIN_PASSWORD` | Admin interface password | `Q8SgQ2uvkBqOFzD95F/C3Q==` |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@host:5432/db` |
| `API_KEYS` | Comma-separated API keys | `key1,key2,key3` |

## 🔧 Integration Examples

### Flask Application
```python
# lyra_app/secure_config.py
from config.secure_config import SecureConfig

config = SecureConfig()
config.load_env()

app.config['SECRET_KEY'] = config.get('JWT_SECRET')
ADMIN_PASSWORD = config.get('ADMIN_PASSWORD')
```

### Environment Validation in CI/CD
```python
from utils.env_validator import EnvironmentValidator

validator = EnvironmentValidator()
errors = validator.validate_all()

if errors:
    print("Environment validation failed!")
    sys.exit(1)
```

## 🛡️ Security Features

- **Encryption at Rest**: All sensitive config values are encrypted in memory
- **Environment Validation**: Regex patterns ensure proper format and security
- **Secure Generation**: Uses OpenSSL for cryptographically secure random values
- **Proper Permissions**: Generated files have restrictive permissions (600)
- **Fallback Support**: Graceful degradation when secure config is unavailable

## 📊 Test Coverage

The system includes comprehensive tests covering:
- ✅ Encryption/decryption functionality
- ✅ Environment variable validation
- ✅ Error handling and edge cases
- ✅ Integration workflows
- ✅ Security pattern validation

## 🔍 Validation Patterns

The environment validator uses these regex patterns:

```python
JWT_SECRET: r"^[A-Za-z0-9+/=]{32,}$"           # Base64, 32+ chars
DATABASE_URL: r"^[A-Za-z]+:\/\/[A-Za-z0-9-_]+:[A-Za-z0-9-_]+@[A-Za-z0-9-_.]+:\d+\/[A-Za-z0-9-_]+$"
API_KEYS: r"^[A-Za-z0-9-_,]+$"                 # Alphanumeric with commas
ADMIN_PASSWORD: r"^[A-Za-z0-9+/=]{8,}$"        # Base64, 8+ chars
```

## 📚 Files Structure

```
├── config/
│   ├── __init__.py
│   └── secure_config.py          # Main secure config class
├── utils/
│   ├── __init__.py
│   └── env_validator.py          # Environment validation
├── tests/
│   ├── test_secure_config.py     # SecureConfig tests
│   ├── test_env_validator.py     # Validator tests
│   └── test_security_integration.py # Integration tests
├── lyra_app/
│   └── secure_config.py          # Integration example
├── setup_env.sh                  # Environment setup script
├── validate_env.py               # Validation script
└── demo_security.py              # Demo script
```

This security system provides a robust foundation for managing sensitive configuration data while maintaining ease of use and development flexibility.