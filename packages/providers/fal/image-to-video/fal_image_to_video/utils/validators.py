"""
Parameter validation utilities for FAL Image-to-Video.
"""

from typing import List
from ..config.constants import SUPPORTED_MODELS


def validate_model(model: str) -> str:
    """
    Validate and return the model type.

    Args:
        model: Model type string

    Returns:
        Validated model type

    Raises:
        ValueError: If model is not supported
    """
    if model not in SUPPORTED_MODELS:
        raise ValueError(
            f"Unsupported model: {model}. "
            f"Supported models: {SUPPORTED_MODELS}"
        )
    return model


def validate_image_url(url: str) -> str:
    """
    Validate image URL format.

    Args:
        url: Image URL to validate

    Returns:
        Validated URL

    Raises:
        ValueError: If URL is invalid
    """
    if not url:
        raise ValueError("Image URL is required")

    if not url.startswith(("http://", "https://", "data:")):
        raise ValueError(
            f"Invalid image URL format: {url}. "
            "Must start with http://, https://, or data:"
        )

    return url
