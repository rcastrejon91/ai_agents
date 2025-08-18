# Deployment Guide

This guide covers deploying the AI Agents application to various platforms.

## Prerequisites

1. Copy `.env.example` to `.env` and fill in your environment variables
2. Ensure all required API keys are configured
3. Test the application locally before deploying

## Vercel Deployment

### Frontend (Next.js)

1. **Connect Repository**: Import the repository in Vercel
2. **Configure Root Directory**: Set to `apps/companion_web`
3. **Environment Variables**: Add the following in Vercel dashboard:
   ```
   OPENAI_API_KEY=sk-xxx
   TAVILY_API_KEY=tvly-xxx
   NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx
   BACKEND_URL=https://your-backend.railway.app
   ADMIN_DASH_KEY=your-admin-key
   NEXT_PUBLIC_ADMIN_UI_KEY=your-admin-key
   DEBUG=false
   ```

4. **Deploy**: Vercel will automatically build and deploy using the `vercel.json` configuration

### Build Commands
- **Install**: `cd apps/companion_web && npm install`
- **Build**: `cd apps/companion_web && npm run build`
- **Start**: `cd apps/companion_web && npm start`

## Railway Deployment

### Backend Service

1. **Create New Service**: Select the repository
2. **Configure Service**: Railway will use the `railway.json` configuration
3. **Environment Variables**:
   ```
   PORT=${{RAILWAY_PORT}}
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   DEBUG=false
   ```

### Frontend Service

1. **Create Frontend Service**: 
2. **Environment Variables**:
   ```
   NODE_ENV=production
   PORT=${{RAILWAY_PORT}}
   OPENAI_API_KEY=sk-xxx
   TAVILY_API_KEY=tvly-xxx
   NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx
   BACKEND_URL=https://your-backend.railway.app
   ```

## Heroku Deployment

Use the provided `Procfile`:

1. **Install Heroku CLI** and login
2. **Create app**: `heroku create your-app-name`
3. **Set environment variables**:
   ```bash
   heroku config:set OPENAI_API_KEY=sk-xxx
   heroku config:set NODE_ENV=production
   # ... add other variables
   ```
4. **Deploy**: `git push heroku main`

## Docker Deployment

1. **Build containers**:
   ```bash
   # Backend
   docker build -f lyra/backend/Dockerfile -t ai-agents-backend .
   
   # Frontend
   docker build -f apps/companion_web/Dockerfile -t ai-agents-frontend .
   ```

2. **Run with docker-compose**:
   ```bash
   docker-compose up -d
   ```

## Environment Variables Reference

### Required Variables
- `OPENAI_API_KEY`: OpenAI API key for AI functionality
- `NODE_ENV`: Environment (development/production)
- `PORT`: Server port (auto-set by most platforms)

### Optional Variables
- `TAVILY_API_KEY`: For web search functionality
- `NEXT_PUBLIC_SUPABASE_URL`: Database URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Database public key
- `BACKEND_URL`: Backend service URL for frontend
- `ADMIN_DASH_KEY`: Admin dashboard access key
- `DEBUG`: Enable debug logging
- `ALLOWED_ORIGINS`: CORS allowed origins (comma-separated)

## Health Checks

Both services provide health check endpoints:
- **Backend**: `/health`
- **Frontend**: `/api/debug/env`

## Troubleshooting

### Build Failures
1. Check all environment variables are set
2. Verify Node.js version compatibility (18+)
3. Check Python dependencies in `requirements.txt`

### CORS Issues
1. Set `ALLOWED_ORIGINS` to include your frontend domain
2. Ensure HTTPS is used in production
3. Check browser console for specific CORS errors

### API Errors
1. Verify `OPENAI_API_KEY` is valid and has credits
2. Check backend logs for detailed error messages
3. Test API endpoints individually

## Security Notes

1. Never commit `.env` files to version control
2. Use strong, unique admin keys
3. Enable HTTPS in production
4. Regularly rotate API keys
5. Monitor usage and set appropriate rate limits

## Performance Optimization

1. **Frontend**: Enable Vercel caching
2. **Backend**: Use Redis for session storage
3. **Database**: Optimize Supabase queries
4. **Monitoring**: Set up error tracking (e.g., Sentry)

## Monitoring

Recommended monitoring setup:
- **Uptime**: Use services like UptimeRobot
- **Errors**: Sentry or similar error tracking
- **Performance**: Vercel Analytics
- **Logs**: Platform-specific logging (Vercel/Railway logs)