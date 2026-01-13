"""
Parameter validation utilities for FAL Image-to-Image models
"""

from typing import Union, List
from ..config.constants import (
    SUPPORTED_MODELS, ASPECT_RATIOS, KONTEXT_MULTI_ASPECT_RATIOS,
    PHOTON_STRENGTH_RANGE, KONTEXT_INFERENCE_STEPS_RANGE,
    KONTEXT_GUIDANCE_SCALE_RANGE, SEEDEDIT_GUIDANCE_SCALE_RANGE,
    NANO_BANANA_ASPECT_RATIOS, RESOLUTIONS, OUTPUT_FORMATS
)


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
        raise ValueError(f"Unsupported model: {model}. Supported models: {SUPPORTED_MODELS}")
    return model


def validate_aspect_ratio(aspect_ratio: str, model: str = "photon") -> str:
    """
    Validate and return the aspect ratio.
    
    Args:
        aspect_ratio: Aspect ratio string
        model: Model type ("photon", "kontext", etc.)
        
    Returns:
        Validated aspect ratio
        
    Raises:
        ValueError: If aspect ratio is not supported for the model
    """
    if model in ["photon", "photon_base"]:
        if aspect_ratio not in ASPECT_RATIOS:
            raise ValueError(f"Unsupported aspect ratio for Photon models: {aspect_ratio}. Supported ratios: {ASPECT_RATIOS}")
    elif model == "kontext":
        # Kontext uses resolution_mode instead of aspect_ratio
        valid_modes = ["auto", "match_input"]
        if aspect_ratio not in valid_modes:
            raise ValueError(f"Unsupported resolution mode for Kontext: {aspect_ratio}. Supported modes: {valid_modes}")
    elif model == "kontext_multi":
        if aspect_ratio not in KONTEXT_MULTI_ASPECT_RATIOS:
            raise ValueError(f"Unsupported aspect ratio for Kontext Multi: {aspect_ratio}. Supported ratios: {KONTEXT_MULTI_ASPECT_RATIOS}")
    
    return aspect_ratio


def validate_strength(strength: float) -> float:
    """
    Validate and return the modification strength (Photon only).
    
    Args:
        strength: Modification strength (0-1)
        
    Returns:
        Validated strength value
        
    Raises:
        ValueError: If strength is not in valid range
    """
    min_val, max_val = PHOTON_STRENGTH_RANGE
    if not min_val <= strength <= max_val:
        raise ValueError(f"Strength must be between {min_val} and {max_val}, got: {strength}")
    return strength


def validate_inference_steps(steps: int) -> int:
    """
    Validate and return inference steps (Kontext only).
    
    Args:
        steps: Number of inference steps (1-50)
        
    Returns:
        Validated steps value
        
    Raises:
        ValueError: If steps is not in valid range
    """
    min_val, max_val = KONTEXT_INFERENCE_STEPS_RANGE
    if not min_val <= steps <= max_val:
        raise ValueError(f"Inference steps must be between {min_val} and {max_val}, got: {steps}")
    return steps


def validate_guidance_scale(scale: float, model: str = "kontext") -> float:
    """
    Validate and return guidance scale.
    
    Args:
        scale: Guidance scale value
        model: Model type to determine valid range
        
    Returns:
        Validated scale value
        
    Raises:
        ValueError: If scale is not in valid range
    """
    if model == "seededit":
        min_val, max_val = SEEDEDIT_GUIDANCE_SCALE_RANGE
    else:  # kontext
        min_val, max_val = KONTEXT_GUIDANCE_SCALE_RANGE
    
    if not min_val <= scale <= max_val:
        raise ValueError(f"Guidance scale for {model} must be between {min_val} and {max_val}, got: {scale}")
    return scale


def validate_num_images(num_images: int, max_images: int = 10) -> int:
    """
    Validate number of images to generate.
    
    Args:
        num_images: Number of images to generate
        max_images: Maximum allowed images
        
    Returns:
        Validated number
        
    Raises:
        ValueError: If number is not in valid range
    """
    if not 1 <= num_images <= max_images:
        raise ValueError(f"Number of images must be between 1 and {max_images}, got: {num_images}")
    return num_images


def validate_safety_tolerance(tolerance: int) -> int:
    """
    Validate safety tolerance level.
    
    Args:
        tolerance: Safety tolerance level (1-6)
        
    Returns:
        Validated tolerance level
        
    Raises:
        ValueError: If tolerance is not in valid range
    """
    if not 1 <= tolerance <= 6:
        raise ValueError(f"Safety tolerance must be between 1 and 6, got: {tolerance}")
    return tolerance


def validate_output_format(format_str: str) -> str:
    """
    Validate output format.

    Args:
        format_str: Output format ("jpeg", "png", or "webp")

    Returns:
        Validated format string

    Raises:
        ValueError: If format is not supported
    """
    if format_str not in OUTPUT_FORMATS:
        raise ValueError(f"Output format must be one of {OUTPUT_FORMATS}, got: {format_str}")
    return format_str


def validate_nano_banana_aspect_ratio(aspect_ratio: str) -> str:
    """
    Validate aspect ratio for Nano Banana Pro Edit model.

    Args:
        aspect_ratio: Aspect ratio string

    Returns:
        Validated aspect ratio

    Raises:
        ValueError: If aspect ratio is not supported
    """
    if aspect_ratio not in NANO_BANANA_ASPECT_RATIOS:
        raise ValueError(
            f"Invalid aspect_ratio: {aspect_ratio}. "
            f"Valid options: {NANO_BANANA_ASPECT_RATIOS}"
        )
    return aspect_ratio


def validate_resolution(resolution: str) -> str:
    """
    Validate resolution for models that support 1K/2K/4K.

    Args:
        resolution: Resolution string (1K, 2K, 4K)

    Returns:
        Validated resolution

    Raises:
        ValueError: If resolution is not supported
    """
    if resolution not in RESOLUTIONS:
        raise ValueError(
            f"Invalid resolution: {resolution}. "
            f"Valid options: {RESOLUTIONS}"
        )
    return resolution


def validate_image_urls(
    image_urls: List[str],
    min_count: int = 1,
    max_count: int = 4
) -> List[str]:
    """
    Validate list of image URLs for multi-image models.

    Args:
        image_urls: List of image URLs
        min_count: Minimum required images
        max_count: Maximum allowed images

    Returns:
        Validated list of URLs

    Raises:
        ValueError: If count is outside valid range
    """
    if not image_urls:
        raise ValueError("At least one image URL is required")

    if len(image_urls) < min_count:
        raise ValueError(f"At least {min_count} image URL(s) required")

    if len(image_urls) > max_count:
        raise ValueError(
            f"Maximum {max_count} image URLs allowed, got {len(image_urls)}"
        )

    return image_urls


def validate_reframing_coordinates(
    x_start: Union[int, None],
    y_start: Union[int, None],
    x_end: Union[int, None],
    y_end: Union[int, None]
) -> tuple:
    """
    Validate reframing coordinates.
    
    Args:
        x_start: Start X coordinate
        y_start: Start Y coordinate
        x_end: End X coordinate
        y_end: End Y coordinate
        
    Returns:
        Tuple of validated coordinates (x_start, y_start, x_end, y_end)
        
    Raises:
        ValueError: If coordinates are invalid
    """
    # If all are None, return None tuple
    if all(coord is None for coord in [x_start, y_start, x_end, y_end]):
        return (None, None, None, None)
    
    # If any are provided, all must be provided
    if any(coord is None for coord in [x_start, y_start, x_end, y_end]):
        raise ValueError("If any reframing coordinate is provided, all must be provided")
    
    # Validate coordinate values
    if x_start < 0 or y_start < 0:
        raise ValueError("Start coordinates must be non-negative")
    
    if x_end <= x_start:
        raise ValueError("x_end must be greater than x_start")
    
    if y_end <= y_start:
        raise ValueError("y_end must be greater than y_start")
    
    return (x_start, y_start, x_end, y_end)


def validate_grid_position(
    grid_position_x: Union[int, None],
    grid_position_y: Union[int, None]
) -> tuple:
    """
    Validate grid position for reframing.
    
    Args:
        grid_position_x: X position of the grid
        grid_position_y: Y position of the grid
        
    Returns:
        Tuple of validated positions (grid_position_x, grid_position_y)
        
    Raises:
        ValueError: If positions are invalid
    """
    # Both must be None or both must be provided
    if (grid_position_x is None) != (grid_position_y is None):
        raise ValueError("Both grid_position_x and grid_position_y must be provided together")
    
    if grid_position_x is None:
        return (None, None)
    
    # Validate values
    if grid_position_x < 0 or grid_position_y < 0:
        raise ValueError("Grid positions must be non-negative")
    
    return (grid_position_x, grid_position_y)