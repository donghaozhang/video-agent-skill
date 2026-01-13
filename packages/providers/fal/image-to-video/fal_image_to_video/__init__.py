"""
FAL AI Image-to-Video Generator Package

Supports multiple models for high-quality video generation from images.
"""

from .generator import FALImageToVideoGenerator
from .config.constants import ModelType, SUPPORTED_MODELS

__version__ = "2.0.0"
__all__ = ["FALImageToVideoGenerator", "ModelType", "SUPPORTED_MODELS"]
