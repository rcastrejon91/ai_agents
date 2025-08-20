"""Tests for the VAE implementation."""

import torch
import pytest
from model.vae import AAPTVAE


class TestAAPTVAE:
    """Test suite for AAPTVAE implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.vae = AAPTVAE()
        self.batch_size = 4
        self.input_dim = 512
        self.latent_dim = 256
        
    def test_vae_initialization(self):
        """Test VAE initializes correctly."""
        assert self.vae is not None
        assert hasattr(self.vae, 'encode')
        assert hasattr(self.vae, 'decode')
        
    def test_encoder_output_shape(self):
        """Test encoder outputs correct shapes for mu and logvar."""
        x = torch.randn(self.batch_size, self.input_dim)
        mu, logvar = self.vae.encode(x)
        
        assert mu.shape == (self.batch_size, self.latent_dim)
        assert logvar.shape == (self.batch_size, self.latent_dim)
        
    def test_reparameterization(self):
        """Test reparameterization trick produces correct shapes."""
        mu = torch.randn(self.batch_size, self.latent_dim)
        logvar = torch.randn(self.batch_size, self.latent_dim)
        
        z = self.vae.reparameterize(mu, logvar)
        assert z.shape == (self.batch_size, self.latent_dim)
        
    def test_decoder_output_shape(self):
        """Test decoder outputs correct reconstruction shape."""
        z = torch.randn(self.batch_size, self.latent_dim)
        reconstruction = self.vae.decode(z)
        
        assert reconstruction.shape == (self.batch_size, self.input_dim)
        
    def test_forward_pass(self):
        """Test complete forward pass through VAE."""
        x = torch.randn(self.batch_size, self.input_dim)
        reconstruction, mu, logvar = self.vae.forward(x)
        
        assert reconstruction.shape == x.shape
        assert mu.shape == (self.batch_size, self.latent_dim)
        assert logvar.shape == (self.batch_size, self.latent_dim)
        
    def test_loss_computation(self):
        """Test VAE loss computation."""
        x = torch.randn(self.batch_size, self.input_dim)
        reconstruction, mu, logvar = self.vae.forward(x)
        
        loss = self.vae.loss_function(reconstruction, x, mu, logvar)
        
        assert isinstance(loss, dict)
        assert 'loss' in loss
        assert 'reconstruction_loss' in loss
        assert 'kl_divergence' in loss
        
        # Check loss values are reasonable
        assert loss['loss'].item() >= 0
        assert loss['reconstruction_loss'].item() >= 0
        assert loss['kl_divergence'].item() >= 0
        
    def test_deterministic_with_seed(self):
        """Test reproducibility with fixed seed."""
        torch.manual_seed(42)
        x = torch.randn(self.batch_size, self.input_dim)
        
        torch.manual_seed(42)
        result1 = self.vae.forward(x)
        
        torch.manual_seed(42)
        result2 = self.vae.forward(x)
        
        # Results should be identical with same seed
        assert torch.allclose(result1[0], result2[0], atol=1e-6)
        assert torch.allclose(result1[1], result2[1], atol=1e-6)
        assert torch.allclose(result1[2], result2[2], atol=1e-6)


if __name__ == "__main__":
    # Run basic smoke test
    test_vae = TestAAPTVAE()
    test_vae.setup_method()
    
    print("Testing VAE initialization...")
    test_vae.test_vae_initialization()
    print("✓ Initialization test passed")
    
    print("\nAll basic tests completed!")