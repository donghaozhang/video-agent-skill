"""
Unit tests for image_splitter module.

Tests grid image splitting functionality.
"""

import pytest
import sys
from pathlib import Path
from PIL import Image
import tempfile
import shutil

# Add package path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages/core/ai_content_pipeline"))

from ai_content_pipeline.image_splitter import (
    split_grid_image,
    SplitConfig,
    get_panel_coordinates,
    get_panel_info,
    GRID_CONFIGS,
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


@pytest.fixture
def sample_2x2_image(temp_dir):
    """Create a sample 2x2 grid image with distinct colors."""
    img = Image.new("RGB", (1024, 1024), color="white")
    # Add distinct colors to each quadrant
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    for i, color in enumerate(colors):
        x_start = (i % 2) * 512
        y_start = (i // 2) * 512
        for x in range(x_start, x_start + 512):
            for y in range(y_start, y_start + 512):
                img.putpixel((x, y), color)
    path = Path(temp_dir) / "grid_2x2.png"
    img.save(path)
    return str(path)


@pytest.fixture
def sample_3x3_image(temp_dir):
    """Create a sample 3x3 grid image."""
    img = Image.new("RGB", (900, 900), color="gray")
    path = Path(temp_dir) / "grid_3x3.png"
    img.save(path)
    return str(path)


class TestSplitGridImage:
    """Tests for split_grid_image function."""

    def test_split_2x2_creates_4_panels(self, sample_2x2_image, temp_dir):
        """2x2 grid splits into exactly 4 panels."""
        output_dir = Path(temp_dir) / "output"
        config = SplitConfig(grid="2x2")

        paths = split_grid_image(sample_2x2_image, str(output_dir), config)

        assert len(paths) == 4
        for p in paths:
            assert Path(p).exists()

    def test_split_2x2_panel_size(self, sample_2x2_image, temp_dir):
        """2x2 panels have correct dimensions."""
        output_dir = Path(temp_dir) / "output"
        config = SplitConfig(grid="2x2")

        paths = split_grid_image(sample_2x2_image, str(output_dir), config)

        for p in paths:
            img = Image.open(p)
            assert img.size == (512, 512)

    def test_split_3x3_creates_9_panels(self, sample_3x3_image, temp_dir):
        """3x3 grid splits into exactly 9 panels."""
        output_dir = Path(temp_dir) / "output"
        config = SplitConfig(grid="3x3")

        paths = split_grid_image(sample_3x3_image, str(output_dir), config)

        assert len(paths) == 9

    def test_split_3x3_panel_size(self, sample_3x3_image, temp_dir):
        """3x3 panels have correct dimensions."""
        output_dir = Path(temp_dir) / "output"
        config = SplitConfig(grid="3x3")

        paths = split_grid_image(sample_3x3_image, str(output_dir), config)

        for p in paths:
            img = Image.open(p)
            assert img.size == (300, 300)

    def test_custom_naming_pattern(self, sample_2x2_image, temp_dir):
        """Custom naming pattern is applied correctly."""
        output_dir = Path(temp_dir) / "output"
        config = SplitConfig(grid="2x2", naming_pattern="scene_{n}")

        paths = split_grid_image(sample_2x2_image, str(output_dir), config)

        assert "scene_1.png" in paths[0]
        assert "scene_2.png" in paths[1]
        assert "scene_3.png" in paths[2]
        assert "scene_4.png" in paths[3]

    def test_jpg_output_format(self, sample_2x2_image, temp_dir):
        """JPG output format works."""
        output_dir = Path(temp_dir) / "output"
        config = SplitConfig(grid="2x2", output_format="jpg")

        paths = split_grid_image(sample_2x2_image, str(output_dir), config)

        for p in paths:
            assert p.endswith(".jpg")
            assert Path(p).exists()

    def test_invalid_grid_raises_error(self, sample_2x2_image, temp_dir):
        """Invalid grid configuration raises ValueError."""
        config = SplitConfig(grid="5x5")

        with pytest.raises(ValueError, match="Invalid grid"):
            split_grid_image(sample_2x2_image, temp_dir, config)

    def test_missing_file_raises_error(self, temp_dir):
        """Non-existent file raises FileNotFoundError."""
        config = SplitConfig(grid="2x2")

        with pytest.raises(FileNotFoundError):
            split_grid_image("nonexistent.png", temp_dir, config)

    def test_creates_output_directory(self, sample_2x2_image, temp_dir):
        """Output directory is created if it doesn't exist."""
        output_dir = Path(temp_dir) / "nested" / "output" / "dir"
        config = SplitConfig(grid="2x2")

        paths = split_grid_image(sample_2x2_image, str(output_dir), config)

        assert output_dir.exists()
        assert len(paths) == 4

    def test_panel_colors_preserved(self, sample_2x2_image, temp_dir):
        """Panel colors are correctly preserved from original."""
        output_dir = Path(temp_dir) / "output"
        config = SplitConfig(grid="2x2")

        paths = split_grid_image(sample_2x2_image, str(output_dir), config)

        # Check first panel is red
        panel1 = Image.open(paths[0])
        pixel = panel1.getpixel((256, 256))
        assert pixel == (255, 0, 0)

        # Check second panel is green
        panel2 = Image.open(paths[1])
        pixel = panel2.getpixel((256, 256))
        assert pixel == (0, 255, 0)


class TestGetPanelCoordinates:
    """Tests for get_panel_coordinates function."""

    def test_2x2_coordinates(self):
        """2x2 grid returns correct coordinates."""
        coords = get_panel_coordinates("2x2", (1024, 1024))

        assert len(coords) == 4
        assert coords[0] == (0, 0, 512, 512)       # Top-left
        assert coords[1] == (512, 0, 1024, 512)    # Top-right
        assert coords[2] == (0, 512, 512, 1024)    # Bottom-left
        assert coords[3] == (512, 512, 1024, 1024) # Bottom-right

    def test_3x3_coordinates(self):
        """3x3 grid returns correct coordinates."""
        coords = get_panel_coordinates("3x3", (900, 900))

        assert len(coords) == 9
        assert coords[0] == (0, 0, 300, 300)       # Top-left
        assert coords[4] == (300, 300, 600, 600)   # Center
        assert coords[8] == (600, 600, 900, 900)   # Bottom-right

    def test_invalid_grid_raises(self):
        """Invalid grid raises ValueError."""
        with pytest.raises(ValueError):
            get_panel_coordinates("4x4", (1000, 1000))


class TestGetPanelInfo:
    """Tests for get_panel_info function."""

    def test_2x2_info(self):
        """2x2 info is correct."""
        info = get_panel_info("2x2")
        assert info["rows"] == 2
        assert info["cols"] == 2
        assert info["panels"] == 4

    def test_3x3_info(self):
        """3x3 info is correct."""
        info = get_panel_info("3x3")
        assert info["rows"] == 3
        assert info["cols"] == 3
        assert info["panels"] == 9

    def test_invalid_grid_raises(self):
        """Invalid grid raises ValueError."""
        with pytest.raises(ValueError):
            get_panel_info("invalid")


class TestSplitConfig:
    """Tests for SplitConfig defaults."""

    def test_default_values(self):
        """Config has sensible defaults."""
        config = SplitConfig()
        assert config.grid == "2x2"
        assert config.output_format == "png"
        assert config.naming_pattern == "panel_{n}"
        assert config.quality == 95

    def test_custom_values(self):
        """Config accepts custom values."""
        config = SplitConfig(
            grid="3x3",
            output_format="jpg",
            naming_pattern="frame_{n}",
            quality=80,
        )
        assert config.grid == "3x3"
        assert config.output_format == "jpg"
        assert config.naming_pattern == "frame_{n}"
        assert config.quality == 80


class TestGridConfigs:
    """Tests for GRID_CONFIGS constant."""

    def test_has_2x2(self):
        """GRID_CONFIGS contains 2x2."""
        assert "2x2" in GRID_CONFIGS

    def test_has_3x3(self):
        """GRID_CONFIGS contains 3x3."""
        assert "3x3" in GRID_CONFIGS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
