"""
Tests for ViMax adapters.
"""

import pytest
import sys
import os
from unittest.mock import patch

# Add the vimax package directly to path to avoid loading the whole ai_content_platform
vimax_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'packages', 'core', 'ai_content_platform', 'vimax')
sys.path.insert(0, vimax_path)

from adapters.image_adapter import (
    ImageGeneratorAdapter,
    ImageAdapterConfig,
    ImageOutput,
)
from adapters.video_adapter import (
    VideoGeneratorAdapter,
    VideoAdapterConfig,
    VideoOutput,
)
from adapters.llm_adapter import (
    LLMAdapter,
    LLMAdapterConfig,
    LLMResponse,
    Message,
)


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


class TestImageGeneratorAdapter:
    """Tests for ImageGeneratorAdapter."""

    def test_adapter_creation(self):
        """Test adapter creation."""
        adapter = ImageGeneratorAdapter()
        assert adapter.config.model == "flux_dev"

    def test_adapter_with_custom_config(self):
        """Test adapter with custom config."""
        config = ImageAdapterConfig(model="flux_schnell")
        adapter = ImageGeneratorAdapter(config)
        assert adapter.config.model == "flux_schnell"

    def test_available_models(self):
        """Test available models list."""
        adapter = ImageGeneratorAdapter()
        models = adapter.get_available_models()
        assert "flux_dev" in models
        assert "flux_schnell" in models
        assert "imagen4" in models

    def test_model_info(self):
        """Test model info retrieval."""
        adapter = ImageGeneratorAdapter()
        info = adapter.get_model_info("flux_dev")
        assert info["model"] == "flux_dev"
        assert "endpoint" in info
        assert "cost" in info

    @pytest.mark.asyncio
    async def test_mock_generate(self, tmp_path):
        """Test mock image generation."""
        # Clear FAL_KEY to force mock mode
        with patch.dict(os.environ, {"FAL_KEY": ""}, clear=False):
            config = ImageAdapterConfig(output_dir=str(tmp_path))
            adapter = ImageGeneratorAdapter(config)

            result = await adapter.generate("A test prompt")

            assert isinstance(result, ImageOutput)
            assert result.prompt == "A test prompt"
            assert result.model == "flux_dev"
            assert "mock" in result.metadata


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


class TestVideoGeneratorAdapter:
    """Tests for VideoGeneratorAdapter."""

    def test_adapter_creation(self):
        """Test adapter creation."""
        adapter = VideoGeneratorAdapter()
        assert adapter.config.model == "kling"

    def test_available_models(self):
        """Test available models list."""
        adapter = VideoGeneratorAdapter()
        models = adapter.get_available_models()
        assert "kling" in models
        assert "veo3" in models
        assert "hailuo" in models

    @pytest.mark.asyncio
    async def test_mock_generate(self, tmp_path):
        """Test mock video generation."""
        # Clear FAL_KEY to force mock mode
        with patch.dict(os.environ, {"FAL_KEY": ""}, clear=False):
            config = VideoAdapterConfig(output_dir=str(tmp_path))
            adapter = VideoGeneratorAdapter(config)

            # Create a mock input image
            input_image = tmp_path / "input.png"
            input_image.write_text("mock image")

            result = await adapter.generate(
                image_path=str(input_image),
                prompt="Character walking forward",
            )

            assert isinstance(result, VideoOutput)
            assert result.prompt == "Character walking forward"
            assert result.model == "kling"
            assert "mock" in result.metadata


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


class TestLLMAdapter:
    """Tests for LLMAdapter."""

    def test_adapter_creation(self):
        """Test adapter creation."""
        adapter = LLMAdapter()
        assert "claude-3.5-sonnet" in adapter.config.model

    def test_model_aliases(self):
        """Test model alias resolution."""
        adapter = LLMAdapter()
        assert "claude-3.5-sonnet" in adapter.MODEL_ALIASES
        assert "gpt-4o" in adapter.MODEL_ALIASES

    @pytest.mark.asyncio
    async def test_mock_chat(self):
        """Test mock chat response."""
        adapter = LLMAdapter()

        messages = [
            Message(role="user", content="Hello, test message"),
        ]

        response = await adapter.chat(messages)

        assert isinstance(response, LLMResponse)
        assert "Mock LLM response" in response.content
        assert response.usage["total_tokens"] == 150

    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test text generation convenience method."""
        adapter = LLMAdapter()

        result = await adapter.generate_text(
            prompt="Write a short poem",
            system_prompt="You are a poet",
        )

        assert isinstance(result, str)
        assert len(result) > 0


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
