import torch
from torch import nn
from torch.nn import functional as F
from typing import Tuple, Dict


class AAPTVAE(nn.Module):
    """Variational Autoencoder for AAPT video generation.
    
    This VAE implements the standard variational autoencoder architecture with:
    - Multi-layer encoder that outputs mean and log-variance of latent distribution
    - Reparameterization trick for differentiable sampling
    - Multi-layer decoder for reconstruction
    - Combined reconstruction and KL divergence loss
    
    The architecture is flexible and can handle different input dimensions.
    Default configuration is optimized for 512-dimensional inputs (e.g., flattened
    image patches or encoded video features).
    
    Args:
        input_dim: Dimension of input data (default: 512)
        latent_dim: Dimension of latent space (default: 256) 
        hidden_dim: Dimension of hidden layers (default: 400)
        
    Example:
        >>> vae = AAPTVAE(input_dim=512, latent_dim=256)
        >>> x = torch.randn(batch_size, 512)
        >>> reconstruction, mu, logvar = vae.forward(x)
        >>> loss_dict = vae.loss_function(reconstruction, x, mu, logvar)
    """

    def __init__(self, input_dim: int = 512, latent_dim: int = 256, hidden_dim: int = 400):
        super().__init__()
        
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        
        # Encoder: maps input to latent distribution parameters
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        
        # Latent distribution parameters
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)
        
        # Decoder: maps latent variables back to input space
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
        )

    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode the input into latent distribution parameters.
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
            
        Returns:
            Tuple of (mu, logvar) tensors of shape (batch_size, latent_dim)
        """
        h = self.encoder(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """Reparameterization trick for sampling from latent distribution.
        
        Args:
            mu: Mean tensor of shape (batch_size, latent_dim)
            logvar: Log-variance tensor of shape (batch_size, latent_dim)
            
        Returns:
            Sampled latent tensor of shape (batch_size, latent_dim)
        """
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode the latent representation back to the input space.
        
        Args:
            z: Latent tensor of shape (batch_size, latent_dim)
            
        Returns:
            Reconstructed tensor of shape (batch_size, input_dim)
        """
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass through the VAE.
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
            
        Returns:
            Tuple of (reconstruction, mu, logvar)
        """
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        reconstruction = self.decode(z)
        return reconstruction, mu, logvar

    def loss_function(self, 
                     reconstruction: torch.Tensor, 
                     x: torch.Tensor, 
                     mu: torch.Tensor, 
                     logvar: torch.Tensor,
                     beta: float = 1.0) -> Dict[str, torch.Tensor]:
        """Compute the VAE loss (reconstruction + KL divergence).
        
        Args:
            reconstruction: Reconstructed input tensor
            x: Original input tensor
            mu: Mean of latent distribution
            logvar: Log-variance of latent distribution
            beta: Weight for KL divergence term (beta-VAE)
            
        Returns:
            Dictionary containing 'loss', 'reconstruction_loss', and 'kl_divergence'
        """
        # Reconstruction loss (MSE)
        reconstruction_loss = F.mse_loss(reconstruction, x, reduction='mean')
        
        # KL divergence loss
        # -0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
        kl_divergence = -0.5 * torch.mean(
            torch.sum(1 + logvar - mu.pow(2) - logvar.exp(), dim=1)
        )
        
        # Total loss
        loss = reconstruction_loss + beta * kl_divergence
        
        return {
            'loss': loss,
            'reconstruction_loss': reconstruction_loss,
            'kl_divergence': kl_divergence
        }
