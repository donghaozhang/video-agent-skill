"""Tests for registry_data - verifies all models are registered correctly."""

import pytest
from ai_content_pipeline.registry import ModelRegistry

# Trigger registration
import ai_content_pipeline.registry_data  # noqa: F401


class TestModelCounts:
    """Verify expected model counts per category."""

    def test_total_model_count(self):
        """All models are registered (text_to_video=10, image_to_video=15,
        image_to_image=8, avatar=10, video_to_video=4, add_audio=1,
        upscale_video=1, text_to_image=8, text_to_speech=3,
        image_understanding=7, prompt_generation=5, speech_to_text=1).
        Total unique keys >= 73.
        """
        assert ModelRegistry.count() >= 73

    def test_text_to_video_count(self):
        assert len(ModelRegistry.keys_for_category("text_to_video")) == 10

    def test_image_to_video_count(self):
        assert len(ModelRegistry.keys_for_category("image_to_video")) == 15

    def test_image_to_image_count(self):
        assert len(ModelRegistry.keys_for_category("image_to_image")) == 8

    def test_avatar_count(self):
        assert len(ModelRegistry.keys_for_category("avatar")) == 10

    def test_video_to_video_count(self):
        assert len(ModelRegistry.keys_for_category("video_to_video")) == 4

    def test_add_audio_count(self):
        assert len(ModelRegistry.keys_for_category("add_audio")) == 1

    def test_upscale_video_count(self):
        assert len(ModelRegistry.keys_for_category("upscale_video")) == 1

    def test_text_to_image_count(self):
        assert len(ModelRegistry.keys_for_category("text_to_image")) == 8

    def test_text_to_speech_count(self):
        assert len(ModelRegistry.keys_for_category("text_to_speech")) == 3

    def test_image_understanding_count(self):
        assert len(ModelRegistry.keys_for_category("image_understanding")) == 7

    def test_prompt_generation_count(self):
        assert len(ModelRegistry.keys_for_category("prompt_generation")) == 5

    def test_speech_to_text_count(self):
        assert len(ModelRegistry.keys_for_category("speech_to_text")) == 1


class TestRequiredFields:
    """Verify all models have required fields populated."""

    def test_all_models_have_required_fields(self):
        for key in ModelRegistry.all_keys():
            m = ModelRegistry.get(key)
            assert m.key, f"{key}: missing key"
            assert m.name, f"{key}: missing name"
            assert m.endpoint, f"{key}: missing endpoint"
            assert m.categories, f"{key}: missing categories"
            assert m.description, f"{key}: missing description"

    def test_no_duplicate_keys(self):
        keys = ModelRegistry.all_keys()
        assert len(keys) == len(set(keys))


class TestKeyModels:
    """Spot-check specific well-known models."""

    def test_veo3_exists(self):
        m = ModelRegistry.get("veo3")
        assert m.provider == "Google (via FAL)"
        assert m.endpoint == "fal-ai/veo3"
        assert "text_to_video" in m.categories

    def test_kling_3_standard_exists(self):
        m = ModelRegistry.get("kling_3_standard")
        assert m.provider == "Kuaishou"
        assert "text_to_video" in m.categories
        assert len(m.duration_options) == 13  # 3-15

    def test_hailuo_i2v_exists(self):
        m = ModelRegistry.get("hailuo")
        assert "image_to_video" in m.categories
        assert m.endpoint == "fal-ai/minimax/hailuo-02/standard/image-to-video"

    def test_omnihuman_exists(self):
        m = ModelRegistry.get("omnihuman_v1_5")
        assert "avatar" in m.categories
        assert m.provider == "ByteDance"

    def test_thinksound_exists(self):
        m = ModelRegistry.get("thinksound")
        assert "add_audio" in m.categories

    def test_topaz_exists(self):
        m = ModelRegistry.get("topaz")
        assert "upscale_video" in m.categories

    def test_photon_exists(self):
        m = ModelRegistry.get("photon")
        assert "image_to_image" in m.categories

    def test_flux_dev_exists(self):
        m = ModelRegistry.get("flux_dev")
        assert "text_to_image" in m.categories

    def test_elevenlabs_exists(self):
        m = ModelRegistry.get("elevenlabs")
        assert "text_to_speech" in m.categories

    def test_gemini_describe_exists(self):
        m = ModelRegistry.get("gemini_describe")
        assert "image_understanding" in m.categories

    def test_openrouter_prompt_exists(self):
        m = ModelRegistry.get("openrouter_video_prompt")
        assert "prompt_generation" in m.categories

    def test_scribe_v2_exists(self):
        m = ModelRegistry.get("scribe_v2")
        assert "speech_to_text" in m.categories


class TestCostEstimates:
    """Verify cost estimates are populated from registry."""

    def test_cost_estimates_structure(self):
        costs = ModelRegistry.get_cost_estimates()
        assert "text_to_video" in costs
        assert "image_to_video" in costs
        assert "image_to_image" in costs

    def test_veo3_cost(self):
        costs = ModelRegistry.get_cost_estimates()
        assert costs["text_to_video"]["veo3"] == 4.00

    def test_hailuo_pro_cost(self):
        costs = ModelRegistry.get_cost_estimates()
        assert costs["text_to_video"]["hailuo_pro"] == 0.08


class TestProcessingTimes:
    """Verify processing times are populated from registry."""

    def test_processing_times_structure(self):
        times = ModelRegistry.get_processing_times()
        assert "text_to_video" in times
        assert "image_to_video" in times

    def test_veo3_processing_time(self):
        times = ModelRegistry.get_processing_times()
        assert times["text_to_video"]["veo3"] == 300


class TestSupportedModels:
    """Verify SUPPORTED_MODELS structure from registry."""

    def test_supported_models_structure(self):
        supported = ModelRegistry.get_supported_models()
        assert isinstance(supported, dict)
        assert "text_to_video" in supported
        assert "image_to_video" in supported
        assert "avatar" in supported

    def test_supported_models_text_to_video(self):
        supported = ModelRegistry.get_supported_models()
        t2v = supported["text_to_video"]
        assert "veo3" in t2v
        assert "kling_3_standard" in t2v
        assert "hailuo_pro" in t2v


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
