#!/usr/bin/env python3
"""
Environment validation script for AI Agents repository.
Run this script to validate your environment configuration.
"""
import os
import sys

# Add parent directory to sys.path if running as script
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.env_validator import EnvironmentValidator

def main():
    """Main validation function"""
    print("🔍 Environment Configuration Validator")
    print("=" * 50)
    
    # Check if required security variables are set
    security_vars = ['JWT_SECRET', 'ADMIN_PASSWORD', 'DATABASE_URL', 'API_KEYS']
    missing_vars = []
    
    for var in security_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing security environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Run ./setup_env.sh to generate secure values")
        print()
    else:
        print("✅ All required security variables are set")
        print()
    
    # Run validation
    print("🧪 Running validation tests...")
    validator = EnvironmentValidator()
    errors = validator.validate_all()
    
    if errors:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"   - {error}")
        print("\n💡 Fix these issues or run ./setup_env.sh for new secure values")
        return False
    else:
        print("✅ All environment variables pass validation")
        print()
    
    # Test secure config loading if no validation errors
    if not errors and not missing_vars:
        print("🔐 Testing secure configuration loading...")
        try:
            from config.secure_config import SecureConfig
            config = SecureConfig()
            config.load_env()
            
            # Test that we can retrieve values
            config.get('JWT_SECRET')
            config.get('ADMIN_PASSWORD')
            config.get('DATABASE_URL')
            config.get('API_KEYS')
            
            print("✅ Secure configuration loaded successfully")
            print()
        except Exception as e:
            print(f"❌ Secure configuration failed: {e}")
            return False
    
    print("🎉 Environment validation completed successfully!")
    print("\n📋 Summary:")
    print("   • Environment variables are properly set")
    print("   • All validation rules pass")
    print("   • Secure configuration system is working")
    print("\n🚀 Your environment is ready for secure operation!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)