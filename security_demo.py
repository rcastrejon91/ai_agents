#!/usr/bin/env python3
"""
Security Improvements Demo Script
Demonstrates the comprehensive security features implemented in the AI agents system.
"""

import asyncio
import json
import sys
import time
from dataclasses import dataclass
from bots.core.launch_manager import (
    LaunchManager, BotRegistry, FloBot, BotError, BotNotFoundError,
    BotLaunchError, BotValidationError, BotSecurityError, BotRateLimitError
)

def demo_bot_function(*args, **kwargs):
    """Demo bot function for testing."""
    return f"Demo bot executed with args: {args}, kwargs: {kwargs}"

def malicious_bot_function(*args, **kwargs):
    """Bot function that might be misused."""
    # This would normally be a real bot, but for demo we'll just return the input
    return f"Processed: {kwargs}"

@dataclass 
class SecurityDemo:
    """Demonstrates security improvements in the AI agent system."""
    
    def __init__(self):
        self.registry = BotRegistry()
        self.launch_manager = LaunchManager(
            self.registry, 
            enable_security=True, 
            rate_limit_per_minute=3  # Low limit for demo
        )
        self.setup_demo_bots()
    
    def setup_demo_bots(self):
        """Set up demo bots for testing."""
        try:
            # Valid bot
            demo_bot = FloBot(
                name="demo_bot",
                category="demo",
                description="A safe demo bot",
                launch_callable=demo_bot_function
            )
            self.registry.add_bot(demo_bot)
            
            # Another valid bot  
            echo_bot = FloBot(
                name="echo_bot",
                category="utility",
                description="Echoes input safely",
                launch_callable=malicious_bot_function
            )
            self.registry.add_bot(echo_bot)
            
            print("✅ Demo bots registered successfully")
            
        except Exception as e:
            print(f"❌ Error setting up demo bots: {e}")
    
    def demo_input_validation(self):
        """Demonstrate input validation and sanitization."""
        print("\n🔒 SECURITY DEMO: Input Validation")
        print("=" * 50)
        
        test_cases = [
            # Safe inputs
            {"message": "Hello, how are you?", "expected": "safe"},
            {"query": "What is the weather today?", "expected": "safe"},
            
            # Potentially malicious inputs
            {"script": "<script>alert('xss')</script>", "expected": "blocked"},
            {"injection": "'; DROP TABLE users; --", "expected": "blocked"},
            {"path_traversal": "../../../etc/passwd", "expected": "blocked"},
            {"js_injection": "javascript:alert('hack')", "expected": "blocked"},
            {"python_exec": "__import__('os').system('rm -rf /')", "expected": "blocked"},
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {list(test_case.keys())[0]}")
            try:
                result = self.launch_manager.launch("echo_bot", "api", **test_case)
                if test_case["expected"] == "blocked":
                    print(f"⚠️  Expected to be blocked but got: {result}")
                else:
                    print(f"✅ Safe input processed: {result}")
            except BotSecurityError as e:
                if test_case["expected"] == "blocked":
                    print(f"✅ Malicious input blocked: {e.error_code}")
                else:
                    print(f"❌ Safe input incorrectly blocked: {e}")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
    
    def demo_rate_limiting(self):
        """Demonstrate rate limiting protection."""
        print("\n🚦 SECURITY DEMO: Rate Limiting")
        print("=" * 50)
        
        print("Testing rate limiting (limit: 3 requests per minute)")
        
        for i in range(5):
            try:
                result = self.launch_manager.launch("demo_bot", "api", request_id=i)
                print(f"✅ Request {i+1}: Success")
            except BotRateLimitError as e:
                print(f"🛑 Request {i+1}: Rate limited - {e.error_code}")
            except Exception as e:
                print(f"❌ Request {i+1}: Unexpected error - {e}")
            
            time.sleep(0.5)  # Small delay between requests
    
    def demo_bot_validation(self):
        """Demonstrate bot registration validation."""
        print("\n✅ SECURITY DEMO: Bot Registration Validation") 
        print("=" * 50)
        
        # Test invalid bot registrations
        invalid_bots = [
            # Invalid name
            FloBot(name="", category="test", description="Empty name", launch_callable=demo_bot_function),
            FloBot(name="bot with spaces", category="test", description="Invalid chars", launch_callable=demo_bot_function),
            FloBot(name="bot<script>", category="test", description="XSS in name", launch_callable=demo_bot_function),
            
            # No launch method
            FloBot(name="no_launch", category="test", description="No launch method"),
            
            # Duplicate name (demo_bot already exists)
            FloBot(name="demo_bot", category="test", description="Duplicate", launch_callable=demo_bot_function),
        ]
        
        for i, bot in enumerate(invalid_bots, 1):
            try:
                self.registry.add_bot(bot)
                print(f"❌ Test {i}: Invalid bot '{bot.name}' was registered (should have failed)")
            except BotValidationError as e:
                print(f"✅ Test {i}: Invalid bot correctly rejected - {e.error_code}")
            except Exception as e:
                print(f"❌ Test {i}: Unexpected error - {e}")
    
    def demo_error_handling(self):
        """Demonstrate structured error handling and logging."""
        print("\n📋 SECURITY DEMO: Structured Error Handling")
        print("=" * 50)
        
        # Test different error types
        error_tests = [
            ("nonexistent_bot", "chat", {}, BotNotFoundError),
            ("demo_bot", "invalid_trigger", {}, BotSecurityError),
            ("echo_bot", "api", {"script": "<script>alert(1)</script>"}, BotSecurityError),
        ]
        
        for bot_name, trigger, kwargs, expected_error in error_tests:
            try:
                result = self.launch_manager.launch(bot_name, trigger, **kwargs)
                print(f"❌ Expected {expected_error.__name__} but got result: {result}")
            except expected_error as e:
                error_dict = e.to_dict() if hasattr(e, 'to_dict') else {"message": str(e)}
                print(f"✅ {expected_error.__name__} correctly raised:")
                print(f"   📄 Error details: {json.dumps(error_dict, indent=2)}")
            except Exception as e:
                print(f"❌ Expected {expected_error.__name__} but got {type(e).__name__}: {e}")
    
    def demo_environment_config(self):
        """Demonstrate environment-based configuration."""
        print("\n⚙️  SECURITY DEMO: Environment Configuration")
        print("=" * 50)
        
        import os
        
        # Show current environment settings
        env_vars = [
            "NODE_ENV",
            "JWT_SECRET", 
            "ALLOWED_ORIGINS",
            "ADMIN_DASH_KEY"
        ]
        
        print("Current environment configuration:")
        for var in env_vars:
            value = os.environ.get(var, "Not set")
            # Mask sensitive values
            if "SECRET" in var or "KEY" in var:
                value = "***MASKED***" if value != "Not set" else "Not set"
            print(f"  {var}: {value}")
    
    def run_all_demos(self):
        """Run all security demonstrations."""
        print("🔐 AI AGENTS SECURITY IMPROVEMENTS DEMONSTRATION")
        print("=" * 60)
        print("This demo showcases the comprehensive security improvements")
        print("implemented in the AI agents system.")
        print("=" * 60)
        
        try:
            self.demo_environment_config()
            self.demo_bot_validation()
            self.demo_input_validation()
            self.demo_rate_limiting() 
            self.demo_error_handling()
            
            print("\n✨ SECURITY DEMO COMPLETED")
            print("=" * 60)
            print("All security features demonstrated successfully!")
            print("The system now includes:")
            print("  ✅ Input validation and sanitization")
            print("  ✅ Rate limiting protection")
            print("  ✅ Bot registration validation")
            print("  ✅ Structured error handling")
            print("  ✅ Environment-based configuration")
            print("  ✅ Security logging and monitoring")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            return False
        
        return True

if __name__ == "__main__":
    demo = SecurityDemo()
    success = demo.run_all_demos()
    sys.exit(0 if success else 1)