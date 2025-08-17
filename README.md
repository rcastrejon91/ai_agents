# ai_agents

# Real-Time Video Generation with AAPT

This repository provides a starting point for building a real-time AI video generation pipeline using **AAPT** (autoregressive adversarial post-training). The goal is to combine transformer models with a variational autoencoder (VAE) to generate videos from text prompts or images with minimal latency.

### Folder Structure

- `model/` - Code for the transformer, VAE, and related components.
- `train/` - Training loops implementing student-forcing and other strategies.
- `inference/` - Scripts and utilities for running the model to produce videos.
- `configs/` - YAML configuration files (resolution, attention window, etc.).
- `utils/` - Helper functions for logging, decoding, and more.

This project is currently a scaffold and will evolve as development progresses. Contributions are welcome!

## AITaskFlo

This repository also includes **AITaskFlo**, an example automation system built with multiple intelligent agents. Each agent can process specialized tasks such as finance calculations, legal clause extraction, retail inventory suggestions, and dynamic product pricing. A FastAPI gateway exposes a simple HTTP interface.

### Agent Memory

`AITaskFlo` ships with a lightweight JSON memory layer that records each
request and response per session. The controller generates a session ID
when one is not supplied. Inspect stored history or run a quick demo via:

```bash
python controller.py --test-memory
```

### Visualizing Session Activity

The Streamlit dashboard now includes a simple bar chart that displays how many
records are stored for each session. Launch `app.py` to explore agent interactions
and view session counts at a glance.

### Reactive World State

The system now includes a lightweight world state engine that mutates the
environment in response to agent emotion and memory. Check out
`world_state_engine.py`, `timeline_branching.py`, and
`consequence_orchestrator.py` for simple examples of how feelings can reshape
the simulated surroundings.

### Dynamic Pricing Agent

A new `PricingAgent` demonstrates a dynamic pricing algorithm that adjusts
product prices using real-time analytics. Provide user engagement metrics to the
agent and receive a calculated price in response:

```bash
python controller.py --test-memory  # optional memory test
# Example call via the controller (pseudo-code)
# await controller.route("pricing", {"session_id": "123", "metrics": {...}})
```

### Passive Income Bot

`passive_income_bot.py` runs the `PricingAgent` on a loop with example metrics
and stores the recommended prices in `pricing_log.json`. This simple automation
shows how dynamic pricing could keep working for you even while you sleep.

Run it with:

```bash
python passive_income_bot.py
```

## Environment Configuration

This repository includes frontend applications in `frontend/`, `lyra-ai/frontend/`, and `lyra/frontend/` that can be configured to work with different backend environments.

### Setup Instructions

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your environment variables:**
   - `NEXT_PUBLIC_BACKEND_URL`: Set this to your backend API URL (e.g., `https://api.yourdomain.com`)
   - `NODE_ENV`: Set to `production` for production builds, defaults to `development`

3. **Development vs Production:**
   - **Development**: Uses `http://localhost:5000` by default
   - **Production**: Uses the value from `NEXT_PUBLIC_BACKEND_URL` or falls back to `https://api.yourdomain.com`

### Frontend Applications

Each frontend application includes:
- **Centralized configuration** in `frontend/config/` directory
- **Timeout handling** (10 seconds) for API calls  
- **Proper error handling** with user-friendly messages
- **Environment-based URL switching** for development and production

### Backend Configuration

Both backend applications (`lyra/backend/` and `lyra-ai/backend/`) include:
- **CORS configuration** allowing cross-origin requests
- **Flask applications** running on port 5000 by default

### Building and Running

```bash
# Frontend applications
cd frontend/
npm install
npm run build
npm run dev

# Backend applications  
cd lyra/backend/
python app.py
```
