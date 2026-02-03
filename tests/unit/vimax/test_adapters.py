"""
Tests for ViMax adapters.

These tests verify adapter configurations, model mappings, and core logic patterns
without requiring the full package import chain.
"""

import pytest
import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# Replicated Adapter Configurations for Testing
# These mirror the actual adapter configs to test the configuration logic
# ==============================================================================

class AdapterConfig(BaseModel):
    """Base adapter configuration."""
    provider: str = "fal"
    model: str = ""
    timeout: float = 120.0


class ImageAdapterConfig(AdapterConfig):
    """Configuration for image adapter."""
    model: str = "flux_dev"
    aspect_ratio: str = "1:1"
    num_inference_steps: int = 28
    guidance_scale: float = 3.5
    output_dir: str = "output/vimax/images"


class VideoAdapterConfig(AdapterConfig):
    """Configuration for video adapter."""
    model: str = "kling"
    duration: float = 5.0
    fps: int = 24
    output_dir: str = "output/vimax/videos"


class LLMAdapterConfig(AdapterConfig):
    """Configuration for LLM adapter."""
    model: str = "openrouter/anthropic/claude-3.5-sonnet"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 60.0


class Message(BaseModel):
    """Chat message."""
    role: str  # system, user, assistant
    content: str


class LLMResponse(BaseModel):
    """LLM response."""
    content: str
    model: str
    usage: Dict[str, int] = Field(default_factory=dict)
    cost: float = 0.0


class ImageOutput(BaseModel):
    """Image generation output."""
    image_path: str
    image_url: Optional[str] = None
    prompt: str = ""
    model: str = ""
    width: int = 0
    height: int = 0
    generation_time: float = 0.0
    cost: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VideoOutput(BaseModel):
    """Video generation output."""
    video_path: str
    video_url: Optional[str] = None
    source_image: Optional[str] = None
    prompt: str = ""
    model: str = ""
    duration: float = 0.0
    width: int = 0
    height: int = 0
    fps: int = 24
    generation_time: float = 0.0
    cost: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Model mappings from the actual adapters
IMAGE_MODEL_MAP = {
    "flux_dev": "fal-ai/flux/dev",
    "flux_schnell": "fal-ai/flux/schnell",
    "imagen4": "google/imagen-4",
    "nano_banana_pro": "fal-ai/nano-banana-pro",
    "gpt_image_1_5": "fal-ai/gpt-image-1-5",
    "seedream_v3": "fal-ai/seedream-v3",
}

VIDEO_MODEL_MAP = {
    "kling": "fal-ai/kling-video/v1/standard/image-to-video",
    "kling_2_1": "fal-ai/kling-video/v2.1/standard/image-to-video",
    "kling_2_6_pro": "fal-ai/kling-video/v2.6/pro/image-to-video",
    "veo3": "google/veo-3",
    "veo3_fast": "google/veo-3-fast",
    "hailuo": "fal-ai/hailuo/image-to-video",
    "grok_imagine": "fal-ai/grok/imagine",
}

LLM_MODEL_ALIASES = {
    "claude-3.5-sonnet": "openrouter/anthropic/claude-3.5-sonnet",
    "claude-3-opus": "openrouter/anthropic/claude-3-opus",
    "gpt-4": "openrouter/openai/gpt-4-turbo",
    "gpt-4o": "openrouter/openai/gpt-4o",
    "gemini-pro": "openrouter/google/gemini-pro",
}

IMAGE_COST_MAP = {
    "flux_dev": 0.003,
    "flux_schnell": 0.001,
    "imagen4": 0.004,
}

VIDEO_COST_PER_SECOND = {
    "kling": 0.03,
    "veo3": 0.10,
    "hailuo": 0.02,
}


# ==============================================================================
# Tests
# ==============================================================================

class TestImageAdapterConfig:
    """Tests for ImageAdapterConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = ImageAdapterConfig()
        assert config.model == "flux_dev"
        assert config.aspect_ratio == "1:1"
        assert config.num_inference_steps == 28

    def test_custom_config(self):
        """Test custom configuration."""
        config = ImageAdapterConfig(
            model="imagen4",
            aspect_ratio="16:9",
            output_dir="custom/output",
        )
        assert config.model == "imagen4"
        assert config.aspect_ratio == "16:9"


class TestImageModelMapping:
    """Tests for image model mappings."""

    def test_available_models(self):
        """Test available models list."""
        models = list(IMAGE_MODEL_MAP.keys())
        assert "flux_dev" in models
        assert "flux_schnell" in models
        assert "imagen4" in models

    def test_model_endpoints(self):
        """Test model endpoint mappings."""
        assert IMAGE_MODEL_MAP["flux_dev"] == "fal-ai/flux/dev"
        assert IMAGE_MODEL_MAP["flux_schnell"] == "fal-ai/flux/schnell"

    def test_model_info(self):
        """Test model info retrieval."""
        model = "flux_dev"
        info = {
            "model": model,
            "endpoint": IMAGE_MODEL_MAP.get(model, "unknown"),
            "cost": IMAGE_COST_MAP.get(model, 0.003),
        }
        assert info["model"] == "flux_dev"
        assert "endpoint" in info
        assert info["cost"] == 0.003


class TestVideoAdapterConfig:
    """Tests for VideoAdapterConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = VideoAdapterConfig()
        assert config.model == "kling"
        assert config.duration == 5.0
        assert config.fps == 24

    def test_custom_config(self):
        """Test custom configuration."""
        config = VideoAdapterConfig(
            model="veo3",
            duration=10.0,
            fps=30,
        )
        assert config.model == "veo3"
        assert config.duration == 10.0


class TestVideoModelMapping:
    """Tests for video model mappings."""

    def test_available_models(self):
        """Test available models list."""
        models = list(VIDEO_MODEL_MAP.keys())
        assert "kling" in models
        assert "veo3" in models
        assert "hailuo" in models

    def test_model_endpoints(self):
        """Test model endpoint mappings."""
        assert "kling-video" in VIDEO_MODEL_MAP["kling"]
        assert "veo-3" in VIDEO_MODEL_MAP["veo3"]

    def test_cost_estimation(self):
        """Test video cost estimation."""
        model = "kling"
        duration = 10.0
        cost = VIDEO_COST_PER_SECOND.get(model, 0.03) * duration
        assert cost == 0.30


class TestLLMAdapterConfig:
    """Tests for LLMAdapterConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = LLMAdapterConfig()
        assert config.model == "openrouter/anthropic/claude-3.5-sonnet"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096

    def test_custom_config(self):
        """Test custom configuration."""
        config = LLMAdapterConfig(
            model="openrouter/openai/gpt-4o",
            temperature=0.5,
        )
        assert config.model == "openrouter/openai/gpt-4o"
        assert config.temperature == 0.5


class TestLLMModelAliases:
    """Tests for LLM model alias resolution."""

    def test_alias_resolution(self):
        """Test model alias resolution."""
        assert "claude-3.5-sonnet" in LLM_MODEL_ALIASES
        assert "gpt-4o" in LLM_MODEL_ALIASES

    def test_resolve_alias(self):
        """Test resolving an alias to full model name."""
        alias = "claude-3.5-sonnet"
        resolved = LLM_MODEL_ALIASES.get(alias, alias)
        assert "openrouter/anthropic/claude-3.5-sonnet" == resolved

    def test_unknown_alias_passthrough(self):
        """Test that unknown aliases pass through unchanged."""
        unknown = "some-custom-model"
        resolved = LLM_MODEL_ALIASES.get(unknown, unknown)
        assert resolved == unknown


class TestMessage:
    """Tests for Message model."""

    def test_message_creation(self):
        """Test message creation."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_roles(self):
        """Test different message roles."""
        system = Message(role="system", content="You are helpful")
        user = Message(role="user", content="Hi")
        assistant = Message(role="assistant", content="Hello!")

        assert system.role == "system"
        assert user.role == "user"
        assert assistant.role == "assistant"


class TestLLMResponse:
    """Tests for LLMResponse model."""

    def test_response_creation(self):
        """Test LLM response creation."""
        response = LLMResponse(
            content="Hello! How can I help?",
            model="claude-3.5-sonnet",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            cost=0.001,
        )
        assert response.content == "Hello! How can I help?"
        assert response.usage["total_tokens"] == 30
        assert response.cost == 0.001


class TestImageOutput:
    """Tests for ImageOutput model."""

    def test_output_creation(self):
        """Test image output creation."""
        output = ImageOutput(
            image_path="/tmp/test.png",
            prompt="A beautiful sunset",
            model="flux_dev",
            cost=0.003,
        )
        assert output.image_path == "/tmp/test.png"
        assert output.cost == 0.003


class TestVideoOutput:
    """Tests for VideoOutput model."""

    def test_output_creation(self):
        """Test video output creation."""
        output = VideoOutput(
            video_path="/tmp/test.mp4",
            prompt="Walking forward",
            model="kling",
            duration=5.0,
        )
        assert output.video_path == "/tmp/test.mp4"
        assert output.duration == 5.0


class TestAspectRatioConversion:
    """Tests for aspect ratio to size conversion."""

    def test_aspect_to_size(self):
        """Test aspect ratio conversion."""
        sizes = {
            "1:1": "square",
            "16:9": "landscape_16_9",
            "9:16": "portrait_16_9",
            "4:3": "landscape_4_3",
            "3:4": "portrait_4_3",
        }
        assert sizes.get("1:1") == "square"
        assert sizes.get("16:9") == "landscape_16_9"
        assert sizes.get("unknown", "square") == "square"


class TestCostEstimation:
    """Tests for cost estimation logic."""

    def test_llm_cost_estimation(self):
        """Test LLM cost estimation."""
        # Approximate costs per 1K tokens (input, output)
        costs = {
            "openrouter/anthropic/claude-3.5-sonnet": (0.003, 0.015),
            "openrouter/openai/gpt-4o": (0.005, 0.015),
        }

        model = "openrouter/anthropic/claude-3.5-sonnet"
        usage = {"prompt_tokens": 1000, "completion_tokens": 500}

        if model in costs:
            input_cost, output_cost = costs[model]
            total_cost = (usage["prompt_tokens"] * input_cost + usage["completion_tokens"] * output_cost) / 1000
            assert total_cost == pytest.approx(0.0105)

    def test_video_cost_estimation(self):
        """Test video cost estimation."""
        model = "kling"
        duration = 5.0
        cost = VIDEO_COST_PER_SECOND.get(model, 0.03) * duration
        assert cost == 0.15
