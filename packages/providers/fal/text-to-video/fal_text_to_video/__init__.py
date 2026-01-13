"""
FAL Text-to-Video package with class-based model architecture.

This package provides a unified interface for text-to-video generation
using various FAL AI models.
"""

from .models import (
    BaseTextToVideoModel,
    Kling26ProModel,
    Sora2Model,
    Sora2ProModel
)

from .config import (
    SUPPORTED_MODELS,
    MODEL_ENDPOINTS,
    MODEL_DISPLAY_NAMES,
    MODEL_PRICING,
    MODEL_INFO
)

from .generator import FALTextToVideoGenerator

__all__ = [
    # Generator
    "FALTextToVideoGenerator",
    # Models
    "BaseTextToVideoModel",
    "Kling26ProModel",
    "Sora2Model",
    "Sora2ProModel",
    # Config
    "SUPPORTED_MODELS",
    "MODEL_ENDPOINTS",
    "MODEL_DISPLAY_NAMES",
    "MODEL_PRICING",
    "MODEL_INFO"
]

__version__ = "1.0.0"
