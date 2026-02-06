"""
Tests for model auto-discovery via MODEL_KEY attributes.

Ensures that all registered models have corresponding classes
that can be discovered and instantiated automatically.
"""

import pytest
from ai_content_pipeline.registry import ModelRegistry
import ai_content_pipeline.registry_data  # noqa: F401


class TestTextToVideoAutoDiscovery:
    """Tests for text-to-video model auto-discovery."""

    def test_model_key_matches_registry(self):
        """MODEL_KEY attribute matches registry key."""
        from fal_text_to_video.generator import MODEL_CLASSES
        for key, cls in MODEL_CLASSES.items():
            assert cls.MODEL_KEY == key

    def test_generator_instantiates_all(self):
        """Generator can instantiate all discovered models."""
        from fal_text_to_video.generator import MODEL_CLASSES
        for key, cls in MODEL_CLASSES.items():
            instance = cls()
            assert instance.model_key == key

    def test_discovered_models_have_endpoint(self):
        """All discovered model instances have endpoints."""
        from fal_text_to_video.generator import MODEL_CLASSES
        for key, cls in MODEL_CLASSES.items():
            instance = cls()
            assert instance.endpoint, f"{key} has no endpoint"


class TestImageToVideoAutoDiscovery:
    """Tests for image-to-video model auto-discovery."""

    def test_all_i2v_models_have_class(self):
        """All registered image-to-video models have a corresponding class."""
        from fal_image_to_video.generator import FALImageToVideoGenerator
        gen = FALImageToVideoGenerator.__new__(FALImageToVideoGenerator)
        gen.models = FALImageToVideoGenerator._build_models()
        provider_keys = ModelRegistry.provider_keys_for_category("image_to_video")
        for key in provider_keys:
            assert key in gen.models, f"Missing class for i2v model {key}"

    def test_i2v_model_count(self):
        """Image-to-video auto-discovers expected number of models."""
        from fal_image_to_video.generator import FALImageToVideoGenerator
        gen = FALImageToVideoGenerator.__new__(FALImageToVideoGenerator)
        gen.models = FALImageToVideoGenerator._build_models()
        assert len(gen.models) == 15


class TestAvatarAutoDiscovery:
    """Tests for avatar model auto-discovery."""

    def test_all_avatar_models_discovered(self):
        """All registered avatar models have a corresponding class."""
        from fal_avatar import FALAvatarGenerator
        gen = FALAvatarGenerator()
        registry_keys = ModelRegistry.keys_for_category("avatar")
        for key in registry_keys:
            assert key in gen.models, f"Missing class for avatar model {key}"

    def test_avatar_model_count(self):
        """Avatar auto-discovers expected number of models."""
        from fal_avatar import FALAvatarGenerator
        gen = FALAvatarGenerator()
        assert len(gen.models) == 10

    def test_fabric_fast_discovered(self):
        """FabricFastModel is discovered as fabric_1_0_fast."""
        from fal_avatar import FALAvatarGenerator
        gen = FALAvatarGenerator()
        assert "fabric_1_0_fast" in gen.models
        assert gen.models["fabric_1_0_fast"].is_fast is True


class TestVideoToVideoAutoDiscovery:
    """Tests for video-to-video model auto-discovery."""

    def test_v2v_model_count(self):
        """Video-to-video auto-discovers expected number of models."""
        from fal_video_to_video.generator import FALVideoToVideoGenerator
        gen = FALVideoToVideoGenerator.__new__(FALVideoToVideoGenerator)
        gen.models = FALVideoToVideoGenerator._build_models()
        assert len(gen.models) == 6


class TestCrossPackageConsistency:
    """Tests for cross-package consistency of registry data."""

    def test_all_models_have_endpoints(self):
        """Every registered model has a non-empty endpoint."""
        for key in ModelRegistry.all_keys():
            m = ModelRegistry.get(key)
            assert m.endpoint, f"{key} has no endpoint"

    def test_all_models_have_categories(self):
        """Every registered model has at least one category."""
        for key in ModelRegistry.all_keys():
            m = ModelRegistry.get(key)
            assert m.categories, f"{key} has no categories"

    def test_no_duplicate_keys(self):
        """No duplicate model keys exist."""
        keys = ModelRegistry.all_keys()
        assert len(keys) == len(set(keys))

    def test_minimum_model_count(self):
        """Registry contains at least 50 models."""
        assert ModelRegistry.count() >= 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
