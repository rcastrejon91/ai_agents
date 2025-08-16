from .transformer import AAPTTransformer
from .vae import AAPTVAE


def load_model() -> tuple[AAPTTransformer, AAPTVAE]:
    """Instantiate the core models used in AAPT.

    Returns:
        Tuple containing the transformer and VAE models.
    """
    transformer = AAPTTransformer()
    vae = AAPTVAE()
    print("AAPT models loaded: transformer and VAE initialized")
    return transformer, vae


__all__ = ["AAPTTransformer", "AAPTVAE", "load_model"]
