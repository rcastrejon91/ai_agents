# VAE Implementation

This directory contains the implementation of a Variational Autoencoder (VAE) for the AAPT video generation project.

## Overview

The `AAPTVAE` class implements a standard VAE with the following components:

- **Encoder**: Multi-layer neural network that maps input data to latent distribution parameters (mean and log-variance)
- **Reparameterization**: Implements the reparameterization trick for differentiable sampling from the latent distribution
- **Decoder**: Multi-layer neural network that reconstructs data from latent samples
- **Loss Function**: Combines reconstruction loss (MSE) and KL divergence for proper VAE training

## Architecture

```
Input (512) → Encoder → (μ, log σ²) → Reparameterize → z (256) → Decoder → Reconstruction (512)
```

Default architecture:
- **Input dimension**: 512 (configurable)
- **Hidden dimension**: 400 (configurable) 
- **Latent dimension**: 256 (configurable)
- **Activation**: ReLU
- **Loss**: MSE reconstruction + KL divergence

## Usage

### Basic Usage

```python
from model.vae import AAPTVAE
import torch

# Initialize VAE
vae = AAPTVAE(input_dim=512, latent_dim=256, hidden_dim=400)

# Forward pass
x = torch.randn(batch_size, 512)
reconstruction, mu, logvar = vae.forward(x)

# Compute loss
loss_dict = vae.loss_function(reconstruction, x, mu, logvar)
total_loss = loss_dict['loss']
```

### Training Loop

```python
import torch.optim as optim

vae = AAPTVAE()
optimizer = optim.Adam(vae.parameters(), lr=1e-3)

for batch in dataloader:
    optimizer.zero_grad()
    reconstruction, mu, logvar = vae(batch)
    loss_dict = vae.loss_function(reconstruction, batch, mu, logvar)
    loss_dict['loss'].backward()
    optimizer.step()
```

### Generation

```python
# Generate new samples
vae.eval()
with torch.no_grad():
    z = torch.randn(num_samples, vae.latent_dim)
    generated = vae.decode(z)
```

### Latent Space Interpolation

```python
# Interpolate between two inputs
mu1, logvar1 = vae.encode(input1)
mu2, logvar2 = vae.encode(input2)

# Linear interpolation in latent space
alpha = 0.5  # interpolation factor
z_interp = alpha * mu1 + (1 - alpha) * mu2
interpolated = vae.decode(z_interp)
```

## Model Components

### Encoder
- Maps input to latent distribution parameters
- Returns: `(mu, logvar)` where both have shape `(batch_size, latent_dim)`

### Reparameterization
- Implements: `z = μ + σ * ε` where `ε ~ N(0,1)`
- Enables backpropagation through stochastic sampling

### Decoder  
- Maps latent variables back to input space
- Input: `z` with shape `(batch_size, latent_dim)`
- Output: reconstruction with shape `(batch_size, input_dim)`

### Loss Function
- **Reconstruction Loss**: MSE between input and reconstruction
- **KL Divergence**: `KL(q(z|x) || p(z))` where `p(z) = N(0,I)`
- **Total Loss**: `reconstruction_loss + β * kl_divergence` (β=1.0 by default)

## Testing

Run the test suite to verify the implementation:

```bash
cd /path/to/ai_agents
PYTHONPATH=. python -m pytest tests/test_vae.py -v
```

## Examples

See `examples/vae_usage.py` for a complete example including:
- Training loop
- Sample generation  
- Latent space interpolation

```bash
cd /path/to/ai_agents
PYTHONPATH=. python examples/vae_usage.py
```