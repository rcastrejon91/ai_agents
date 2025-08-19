# Lyra AI Agents System - Copilot Instructions

**ALWAYS follow these instructions first and only search for additional context if information here is incomplete or incorrect.**

## System Overview

Lyra is a multi-agent AI system powered by OpenAI + Tavily search that routes user requests to domain-specific agents (finance, legal, retail, etc.). The system consists of:

- **companion_api**: TypeScript/Express API backend 
- **companion_web**: Next.js frontend application
- **Python AI agents**: Core AI processing and agent logic
- **Multiple deployment targets**: Vercel, Railway, Render

## Working Effectively

### Initial Setup and Dependencies

1. **Install Node.js dependencies**:
   ```bash
   npm install
   ```
   Takes ~20 seconds. Installs workspace dependencies for both API and web applications.

2. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```
   Takes ~30 seconds. Installs core Python packages: flask, gunicorn, openai, redis, uuid.

3. **Additional Python dependencies for full functionality**:
   ```bash
   pip3 install -r services/robot_core/requirements.txt
   pip3 install -r lyra-ai/backend/requirements.txt  
   pip3 install -r lyra_app/requirements.txt
   ```
   ⚠️ **MAY FAIL** due to network timeouts with PyPI. Alternative: `pip3 install uvicorn fastapi` for key missing packages.
   Takes ~45 seconds total when successful. Required for FastAPI, uvicorn, and specialized agent features.

### Environment Configuration

1. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Set required variables in .env**:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key
   NODE_ENV=development
   PORT=8787
   ALLOWED_ORIGINS=http://localhost:3000
   ```

3. **Copy .env to API directory** (required for proper loading):
   ```bash
   cp .env apps/companion_api/
   ```

### Build Commands

1. **Build API application**:
   ```bash
   cd apps/companion_api && npm run build
   ```
   Takes ~3 seconds. NEVER CANCEL. Uses TypeScript compiler.

2. **Check web pages structure**:
   ```bash
   npm run check:pages
   ```
   Takes <1 second. Validates Next.js page exports.

3. **Build web application** (currently has dependency issues):
   ```bash
   cd apps/companion_web && npm run build
   ```
   ⚠️ **CURRENTLY FAILS** due to missing `next-auth` dependency. Build time would be ~30-60 seconds when working. NEVER CANCEL build processes.

### Running Applications

1. **Start API server**:
   ```bash
   cd apps/companion_api && npm run dev
   ```
   Takes ~3-5 seconds to start. Runs on http://localhost:8787
   **NEVER CANCEL** - Server needs to stay running for development.

2. **Start web application**:
   ```bash
   cd apps/companion_web && npm run dev  
   ```
   ⚠️ **CURRENTLY FAILS** due to missing dependencies. Would run on http://localhost:3000 when working.

3. **Start both applications** (from root):
   ```bash
   npm run dev
   ```
   Starts both API and web servers concurrently.

### Testing and Validation

1. **Run Python tests**:
   ```bash
   python3 tests/test_robotics_sandbox.py
   ```
   Takes ~5-10 seconds. Tests robotics safety configuration.

2. **Test API health endpoint**:
   ```bash
   curl http://localhost:8787/health
   ```
   Should return JSON with status information.

3. **Run security features test**:
   ```bash
   ./test_security_features.sh
   ```
   Takes ~10 seconds. Validates environment and security configuration.

4. **Test memory system**:
   ```bash
   python3 controller.py --test-memory
   ```
   ⚠️ **CURRENTLY FAILS** due to missing uvicorn dependency.

## Validation Scenarios

### Complete End-to-End Workflow (Recommended)
After any changes to the system, run this complete validation:

1. **Fresh dependency install**:
   ```bash
   npm install
   pip3 install -r requirements.txt
   ```

2. **Build validation**:
   ```bash
   npm run check:pages
   cd apps/companion_api && npm run build
   ```

3. **Start API server**:
   ```bash
   cd apps/companion_api && npm run dev
   ```
   Wait for "✅ Environment validation passed" and "🚀 API server running on port 8787"

4. **Test endpoints** (in new terminal):
   ```bash
   curl http://localhost:8787/health
   curl -H "Origin: http://localhost:3000" http://localhost:8787/health
   ```

5. **Run test suites**:
   ```bash
   python3 tests/test_robotics_sandbox.py
   ./test_security_features.sh
   ```

6. **Stop server**: Ctrl+C in API terminal

Expected total time: ~2-3 minutes. All commands should complete successfully.

### API Server Validation
After starting the API server, ALWAYS test:

1. **Health check**: `curl http://localhost:8787/health` - Should return JSON status
2. **CORS validation**: `curl -H "Origin: http://localhost:3000" http://localhost:8787/health` - Should include CORS headers
3. **Environment validation**: Server logs should show "✅ Environment validation passed"

### Python Components Validation  
After any Python changes:

1. **Run robotics tests**: `python3 tests/test_robotics_sandbox.py` - Should pass all safety checks
2. **Test security script**: `./test_security_features.sh` - Should complete without errors

## Critical Build Information

### Timeout Requirements (CRITICAL)
- **NPM installs**: Set timeout to 120+ seconds minimum 
- **API builds**: Set timeout to 60+ seconds minimum
- **Web builds**: Set timeout to 180+ seconds minimum (when dependencies are fixed)
- **Python installs**: Set timeout to 600+ seconds (network dependent)
- **Server startup**: Set timeout to 60+ seconds minimum
- **NEVER CANCEL** any build, install, or test process

### Expected Build Times (Measured)
- Node.js workspace install: ~6-20 seconds
- API TypeScript build: ~3 seconds 
- Python requirements install: ~1-30 seconds (may fail due to network timeouts)
- API server startup: ~3-5 seconds
- Security test script: <1 second
- Pages check script: <1 second

## Common Issues and Workarounds

### Known Build Issues

1. **Web application build fails**: Missing `next-auth/react` dependency
   - **Status**: Known issue, missing from package.json
   - **Workaround**: Focus on API development, web build will be fixed separately

2. **Python controller fails**: Missing `uvicorn` dependency
   - **Status**: PyPI network timeouts prevent installation
   - **Solution**: Try `pip3 install uvicorn fastapi` when network is stable
   - **Alternative**: Use individual agent scripts instead

3. **Environment not loading**: .env file location
   - **Solution**: Copy .env to `apps/companion_api/` directory
   - **Required**: API server reads .env from its own directory

4. **PyPI network timeouts**: pip install commands may fail
   - **Status**: External network connectivity issue  
   - **Workaround**: Retry installation commands or work with existing packages
   - **Critical**: Core requirements.txt usually installs successfully

### Security and Validation

- **Always run** `./test_security_features.sh` before deployment
- **Environment validation** catches invalid API keys and missing variables
- **Rate limiting** is environment-specific: 1000/15min (dev), 100/15min (prod)
- **CORS** is properly configured per environment

## Repository Structure

### Key Directories
- `/apps/companion_api/` - Express TypeScript API server
- `/apps/companion_web/` - Next.js frontend (has dependency issues)
- `/agents/` - Python AI agent implementations  
- `/core/` - Python base classes and utilities
- `/tests/` - Python test suites
- `/docs/` - Documentation including security and robotics safety
- `/.github/workflows/` - CI/CD pipeline definitions

### Important Files
- `package.json` - Workspace configuration and scripts
- `.env.example` - Comprehensive environment variable documentation
- `requirements.txt` - Core Python dependencies
- `CODEX.md` - System architecture and deployment guide
- `test_security_features.sh` - Security validation script

## Deployment Information

### Supported Platforms
- **Vercel**: For Next.js web application
- **Railway**: For both API and web applications  
- **Render**: For API backend
- **GitHub Actions**: Automated CI/CD pipelines

### CI/CD Pipelines
- API deployment triggers on push to main
- Security validation runs automatically
- Build processes use proper timeouts and never cancel policies

## Development Best Practices

1. **Always validate changes** with security test script
2. **Test API endpoints** after any backend changes
3. **Use proper timeouts** for all build commands (60+ minutes)
4. **Copy .env files** to appropriate directories before testing
5. **Run Python tests** after any agent or core changes
6. **Check health endpoints** to ensure services are operational
7. **Monitor environment validation** logs for configuration issues

Remember: **NEVER CANCEL** long-running build or install processes. The system is designed for reliability and all timeouts should account for worst-case scenarios.