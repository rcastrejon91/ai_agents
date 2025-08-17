#!/usr/bin/env python3
"""
Demo script showing the secure configuration system in action
"""
import os
import sys
import tempfile

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def demo_secure_config():
    """Demonstrate the secure configuration system"""
    print("=== Secure Configuration Demo ===\n")
    
    # Step 1: Generate secure environment
    print("1. Setting up secure environment variables...")
    test_env = {
        'JWT_SECRET': 'VGVzdFNlY3JldEtleUZvckpXVEF1dGhlbnRpY2F0aW9u',
        'DATABASE_URL': 'postgresql://demo:pass@localhost:5432/demodb',
        'API_KEYS': 'demo-key1,demo-key2,demo-key3',
        'ADMIN_PASSWORD': 'SecureDemo123',
        'ENCRYPTION_KEY': 'gwOTsLfhqYdFBxFO8qybsztnK/QKBAMcE2sVp419PWQ='
    }
    
    # Set environment variables for this demo
    for key, value in test_env.items():
        os.environ[key] = value
    
    print("✓ Environment variables set\n")
    
    # Step 2: Validate environment
    print("2. Validating environment variables...")
    from utils.env_validator import EnvironmentValidator
    
    validator = EnvironmentValidator()
    errors = validator.validate_all()
    
    if errors:
        print("✗ Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ All environment variables are valid\n")
    
    # Step 3: Load secure configuration
    print("3. Loading secure configuration...")
    from config.secure_config import SecureConfig
    
    try:
        config = SecureConfig()
        config.load_env()
        print("✓ Configuration loaded and encrypted\n")
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False
    
    # Step 4: Demonstrate secure access
    print("4. Accessing encrypted configuration...")
    try:
        jwt_secret = config.get('JWT_SECRET')
        db_url = config.get('DATABASE_URL')
        api_keys = config.get('API_KEYS')
        admin_password = config.get('ADMIN_PASSWORD')
        
        print(f"✓ JWT Secret (first 10 chars): {jwt_secret[:10]}...")
        print(f"✓ Database URL: {db_url}")
        print(f"✓ API Keys: {api_keys}")
        print(f"✓ Admin Password (length): {len(admin_password)} chars")
        print()
        
    except Exception as e:
        print(f"✗ Configuration access failed: {e}")
        return False
    
    # Step 5: Show lyra_app integration
    print("5. Testing lyra_app integration...")
    try:
        from lyra_app.secure_config import SECRET_KEY, ADMIN_PASSWORD as SECURE_ADMIN_PASSWORD
        print(f"✓ SECRET_KEY loaded (first 10 chars): {SECRET_KEY[:10]}...")
        print(f"✓ ADMIN_PASSWORD loaded (length): {len(SECURE_ADMIN_PASSWORD)} chars")
        print()
    except Exception as e:
        print(f"✗ lyra_app integration failed: {e}")
        return False
    
    print("=== Demo completed successfully! ===")
    return True

def demo_invalid_environment():
    """Demonstrate validation with invalid environment"""
    print("\n=== Invalid Environment Demo ===\n")
    
    # Clear environment and set invalid values
    for key in ['JWT_SECRET', 'DATABASE_URL', 'API_KEYS', 'ADMIN_PASSWORD']:
        if key in os.environ:
            del os.environ[key]
    
    invalid_env = {
        'JWT_SECRET': 'too-short',
        'DATABASE_URL': 'not-a-url',
        'API_KEYS': 'invalid chars!',
        'ADMIN_PASSWORD': 'weak'
    }
    
    for key, value in invalid_env.items():
        os.environ[key] = value
    
    print("1. Setting invalid environment variables...")
    from utils.env_validator import EnvironmentValidator
    
    validator = EnvironmentValidator()
    errors = validator.validate_all()
    
    if errors:
        print("✓ Validation correctly identified errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✗ Validation should have found errors but didn't")
    
    print("\n=== Invalid Environment Demo completed ===")

if __name__ == "__main__":
    print("Starting Secure Configuration System Demo\n")
    
    # Run the main demo
    success = demo_secure_config()
    
    # Run the invalid environment demo
    demo_invalid_environment()
    
    if success:
        print(f"\n🎉 All demos completed successfully!")
        print("To use this system:")
        print("1. Run ./setup_env.sh to generate secure environment variables")
        print("2. Use config.secure_config.SecureConfig in your applications")
        print("3. Validate environment with utils.env_validator.EnvironmentValidator")
        sys.exit(0)
    else:
        print("\n❌ Demo failed - check the output above")
        sys.exit(1)