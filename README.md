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

## Environment Variables

The companion API and web app require several secrets which are **never** committed to the repository. Create `.env` files from the provided templates and supply the values in your hosting dashboard.

| Variable | Description |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI API key used for chat completions |
| `STRIPE_SECRET_KEY` | Stripe secret for API requests |
| `STRIPE_WEBHOOK_SECRET` | Secret to verify Stripe webhooks |
| `STRIPE_PRICE_PRO` | Stripe price ID for subscriptions |
| `SUCCESS_URL` / `CANCEL_URL` | Redirect URLs after checkout |
| `PORT` | API port (default 8787) |
| `NEXT_PUBLIC_API_URL` | Base URL of the deployed API |
| `NEXT_PUBLIC_STRIPE_PK` | Stripe publishable key for the web app |

### Rotating Secrets

1. Generate a new key in the provider dashboard (OpenAI, Stripe, etc.).
2. Update the value in your deployment platform's environment settings (Railway, Vercel, etc.).
3. Redeploy the service so the new secret takes effect.
