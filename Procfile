# Main web application (lyra_app)
web: gunicorn lyra_app.app:app --bind 0.0.0.0:$PORT

# Alternative FastAPI entry points for specific deployments:
# api: uvicorn api_gateway:app --host 0.0.0.0 --port $PORT
# companion-api: uvicorn apps.companion_api.main:app --host 0.0.0.0 --port $PORT
