# Real-Time Video Generation with AAPT

This repository provides a starting point for building a real-time AI video generation pipeline using **AAPT** (autoregressive adversarial post-training). The goal is to combine transformer models with a variational autoencoder (VAE) to generate videos from text prompts or images with minimal latency.

### Folder Structure

- `model/` – Code for the transformer, VAE, and related components.
- `train/` – Training loops implementing student-forcing and other strategies.
- `inference/` – Scripts and utilities for running the model to produce videos.
- `configs/` – YAML configuration files (resolution, attention window, etc.).
- `utils/` – Helper functions for logging, decoding, and more.

This project is currently a scaffold and will evolve as development progresses. Contributions are welcome!
