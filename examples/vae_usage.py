"""
Example usage of the AAPTVAE model for training.

This demonstrates how to use the VAE for training with proper loss computation.
"""

import torch
import torch.optim as optim
from model.vae import AAPTVAE


def train_vae_example():
    """Example training loop for the VAE."""
    
    # Initialize model and optimizer
    vae = AAPTVAE(input_dim=512, latent_dim=256, hidden_dim=400)
    optimizer = optim.Adam(vae.parameters(), lr=1e-3)
    
    # Example training data (replace with actual data)
    batch_size = 32
    num_batches = 100
    
    print("Starting VAE training example...")
    
    for batch_idx in range(num_batches):
        # Generate random data (replace with real data loader)
        data = torch.randn(batch_size, 512)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        reconstruction, mu, logvar = vae.forward(data)
        
        # Compute loss
        loss_dict = vae.loss_function(reconstruction, data, mu, logvar, beta=1.0)
        loss = loss_dict['loss']
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Print progress
        if batch_idx % 20 == 0:
            print(f"Batch {batch_idx:3d}: "
                  f"Total Loss: {loss.item():.4f}, "
                  f"Recon: {loss_dict['reconstruction_loss'].item():.4f}, "
                  f"KL: {loss_dict['kl_divergence'].item():.4f}")
    
    print("Training example completed!")
    return vae


def generate_samples(vae, num_samples=5):
    """Generate new samples from the trained VAE."""
    vae.eval()
    
    with torch.no_grad():
        # Sample from standard normal distribution
        z = torch.randn(num_samples, vae.latent_dim)
        
        # Decode to generate new samples
        generated = vae.decode(z)
        
        print(f"Generated {num_samples} samples with shape: {generated.shape}")
        return generated


def interpolate_latent(vae, start_input, end_input, num_steps=10):
    """Interpolate between two inputs in latent space."""
    vae.eval()
    
    with torch.no_grad():
        # Encode inputs to get latent representations
        start_mu, start_logvar = vae.encode(start_input.unsqueeze(0))
        end_mu, end_logvar = vae.encode(end_input.unsqueeze(0))
        
        # Use means for interpolation (ignore variance for simplicity)
        start_z = start_mu
        end_z = end_mu
        
        # Create interpolation steps
        alphas = torch.linspace(0, 1, num_steps).unsqueeze(1)
        interpolated_z = start_z * (1 - alphas) + end_z * alphas
        
        # Decode interpolated latent vectors
        interpolated = vae.decode(interpolated_z)
        
        print(f"Interpolated between inputs with {num_steps} steps")
        return interpolated


if __name__ == "__main__":
    print("AAPTVAE Example Usage\n" + "="*50)
    
    # Train the VAE
    trained_vae = train_vae_example()
    
    print("\n" + "="*50)
    
    # Generate new samples
    generated_samples = generate_samples(trained_vae, num_samples=5)
    
    print("\n" + "="*50)
    
    # Demonstrate latent space interpolation
    start = torch.randn(512)
    end = torch.randn(512)
    interpolated = interpolate_latent(trained_vae, start, end, num_steps=5)
    
    print("\n✓ VAE example completed successfully!")