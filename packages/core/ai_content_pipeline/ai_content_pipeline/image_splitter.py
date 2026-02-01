"""
Image splitting utility for grid images.

Splits 2x2 or 3x3 grid images into individual panels.
Long-term design: Extensible for custom grid sizes and crop coordinates.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image


@dataclass
class SplitConfig:
    """Configuration for image splitting.

    Attributes:
        grid: Grid configuration ("2x2" or "3x3")
        output_format: Output format (png, jpg, webp)
        naming_pattern: Filename pattern with {n} for panel number
        quality: JPEG quality if applicable (1-100)
    """
    grid: str = "2x2"
    output_format: str = "png"
    naming_pattern: str = "panel_{n}"
    quality: int = 95


GRID_CONFIGS = {
    "2x2": {"rows": 2, "cols": 2, "panels": 4},
    "3x3": {"rows": 3, "cols": 3, "panels": 9},
}


def split_grid_image(
    image_path: str,
    output_dir: str,
    config: Optional[SplitConfig] = None
) -> List[str]:
    """
    Split a grid image into individual panels.

    Args:
        image_path: Path to the grid image
        output_dir: Directory to save split panels
        config: Split configuration (uses defaults if None)

    Returns:
        List of paths to the split panel images

    Raises:
        ValueError: If grid configuration is invalid
        FileNotFoundError: If image doesn't exist

    Example:
        >>> paths = split_grid_image("grid.png", "output/panels", SplitConfig(grid="2x2"))
        >>> print(paths)
        ['output/panels/panel_1.png', 'output/panels/panel_2.png', ...]
    """
    config = config or SplitConfig()

    if config.grid not in GRID_CONFIGS:
        raise ValueError(
            f"Invalid grid: {config.grid}. Must be one of {list(GRID_CONFIGS.keys())}"
        )

    # Validate image exists
    image_path_obj = Path(image_path)
    if not image_path_obj.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    grid_info = GRID_CONFIGS[config.grid]
    rows, cols = grid_info["rows"], grid_info["cols"]

    # Load image
    img = Image.open(image_path)
    width, height = img.size

    # Calculate panel dimensions
    panel_width = width // cols
    panel_height = height // rows

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Split into panels (row-major order: left-to-right, top-to-bottom)
    panel_paths = []
    panel_num = 1

    for row in range(rows):
        for col in range(cols):
            # Calculate crop box (left, upper, right, lower)
            left = col * panel_width
            upper = row * panel_height
            right = left + panel_width
            lower = upper + panel_height

            # Crop panel
            panel = img.crop((left, upper, right, lower))

            # Generate filename
            filename = config.naming_pattern.replace("{n}", str(panel_num))
            if not filename.endswith(f".{config.output_format}"):
                filename = f"{filename}.{config.output_format}"
            panel_path = output_path / filename

            # Save panel
            if config.output_format.lower() in ("jpg", "jpeg"):
                panel.save(panel_path, "JPEG", quality=config.quality)
            elif config.output_format.lower() == "webp":
                panel.save(panel_path, "WEBP", quality=config.quality)
            else:
                panel.save(panel_path, "PNG")

            panel_paths.append(str(panel_path))
            panel_num += 1

    return panel_paths


def get_panel_coordinates(
    grid: str,
    image_size: Tuple[int, int]
) -> List[Tuple[int, int, int, int]]:
    """
    Get crop coordinates for each panel in a grid.

    Args:
        grid: Grid configuration ("2x2" or "3x3")
        image_size: (width, height) of the image

    Returns:
        List of (left, upper, right, lower) tuples for each panel

    Example:
        >>> coords = get_panel_coordinates("2x2", (1024, 1024))
        >>> print(coords[0])  # Top-left panel
        (0, 0, 512, 512)
    """
    if grid not in GRID_CONFIGS:
        raise ValueError(f"Invalid grid: {grid}")

    grid_info = GRID_CONFIGS[grid]
    rows, cols = grid_info["rows"], grid_info["cols"]
    width, height = image_size
    panel_width = width // cols
    panel_height = height // rows

    coordinates = []
    for row in range(rows):
        for col in range(cols):
            left = col * panel_width
            upper = row * panel_height
            right = left + panel_width
            lower = upper + panel_height
            coordinates.append((left, upper, right, lower))

    return coordinates


def get_panel_info(grid: str) -> dict:
    """
    Get information about a grid configuration.

    Args:
        grid: Grid configuration ("2x2" or "3x3")

    Returns:
        Dictionary with rows, cols, panels count
    """
    if grid not in GRID_CONFIGS:
        raise ValueError(f"Invalid grid: {grid}")
    return GRID_CONFIGS[grid].copy()
