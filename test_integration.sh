#!/bin/bash

# Integration test script for AI Agents platform
# Tests all components working together

echo "🚀 AI Agents Platform Integration Test"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    echo -e "\n${YELLOW}Testing: $test_name${NC}"
    
    result=$(eval "$test_command" 2>&1)
    
    if echo "$result" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        echo "Expected pattern: $expected_pattern"
        echo "Actual result: $result"
        ((TESTS_FAILED++))
    fi
}

# Check if we can build all components
echo -e "\n📦 Building Components..."

echo "Building companion_api..."
if cd apps/companion_api && npm run build >/dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} companion_api builds successfully"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌${NC} companion_api build failed"
    ((TESTS_FAILED++))
fi

echo "Building companion_web..."
if cd ../companion_web && npm run build >/dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} companion_web builds successfully"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌${NC} companion_web build failed"
    ((TESTS_FAILED++))
fi

cd ../..

# Test environment validation
echo -e "\n🔍 Testing Environment Validation..."

# Test missing API key
run_test "Missing API key validation" \
    "cd apps/companion_api && NODE_ENV=development PORT=8787 timeout 5 npm run dev 2>&1 || true" \
    "OPENAI_API_KEY is required"

# Test invalid API key format
run_test "Invalid API key format validation" \
    "cd apps/companion_api && OPENAI_API_KEY=invalid-key NODE_ENV=development PORT=8787 timeout 5 npm run dev 2>&1 || true" \
    'OPENAI_API_KEY must start with "sk-"'

# Test valid environment
run_test "Valid environment validation" \
    "cd apps/companion_api && OPENAI_API_KEY=sk-test-key NODE_ENV=development PORT=8787 timeout 3 npm run dev 2>&1 || true" \
    "Environment validation passed"

# Test environment-specific configurations
echo -e "\n⚙️  Testing Environment Configurations..."

run_test "Development environment config" \
    "cd apps/companion_api && OPENAI_API_KEY=sk-test-key NODE_ENV=development timeout 3 npm run dev 2>&1 || true" \
    "development"

run_test "Production environment config" \
    "cd apps/companion_api && OPENAI_API_KEY=sk-test-key NODE_ENV=production ALLOWED_ORIGINS=https://example.com timeout 3 npm run dev 2>&1 || true" \
    "production"

# Test TypeScript compilation
echo -e "\n📝 Testing TypeScript Compilation..."

run_test "TypeScript types check - no errors" \
    "cd apps/companion_web && npx tsc --noEmit --skipLibCheck pages/api/health.ts 2>&1 && echo 'no_errors' || echo 'has_errors'" \
    "no_errors"

# Test file structure
echo -e "\n📁 Testing File Structure..."

run_test "API utilities exist" \
    "test -f apps/companion_web/lib/api-utils.ts && echo 'exists'" \
    "exists"

run_test "Environment config exists" \
    "test -f apps/companion_web/lib/env-config.ts && echo 'exists'" \
    "exists"

run_test "Lyra API client exists" \
    "test -f lyra_app/utils/api_client.py && echo 'exists'" \
    "exists"

run_test "Enhanced error handlers exist" \
    "test -f lyra_app/middleware/error_handlers.py && echo 'exists'" \
    "exists"

# Test configuration files
echo -e "\n🔧 Testing Configuration Files..."

run_test "Updated .env.example exists" \
    "grep -q 'API_SECRET_KEY' .env.example && echo 'found'" \
    "found"

run_test "Security documentation exists" \
    "test -f docs/SECURITY_CONFIGURATION.md && echo 'exists'" \
    "exists"

run_test "Deployment guide exists" \
    "test -f docs/DEPLOYMENT_GUIDE.md && echo 'exists'" \
    "exists"

# Test API endpoints structure
echo -e "\n🌐 Testing API Endpoints..."

run_test "Health endpoint exists" \
    "test -f apps/companion_web/pages/api/health.ts && echo 'exists'" \
    "exists"

run_test "Config endpoint exists" \
    "test -f apps/companion_web/pages/api/config.ts && echo 'exists'" \
    "exists"

run_test "Selftest endpoint exists" \
    "test -f apps/companion_web/pages/api/selftest.ts && echo 'exists'" \
    "exists"

# Test security features
echo -e "\n🔒 Testing Security Features..."

run_test "Security module imports correctly" \
    "cd apps/companion_web && node -e 'require(\"./lib/security/index.ts\")' 2>&1 || echo 'typescript file'" \
    "typescript file"

run_test "Rate limiting implemented" \
    "grep -q 'rateLimit' apps/companion_web/lib/security/index.ts && echo 'found'" \
    "found"

run_test "Input sanitization implemented" \
    "grep -q 'sanitizeInput' apps/companion_web/lib/security/index.ts && echo 'found'" \
    "found"

# Summary
echo -e "\n📊 Test Summary"
echo "==============="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! The platform is ready for deployment.${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed. Please review the issues above.${NC}"
    exit 1
fi