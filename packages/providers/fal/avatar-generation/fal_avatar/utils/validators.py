"""Validation utilities for FAL avatar generation."""

from typing import List, Optional


def validate_url(url: Optional[str], param_name: str) -> str:
    """
    Validate URL format.

    Args:
        url: URL string to validate
        param_name: Parameter name for error messages

    Returns:
        Validated URL string

    Raises:
        ValueError: If URL is invalid or missing
    """
    if not url:
        raise ValueError(f"{param_name} is required")
    if not url.startswith(("http://", "https://", "data:")):
        raise ValueError(f"{param_name} must be a valid URL or base64 data URI")
    return url


def validate_resolution(resolution: str, supported: List[str]) -> str:
    """
    Validate resolution parameter.

    Args:
        resolution: Resolution string (e.g., "720p", "1080p")
        supported: List of supported resolutions

    Returns:
        Validated resolution string

    Raises:
        ValueError: If resolution is not supported
    """
    if resolution not in supported:
        raise ValueError(
            f"Unsupported resolution '{resolution}'. Supported: {supported}"
        )
    return resolution


def validate_duration(duration: float, max_duration: float) -> float:
    """
    Validate duration parameter.

    Args:
        duration: Duration in seconds
        max_duration: Maximum allowed duration

    Returns:
        Validated duration

    Raises:
        ValueError: If duration exceeds maximum
    """
    if duration > max_duration:
        raise ValueError(
            f"Duration {duration}s exceeds maximum {max_duration}s"
        )
    return duration


def validate_aspect_ratio(aspect_ratio: str, supported: List[str]) -> str:
    """
    Validate aspect ratio parameter.

    Args:
        aspect_ratio: Aspect ratio string (e.g., "16:9")
        supported: List of supported aspect ratios

    Returns:
        Validated aspect ratio string

    Raises:
        ValueError: If aspect ratio is not supported
    """
    if aspect_ratio not in supported:
        raise ValueError(
            f"Unsupported aspect ratio '{aspect_ratio}'. Supported: {supported}"
        )
    return aspect_ratio


def validate_text_length(text: Optional[str], max_length: int = 2000) -> str:
    """
    Validate text length for TTS.

    Args:
        text: Text string to validate
        max_length: Maximum allowed characters

    Returns:
        Validated text string

    Raises:
        ValueError: If text is empty or exceeds max length
    """
    if not text:
        raise ValueError("Text is required")
    if len(text) > max_length:
        raise ValueError(f"Text exceeds maximum length of {max_length} characters")
    return text


def validate_reference_images(
    images: Optional[List[str]],
    max_count: int = 4
) -> List[str]:
    """
    Validate reference images list.

    Args:
        images: List of image URLs
        max_count: Maximum number of images allowed

    Returns:
        Validated list of image URLs

    Raises:
        ValueError: If images list is invalid
    """
    if not images or len(images) == 0:
        raise ValueError("At least one reference image is required")
    if len(images) > max_count:
        raise ValueError(f"Maximum {max_count} reference images allowed")

    # Validate each URL
    for i, url in enumerate(images):
        validate_url(url, f"reference_images[{i}]")

    return images
