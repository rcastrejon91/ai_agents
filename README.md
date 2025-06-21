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

This repository also includes **AITaskFlo**, an example automation system built with multiple intelligent agents. Each agent can process specialized tasks such as finance calculations, legal clause extraction, and retail inventory suggestions. A FastAPI gateway exposes a simple HTTP interface.

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
