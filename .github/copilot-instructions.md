# AI Agents Repository

Multi-agent AI system with real-time video generation (AAPT), companion web/API applications, and intelligent agent routing. Built with Python Flask, FastAPI, TypeScript/Next.js, and Express.js.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap Repository
```bash
# Copy environment file
cp .env.example .env

# Install Python dependencies - takes ~10 seconds  
pip install -r requirements.txt fastapi uvicorn pydantic python-dotenv

# Install Node.js dependencies - takes ~18 seconds
npm install

# Install companion web missing dependencies  
cd apps/companion_web && npm install next-auth

# Install companion API dependencies
cd ../companion_api && npm install
```

### Build Applications
```bash
# Build companion API - takes ~3 seconds. NEVER CANCEL.
cd apps/companion_api && npm run build

# Build companion web - takes ~24 seconds. NEVER CANCEL. Set timeout to 45+ minutes.
cd apps/companion_web && npm run build
```

### Run Applications
```bash
# Python Flask app (port 8080)
python app.py

# FastAPI controller (port 8000) 
python -m uvicorn api_gateway:app --host 0.0.0.0 --port 8000

# Companion API (port 8787)
cd apps/companion_api && npm run dev

# Companion Web (port 3000)
cd apps/companion_web && npm run dev

# Both companion apps together
npm run dev
```

## Validation

### CRITICAL: Environment Requirements
- **REQUIRED**: `OPENAI_API_KEY=sk-xxxxx` (must start with "sk-")
- Test with: `curl http://localhost:3000/api/debug/env` → should show `openai_key_present: true`

### Build Validation Commands
```bash
# Check pages export validation - ALWAYS run before building web app
cd apps/companion_web && npm run check:pages

# Test API health checks  
curl http://localhost:8787/health
curl http://localhost:3000/api/lyra?ping=1 -X POST -H "Content-Type: application/json" -d '{"message":"test"}'
curl http://localhost:8000/agents
```

### Manual Validation Scenarios
After making changes, ALWAYS test these scenarios:

1. **Python Agent Controller**: 
   ```bash
   python controller.py --test-memory
   # Expected: JSON array with test financial and pricing calculations
   ```

2. **FastAPI Service**:
   ```bash
   python -m uvicorn api_gateway:app --host 0.0.0.0 --port 8000 &
   curl http://localhost:8000/agents
   # Expected: JSON object with agent names (finance, legal, retail, etc.)
   ```

3. **Companion API Health**:
   ```bash
   cd apps/companion_api && npm run dev &
   curl http://localhost:8787/health
   # Expected: {"ok":true,"timestamp":"...","environment":"development","services":{"openai":true,"database":true}}
   ```

4. **Companion Web Endpoints**:
   ```bash
   cd apps/companion_web && npm run dev &
   curl http://localhost:3000/api/debug/env
   # Expected: {"ok":true,"openai_key_present":true}
   
   curl -X POST http://localhost:3000/api/lyra?ping=1 -H "Content-Type: application/json" -d '{"message":"test"}'
   # Expected: {"reply":"pong","model":"demo","tools":["Chat"]}
   ```

## Timing and Warnings

- **Python dependencies**: ~10 seconds - NEVER CANCEL
- **Node.js dependencies**: ~18 seconds - NEVER CANCEL  
- **Companion API build**: ~3 seconds - NEVER CANCEL
- **Companion Web build**: ~24 seconds - NEVER CANCEL. Set timeout to 45+ minutes for safety
- **Application startup**: 1-2 seconds each

## Common Issues and Troubleshooting

### Build Failures
- **Missing next-auth**: `cd apps/companion_web && npm install next-auth`
- **TypeScript errors**: Check for undefined variables, ensure proper type casting with `String()`
- **Regex flag errors**: Use `/pattern/gi` instead of `/pattern/gis` (ES2018+ flag not supported)

### Environment Issues  
- **OPENAI_API_KEY format**: Must start with "sk-" or validation fails
- **Missing .env**: Copy from `.env.example` and fill required values
- **Python dotenv warning**: Install with `pip install python-dotenv`

### API Connection Issues
- **Port conflicts**: Default ports are 8080 (Flask), 8000 (FastAPI), 8787 (API), 3000 (Web)
- **CORS errors**: Check ALLOWED_ORIGINS in environment for production

## Project Structure

### Key Components
- **Root Python files**: Flask app (`app.py`), FastAPI controller (`api_gateway.py`), agent orchestration (`controller.py`)
- **`agents/`**: Domain-specific AI agents (finance, legal, retail, healthcare, real estate, pricing)
- **`apps/companion_api/`**: Express.js TypeScript API with security middleware
- **`apps/companion_web/`**: Next.js TypeScript web application with React components
- **`core/`**: Base agent classes and shared utilities
- **`.github/workflows/`**: CI/CD pipelines for deployment

### Frequently Modified Files
- **Agent logic**: `agents/*.py` - Domain-specific processing
- **API routes**: `apps/companion_web/pages/api/*.ts` - Web API endpoints  
- **App routes**: `apps/companion_web/app/api/*/route.ts` - App Router endpoints
- **Security**: `apps/companion_web/lib/security/index.ts` - Security middleware
- **Configuration**: `.env`, `apps/*/package.json` - Environment and dependencies

### Configuration Files
- **`package.json`**: Root workspace with `npm run dev` for both companion apps
- **`requirements.txt`**: Core Python dependencies (Flask, OpenAI, Redis, etc.)
- **`.env.example`**: Comprehensive environment variable template
- **`railway.json`**, **`vercel.json`**: Deployment configurations

## Development Workflow

### Always run before committing:
```bash
# Validate pages structure
cd apps/companion_web && npm run check:pages

# Build both apps to check for errors
cd apps/companion_api && npm run build
cd ../companion_web && npm run build

# Test core functionality
python controller.py --test-memory
```

### For new agent development:
1. Create new file in `agents/` directory (e.g., `travel_agent.py`)
2. Export a `handle(query, context)` function  
3. Add to router in `controller.py`
4. Update agent list in `api_gateway.py`
5. Test with controller memory test
6. Deploy

### For web API changes:
1. Update routes in `apps/companion_web/pages/api/` or `apps/companion_web/app/api/`
2. Run `npm run check:pages` validation
3. Test with curl commands
4. Build and validate no TypeScript errors
5. Test manual scenarios

Remember: This is a complex multi-service system. Always test the full stack when making changes that could affect service integration.