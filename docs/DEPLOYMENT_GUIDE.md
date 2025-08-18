# Deployment Guide - AI Agents Platform

This guide covers the deployment of the AI Agents platform with all the fixes implemented to resolve deployment blocking issues.

## Issues Resolved

### 1. Environment Configuration Issues ✅
- **Fixed**: Standardized environment variable handling across all components
- **Fixed**: URL routing between frontend and backend services
- **Fixed**: Implemented proper fallback mechanisms for API connections

### 2. API Integration Stability ✅
- **Fixed**: Improved error handling for external API connections
- **Fixed**: Implemented retry mechanisms for intermittent API failures
- **Fixed**: Added comprehensive logging for debugging deployment issues

### 3. Security Configuration ✅
- **Fixed**: Implemented proper authentication flow between components
- **Fixed**: Secured API keys and sensitive configuration
- **Fixed**: Removed problematic next-auth dependency and implemented custom auth

## Architecture Overview

The platform consists of three main components:

1. **companion_api** (Node.js/Express) - Port 8787
2. **companion_web** (Next.js) - Port 3000  
3. **lyra_app** (Python/Flask) - Port 5000

## Prerequisites

- Node.js 18+ 
- Python 3.8+
- OpenAI API key
- Environment variables configured

## Environment Configuration

### 1. Copy Environment File
```bash
cp .env.example .env
```

### 2. Required Environment Variables

**Critical for Production:**
```bash
# Required
OPENAI_API_KEY=sk-your-actual-openai-key
NODE_ENV=production

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
API_SECRET_KEY=your-secure-random-string

# URLs
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_BASE_URL=https://yourdomain.com
```

**Optional but Recommended:**
```bash
# Admin Access
ADMIN_PASSPHRASE=your-admin-passphrase
ADMIN_PIN=your-admin-pin

# Monitoring
DISCORD_WEBHOOK_URL=your-discord-webhook
```

## Local Development

### 1. Install Dependencies
```bash
# Root dependencies
npm install

# API dependencies
cd apps/companion_api && npm install

# Web dependencies  
cd ../companion_web && npm install

# Python dependencies (if using lyra_app)
cd ../../lyra_app && pip install -r requirements.txt
```

### 2. Start Development Servers

**Terminal 1 - API Server:**
```bash
cd apps/companion_api
OPENAI_API_KEY=sk-your-key npm run dev
```

**Terminal 2 - Web Server:**
```bash
cd apps/companion_web  
OPENAI_API_KEY=sk-your-key npm run dev
```

**Terminal 3 - Lyra App (optional):**
```bash
cd lyra_app
OPENAI_API_KEY=sk-your-key python app.py
```

### 3. Health Checks

- API Health: http://localhost:8787/health
- Web Health: http://localhost:3000/api/health
- Web Config: http://localhost:3000/api/config

## Production Deployment

### Option 1: Railway Deployment (Recommended)

Each app has a `railway.json` configuration file for deployment.

**Deploy API:**
```bash
cd apps/companion_api
railway login
railway up
```

**Deploy Web:**
```bash
cd apps/companion_web
railway login  
railway up
```

**Environment Variables in Railway:**
- Set `OPENAI_API_KEY`
- Set `NODE_ENV=production`
- Set `ALLOWED_ORIGINS` to your domain(s)
- Set `NEXT_PUBLIC_API_URL` to your API domain
- Set `API_SECRET_KEY` for authentication

### Option 2: Docker Deployment

**Build Images:**
```bash
# API
cd apps/companion_api
docker build -t ai-agents-api .

# Web  
cd apps/companion_web
docker build -t ai-agents-web .
```

**Run with Docker Compose:**
```yaml
version: '3.8'
services:
  api:
    image: ai-agents-api
    ports:
      - "8787:8787"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NODE_ENV=production
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    
  web:
    image: ai-agents-web
    ports:
      - "3000:3000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NODE_ENV=production
    depends_on:
      - api
```

### Option 3: Manual Server Deployment

**1. Build Applications:**
```bash
# API
cd apps/companion_api
npm run build

# Web
cd apps/companion_web  
npm run build
```

**2. Start Production Servers:**
```bash
# API (with PM2)
cd apps/companion_api
pm2 start dist/index.js --name "ai-agents-api"

# Web (with PM2) 
cd apps/companion_web
pm2 start npm --name "ai-agents-web" -- start
```

## Monitoring and Troubleshooting

### Health Check Endpoints

**API Health Check:**
```bash
curl https://api.yourdomain.com/health
```

**Web Health Check:**
```bash
curl https://yourdomain.com/api/health
```

### Common Issues and Solutions

**1. Build Failures:**
- Ensure all dependencies are installed
- Check TypeScript compilation errors
- Verify environment variables are set

**2. API Connection Issues:**
- Check CORS configuration in ALLOWED_ORIGINS
- Verify API URLs are correctly set
- Test health endpoints

**3. OpenAI API Errors:**
- Verify API key format (starts with sk-)
- Check API key validity
- Monitor rate limits

**4. Authentication Issues:**
- Set API_SECRET_KEY for secure endpoints
- Configure ADMIN_PASSPHRASE/ADMIN_PIN for admin access
- Check CORS origins for cross-domain requests

### Error Handling Features

- **Automatic Retries**: API calls retry up to 3 times with exponential backoff
- **Graceful Degradation**: Services continue working even if external APIs fail
- **Comprehensive Logging**: All errors are logged with context for debugging
- **Health Monitoring**: Real-time status of all services and dependencies

### Logs and Debugging

**View API Logs:**
```bash
# Development
cd apps/companion_api && npm run dev

# Production with PM2
pm2 logs ai-agents-api
```

**View Web Logs:**
```bash
# Development  
cd apps/companion_web && npm run dev

# Production with PM2
pm2 logs ai-agents-web
```

## Security Features

- **Environment Validation**: Automatic validation of required environment variables
- **CORS Protection**: Configurable CORS origins for production security
- **Input Sanitization**: All user inputs are sanitized to prevent XSS
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Error Handling**: Secure error responses that don't leak sensitive information

## Performance Optimizations

- **Retry Logic**: Smart retry mechanisms for external API calls
- **Caching**: Response caching where appropriate
- **Error Boundaries**: Graceful handling of component failures
- **Resource Limits**: Configurable limits for API usage

## Support

For issues or questions:
1. Check health endpoints first
2. Review logs for error details
3. Verify environment configuration
4. Test with minimal configuration

The platform is now production-ready with robust error handling, security measures, and monitoring capabilities.