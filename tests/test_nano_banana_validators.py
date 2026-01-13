"""
Unit tests for Nano Banana Pro Edit validators.

Tests validate_nano_banana_aspect_ratio(), validate_resolution(),
validate_image_urls(), validate_output_format(), and validate_num_images() functions.
"""

import pytest
import sys
from pathlib import Path

# Add the fal_image_to_image package to path
# Note: Directory uses hyphens (image-to-image) which can't be imported via dot notation
_package_path = Path(__file__).parent.parent / "packages" / "providers" / "fal" / "image-to-image"
sys.path.insert(0, str(_package_path))

from fal_image_to_image.utils.validators import (
    validate_nano_banana_aspect_ratio,
    validate_resolution,
    validate_image_urls,
    validate_output_format,
    validate_num_images
)


class TestValidateNanoBananaAspectRatio:
    """Tests for validate_nano_banana_aspect_ratio function."""

    def test_valid_aspect_ratios(self):
        """All 11 aspect ratios should be valid."""
        valid_ratios = [
            "auto", "21:9", "16:9", "3:2", "4:3", "5:4",
            "1:1", "4:5", "3:4", "2:3", "9:16"
        ]
        for ratio in valid_ratios:
            result = validate_nano_banana_aspect_ratio(ratio)
            assert result == ratio, f"Expected {ratio}, got {result}"

    def test_invalid_aspect_ratio_raises_error(self):
        """Invalid aspect ratios should raise ValueError."""
        invalid_ratios = ["invalid", "16:10", "8:5", "2:1", "square", ""]
        for ratio in invalid_ratios:
            with pytest.raises(ValueError) as exc_info:
                validate_nano_banana_aspect_ratio(ratio)
            assert "Invalid aspect_ratio" in str(exc_info.value)

    def test_aspect_ratio_case_sensitive(self):
        """Aspect ratio validation should be case sensitive."""
        with pytest.raises(ValueError):
            validate_nano_banana_aspect_ratio("AUTO")


class TestValidateResolution:
    """Tests for validate_resolution function."""

    def test_valid_resolutions(self):
        """1K, 2K, 4K should be valid."""
        valid_resolutions = ["1K", "2K", "4K"]
        for res in valid_resolutions:
            result = validate_resolution(res)
            assert result == res, f"Expected {res}, got {result}"

    def test_invalid_resolution_raises_error(self):
        """Invalid resolutions should raise ValueError."""
        invalid_resolutions = ["8K", "HD", "1080p", "4k", "2k", "1k", ""]
        for res in invalid_resolutions:
            with pytest.raises(ValueError) as exc_info:
                validate_resolution(res)
            assert "Invalid resolution" in str(exc_info.value)

    def test_resolution_case_sensitive(self):
        """Resolution validation should be case sensitive (must be uppercase)."""
        with pytest.raises(ValueError):
            validate_resolution("4k")  # lowercase should fail


class TestValidateImageUrls:
    """Tests for validate_image_urls function."""

    def test_single_url_valid(self):
        """Single URL should be valid."""
        urls = ["https://example.com/image.jpg"]
        result = validate_image_urls(urls)
        assert result == urls

    def test_multiple_urls_valid(self):
        """2-4 URLs should be valid."""
        urls_2 = ["url1", "url2"]
        urls_3 = ["url1", "url2", "url3"]
        urls_4 = ["url1", "url2", "url3", "url4"]

        assert validate_image_urls(urls_2) == urls_2
        assert validate_image_urls(urls_3) == urls_3
        assert validate_image_urls(urls_4) == urls_4

    def test_empty_list_raises_error(self):
        """Empty list should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_image_urls([])
        assert "At least one image URL is required" in str(exc_info.value)

    def test_too_many_urls_raises_error(self):
        """More than 4 URLs should raise ValueError."""
        urls = ["1", "2", "3", "4", "5"]
        with pytest.raises(ValueError) as exc_info:
            validate_image_urls(urls)
        assert "Maximum 4 image URLs allowed" in str(exc_info.value)

    def test_custom_min_count(self):
        """Custom min_count should be respected."""
        with pytest.raises(ValueError) as exc_info:
            validate_image_urls(["url1"], min_count=2)
        assert "At least 2 image URL(s) required" in str(exc_info.value)

    def test_custom_max_count(self):
        """Custom max_count should be respected."""
        with pytest.raises(ValueError) as exc_info:
            validate_image_urls(["1", "2", "3"], max_count=2)
        assert "Maximum 2 image URLs allowed" in str(exc_info.value)


class TestValidateOutputFormat:
    """Tests for validate_output_format function."""

    def test_valid_formats(self):
        """jpeg, png, webp should be valid."""
        valid_formats = ["jpeg", "png", "webp"]
        for fmt in valid_formats:
            result = validate_output_format(fmt)
            assert result == fmt

    def test_invalid_format_raises_error(self):
        """Invalid formats should raise ValueError."""
        invalid_formats = ["jpg", "gif", "bmp", "tiff", "PNG", "JPEG"]
        for fmt in invalid_formats:
            with pytest.raises(ValueError) as exc_info:
                validate_output_format(fmt)
            assert "Output format must be one of" in str(exc_info.value)


class TestValidateNumImages:
    """Tests for validate_num_images function."""

    def test_valid_num_images(self):
        """Valid number of images within default range (1-10)."""
        valid_nums = [1, 2, 5, 10]
        for num in valid_nums:
            result = validate_num_images(num)
            assert result == num

    def test_boundary_values(self):
        """Edge case: boundary values should be valid."""
        # Lower boundary
        assert validate_num_images(1) == 1
        # Upper boundary with default max
        assert validate_num_images(10) == 10
        # Custom max boundary
        assert validate_num_images(4, max_images=4) == 4

    def test_zero_raises_error(self):
        """Zero images should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_num_images(0)
        assert "Number of images must be between 1 and" in str(exc_info.value)

    def test_negative_raises_error(self):
        """Negative number should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_num_images(-1)
        assert "Number of images must be between 1 and" in str(exc_info.value)

    def test_exceeds_default_max_raises_error(self):
        """Exceeding default max (10) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_num_images(11)
        assert "Number of images must be between 1 and 10" in str(exc_info.value)

    def test_custom_max_images(self):
        """Custom max_images parameter should be respected."""
        # Valid with custom max
        assert validate_num_images(4, max_images=4) == 4
        # Invalid exceeding custom max
        with pytest.raises(ValueError) as exc_info:
            validate_num_images(5, max_images=4)
        assert "Number of images must be between 1 and 4" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
