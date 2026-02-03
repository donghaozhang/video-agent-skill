# Phase 2: Adapter Layer Implementation

**Duration**: 2-3 days
**Dependencies**: Phase 1 completed
**Outcome**: Adapters bridge ViMax agents to existing generators

---

## Overview

Adapters translate between ViMax agent interfaces and the underlying service APIs. This allows ViMax agents to use the existing FAL, Replicate, and OpenRouter integrations.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ViMax Agent   │────▶│    Adapter      │────▶│   Generator     │
│ (CharacterGen)  │     │ (ImageAdapter)  │     │ (FAL/Replicate) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Subtask 2.1: ImageGeneratorAdapter

**Estimated Time**: 3-4 hours

### Description
Create an adapter that wraps the existing image generators (FAL, Replicate) for use by ViMax agents.

### Source Reference
```
packages/core/ai_content_pipeline/generators/
├── unified_text_to_image.py    # UnifiedTextToImageGenerator
└── fal_image_to_image.py       # FALImageToImageGenerator
```

### Target File
```
packages/core/ai_content_platform/vimax/adapters/image_adapter.py
```

### Implementation

```python
"""
Image Generator Adapter for ViMax agents.

Wraps existing image generators (FAL, Replicate) to provide
a consistent interface for ViMax agents.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

from .base import BaseAdapter, AdapterConfig
from ..interfaces import ImageOutput

# Import existing generators
from ai_content_pipeline.generators.unified_text_to_image import UnifiedTextToImageGenerator
from ai_content_pipeline.generators.fal_image_to_image import FALImageToImageGenerator


class ImageAdapterConfig(AdapterConfig):
    """Configuration for image adapter."""

    model: str = "flux_dev"
    aspect_ratio: str = "1:1"
    num_inference_steps: int = 28
    guidance_scale: float = 3.5
    output_dir: str = "output/vimax/images"


class ImageGeneratorAdapter(BaseAdapter[str, ImageOutput]):
    """
    Adapter for image generation.

    Wraps UnifiedTextToImageGenerator and FALImageToImageGenerator
    to provide a consistent interface for ViMax agents.

    Usage:
        adapter = ImageGeneratorAdapter(config)
        result = await adapter.generate("A samurai warrior")
    """

    # Model mapping to underlying generators
    MODEL_MAP = {
        # FAL models
        "flux_dev": ("fal", "fal-ai/flux/dev"),
        "flux_schnell": ("fal", "fal-ai/flux/schnell"),
        "imagen4": ("fal", "google/imagen-4"),
        "nano_banana_pro": ("fal", "fal-ai/nano-banana-pro"),
        "gpt_image_1_5": ("fal", "fal-ai/gpt-image-1-5"),
        # Replicate models
        "seedream3": ("replicate", "bytedance/seedream-3"),
        "gen4": ("replicate", "runway/gen-4-image"),
    }

    def __init__(self, config: Optional[ImageAdapterConfig] = None):
        super().__init__(config or ImageAdapterConfig())
        self.config: ImageAdapterConfig = self.config
        self._text_to_image: Optional[UnifiedTextToImageGenerator] = None
        self._image_to_image: Optional[FALImageToImageGenerator] = None
        self.logger = logging.getLogger("vimax.adapters.image")

    async def initialize(self) -> bool:
        """Initialize underlying generators."""
        try:
            self._text_to_image = UnifiedTextToImageGenerator()
            self._image_to_image = FALImageToImageGenerator()
            self.logger.info("Image generators initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize image generators: {e}")
            return False

    async def execute(self, prompt: str) -> ImageOutput:
        """
        Generate image from text prompt.

        Args:
            prompt: Text description of desired image

        Returns:
            ImageOutput with generated image path and metadata
        """
        return await self.generate(prompt)

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        output_path: Optional[str] = None,
        **kwargs,
    ) -> ImageOutput:
        """
        Generate image from text prompt.

        Args:
            prompt: Text description of desired image
            model: Model to use (default from config)
            aspect_ratio: Aspect ratio (default from config)
            output_path: Custom output path
            **kwargs: Additional generation parameters

        Returns:
            ImageOutput with generated image path and metadata
        """
        await self.ensure_initialized()

        model = model or self.config.model
        aspect_ratio = aspect_ratio or self.config.aspect_ratio

        # Build generation parameters
        params = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "num_inference_steps": kwargs.get("num_inference_steps", self.config.num_inference_steps),
            "guidance_scale": kwargs.get("guidance_scale", self.config.guidance_scale),
        }

        self.logger.info(f"Generating image with model={model}, prompt={prompt[:50]}...")

        try:
            # Use the unified generator
            result = await self._text_to_image.generate(
                text=prompt,
                model=model,
                **params,
            )

            # Determine output path
            if output_path:
                image_path = output_path
            else:
                output_dir = Path(self.config.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                image_path = str(output_dir / f"{model}_{hash(prompt) & 0xFFFFFFFF}.png")

            # Save if result is URL or base64
            if isinstance(result, dict):
                image_path = result.get("path", result.get("url", image_path))

            return ImageOutput(
                image_path=image_path,
                prompt=prompt,
                model=model,
                width=result.get("width", 1024),
                height=result.get("height", 1024),
                generation_time=result.get("generation_time", 0),
                cost=result.get("cost", self._estimate_cost(model)),
                metadata={"aspect_ratio": aspect_ratio, **kwargs},
            )

        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise

    async def generate_batch(
        self,
        prompts: List[str],
        model: Optional[str] = None,
        **kwargs,
    ) -> List[ImageOutput]:
        """
        Generate multiple images from prompts.

        Args:
            prompts: List of text prompts
            model: Model to use
            **kwargs: Additional parameters

        Returns:
            List of ImageOutput objects
        """
        results = []
        for i, prompt in enumerate(prompts):
            self.logger.info(f"Generating image {i+1}/{len(prompts)}")
            result = await self.generate(prompt, model=model, **kwargs)
            results.append(result)
        return results

    async def edit_image(
        self,
        image_path: str,
        prompt: str,
        model: str = "flux_kontext",
        **kwargs,
    ) -> ImageOutput:
        """
        Edit existing image with prompt.

        Args:
            image_path: Path to source image
            prompt: Edit instructions
            model: Image-to-image model
            **kwargs: Additional parameters

        Returns:
            ImageOutput with edited image
        """
        await self.ensure_initialized()

        self.logger.info(f"Editing image: {image_path}")

        result = await self._image_to_image.generate(
            image_path=image_path,
            prompt=prompt,
            model=model,
            **kwargs,
        )

        return ImageOutput(
            image_path=result.get("path", ""),
            prompt=prompt,
            model=model,
            metadata={"source_image": image_path, **kwargs},
        )

    def _estimate_cost(self, model: str) -> float:
        """Estimate generation cost based on model."""
        costs = {
            "flux_dev": 0.003,
            "flux_schnell": 0.001,
            "imagen4": 0.004,
            "nano_banana_pro": 0.002,
            "gpt_image_1_5": 0.003,
            "seedream3": 0.003,
            "gen4": 0.08,
        }
        return costs.get(model, 0.003)


# Convenience function
async def generate_image(prompt: str, model: str = "flux_dev", **kwargs) -> ImageOutput:
    """Quick function to generate a single image."""
    adapter = ImageGeneratorAdapter(ImageAdapterConfig(model=model))
    return await adapter.generate(prompt, **kwargs)
```

### Unit Tests

**File**: `tests/unit/vimax/test_adapters.py`

```python
"""
Tests for ViMax adapters.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai_content_platform.vimax.adapters.image_adapter import (
    ImageGeneratorAdapter,
    ImageAdapterConfig,
    generate_image,
)
from ai_content_platform.vimax.interfaces import ImageOutput


class TestImageGeneratorAdapter:
    """Tests for ImageGeneratorAdapter."""

    @pytest.fixture
    def adapter_config(self):
        return ImageAdapterConfig(
            model="flux_dev",
            output_dir="/tmp/vimax_test",
        )

    @pytest.fixture
    def mock_generator(self):
        mock = AsyncMock()
        mock.generate.return_value = {
            "path": "/tmp/test_image.png",
            "width": 1024,
            "height": 1024,
            "generation_time": 5.0,
        }
        return mock

    @pytest.mark.asyncio
    async def test_initialize(self, adapter_config):
        """Test adapter initialization."""
        with patch('ai_content_platform.vimax.adapters.image_adapter.UnifiedTextToImageGenerator'):
            adapter = ImageGeneratorAdapter(adapter_config)
            result = await adapter.initialize()
            assert result is True
            assert adapter._initialized is True

    @pytest.mark.asyncio
    async def test_generate_image(self, adapter_config, mock_generator):
        """Test image generation."""
        adapter = ImageGeneratorAdapter(adapter_config)
        adapter._text_to_image = mock_generator
        adapter._initialized = True

        result = await adapter.generate("A samurai warrior")

        assert isinstance(result, ImageOutput)
        assert result.prompt == "A samurai warrior"
        mock_generator.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_batch(self, adapter_config, mock_generator):
        """Test batch image generation."""
        adapter = ImageGeneratorAdapter(adapter_config)
        adapter._text_to_image = mock_generator
        adapter._initialized = True

        prompts = ["prompt 1", "prompt 2", "prompt 3"]
        results = await adapter.generate_batch(prompts)

        assert len(results) == 3
        assert all(isinstance(r, ImageOutput) for r in results)

    def test_estimate_cost(self, adapter_config):
        """Test cost estimation."""
        adapter = ImageGeneratorAdapter(adapter_config)

        assert adapter._estimate_cost("flux_dev") == 0.003
        assert adapter._estimate_cost("flux_schnell") == 0.001
        assert adapter._estimate_cost("unknown") == 0.003  # default
```

### Acceptance Criteria
- [ ] Adapter wraps existing generators
- [ ] All models in MODEL_MAP work
- [ ] Batch generation works
- [ ] Cost estimation accurate
- [ ] Tests pass

---

## Subtask 2.2: VideoGeneratorAdapter

**Estimated Time**: 3-4 hours

### Description
Create an adapter for video generation that wraps FAL image-to-video generators.

### Target File
```
packages/core/ai_content_platform/vimax/adapters/video_adapter.py
```

### Implementation

```python
"""
Video Generator Adapter for ViMax agents.

Wraps existing video generators (FAL Kling, Veo, etc.) to provide
a consistent interface for ViMax agents.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

from .base import BaseAdapter, AdapterConfig
from ..interfaces import VideoOutput, ImageOutput

# Import existing generators
from ai_content_pipeline.generators.fal_image_to_video import FALImageToVideoGenerator


class VideoAdapterConfig(AdapterConfig):
    """Configuration for video adapter."""

    model: str = "kling"
    duration: float = 5.0
    fps: int = 24
    output_dir: str = "output/vimax/videos"


class VideoGeneratorAdapter(BaseAdapter[Dict[str, Any], VideoOutput]):
    """
    Adapter for video generation.

    Wraps FALImageToVideoGenerator to provide a consistent interface
    for ViMax agents.

    Usage:
        adapter = VideoGeneratorAdapter(config)
        result = await adapter.generate(
            image_path="input.png",
            prompt="Character walking forward"
        )
    """

    # Model mapping
    MODEL_MAP = {
        "kling": "fal-ai/kling-video/v1/standard/image-to-video",
        "kling_2_1": "fal-ai/kling-video/v2.1/standard/image-to-video",
        "kling_2_6_pro": "fal-ai/kling-video/v2.6/pro/image-to-video",
        "veo3": "google/veo-3",
        "veo3_fast": "google/veo-3-fast",
        "hailuo": "fal-ai/hailuo/image-to-video",
        "grok_imagine": "fal-ai/grok/imagine",
    }

    def __init__(self, config: Optional[VideoAdapterConfig] = None):
        super().__init__(config or VideoAdapterConfig())
        self.config: VideoAdapterConfig = self.config
        self._generator: Optional[FALImageToVideoGenerator] = None
        self.logger = logging.getLogger("vimax.adapters.video")

    async def initialize(self) -> bool:
        """Initialize underlying generator."""
        try:
            self._generator = FALImageToVideoGenerator()
            self.logger.info("Video generator initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize video generator: {e}")
            return False

    async def execute(self, input_data: Dict[str, Any]) -> VideoOutput:
        """Execute video generation."""
        return await self.generate(**input_data)

    async def generate(
        self,
        image_path: str,
        prompt: str,
        model: Optional[str] = None,
        duration: Optional[float] = None,
        output_path: Optional[str] = None,
        **kwargs,
    ) -> VideoOutput:
        """
        Generate video from image and prompt.

        Args:
            image_path: Path to source image
            prompt: Motion/animation description
            model: Video model to use
            duration: Video duration in seconds
            output_path: Custom output path
            **kwargs: Additional parameters

        Returns:
            VideoOutput with generated video path and metadata
        """
        await self.ensure_initialized()

        model = model or self.config.model
        duration = duration or self.config.duration

        self.logger.info(f"Generating video: model={model}, duration={duration}s")

        try:
            # Build parameters
            params = {
                "image_path": image_path,
                "prompt": prompt,
                "duration": duration,
                **kwargs,
            }

            # Use underlying generator
            result = await self._generator.generate(
                model=model,
                **params,
            )

            # Determine output path
            if output_path:
                video_path = output_path
            else:
                output_dir = Path(self.config.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                video_path = result.get("path", str(output_dir / f"{model}_{hash(prompt) & 0xFFFFFFFF}.mp4"))

            return VideoOutput(
                video_path=video_path,
                source_image=image_path,
                prompt=prompt,
                model=model,
                duration=duration,
                width=result.get("width", 1280),
                height=result.get("height", 720),
                fps=result.get("fps", self.config.fps),
                generation_time=result.get("generation_time", 0),
                cost=result.get("cost", self._estimate_cost(model, duration)),
                metadata=kwargs,
            )

        except Exception as e:
            self.logger.error(f"Video generation failed: {e}")
            raise

    async def generate_from_images(
        self,
        images: List[ImageOutput],
        prompts: List[str],
        model: Optional[str] = None,
        **kwargs,
    ) -> List[VideoOutput]:
        """
        Generate videos from multiple images.

        Args:
            images: List of ImageOutput objects
            prompts: List of prompts (one per image)
            model: Video model to use
            **kwargs: Additional parameters

        Returns:
            List of VideoOutput objects
        """
        if len(images) != len(prompts):
            raise ValueError("Number of images must match number of prompts")

        results = []
        for i, (img, prompt) in enumerate(zip(images, prompts)):
            self.logger.info(f"Generating video {i+1}/{len(images)}")
            result = await self.generate(
                image_path=img.image_path,
                prompt=prompt,
                model=model,
                **kwargs,
            )
            results.append(result)

        return results

    async def concatenate_videos(
        self,
        videos: List[VideoOutput],
        output_path: str,
    ) -> VideoOutput:
        """
        Concatenate multiple videos into one.

        Args:
            videos: List of videos to concatenate
            output_path: Output path for final video

        Returns:
            VideoOutput for concatenated video
        """
        import subprocess

        # Create concat file
        concat_file = Path(output_path).parent / "concat_list.txt"
        with open(concat_file, "w") as f:
            for video in videos:
                f.write(f"file '{video.video_path}'\n")

        # Run ffmpeg
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            output_path,
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        # Cleanup
        concat_file.unlink()

        total_duration = sum(v.duration for v in videos)
        total_cost = sum(v.cost for v in videos)

        return VideoOutput(
            video_path=output_path,
            duration=total_duration,
            cost=total_cost,
            metadata={"source_videos": [v.video_path for v in videos]},
        )

    def _estimate_cost(self, model: str, duration: float) -> float:
        """Estimate generation cost based on model and duration."""
        per_second_costs = {
            "kling": 0.03,
            "kling_2_1": 0.03,
            "kling_2_6_pro": 0.06,
            "veo3": 0.10,
            "veo3_fast": 0.06,
            "hailuo": 0.02,
            "grok_imagine": 0.05,
        }
        return per_second_costs.get(model, 0.03) * duration


# Convenience function
async def generate_video(
    image_path: str,
    prompt: str,
    model: str = "kling",
    duration: float = 5.0,
    **kwargs,
) -> VideoOutput:
    """Quick function to generate a single video."""
    adapter = VideoGeneratorAdapter(VideoAdapterConfig(model=model, duration=duration))
    return await adapter.generate(image_path, prompt, **kwargs)
```

### Acceptance Criteria
- [ ] Adapter wraps FAL video generators
- [ ] All models in MODEL_MAP work
- [ ] Batch video generation works
- [ ] Video concatenation works
- [ ] Cost estimation accurate
- [ ] Tests pass

---

## Subtask 2.3: LLMAdapter

**Estimated Time**: 3-4 hours

### Description
Create an adapter for LLM calls using litellm for unified access to multiple providers.

### Target File
```
packages/core/ai_content_platform/vimax/adapters/llm_adapter.py
```

### Implementation

```python
"""
LLM Adapter for ViMax agents.

Uses litellm for unified access to multiple LLM providers:
- OpenRouter (Claude, GPT-4, etc.)
- OpenAI
- Anthropic
- Google (Gemini)
"""

from typing import Optional, Dict, Any, List, Union
import logging
import json

from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseAdapter, AdapterConfig

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


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
    usage: Dict[str, int] = {}
    cost: float = 0.0


class LLMAdapter(BaseAdapter[List[Message], LLMResponse]):
    """
    Adapter for LLM calls.

    Uses litellm for unified access to multiple providers.

    Usage:
        adapter = LLMAdapter(config)
        response = await adapter.chat([
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Write a short story."),
        ])
    """

    # Common model aliases
    MODEL_ALIASES = {
        "claude-3.5-sonnet": "openrouter/anthropic/claude-3.5-sonnet",
        "claude-3-opus": "openrouter/anthropic/claude-3-opus",
        "gpt-4": "openrouter/openai/gpt-4-turbo",
        "gpt-4o": "openrouter/openai/gpt-4o",
        "gemini-pro": "openrouter/google/gemini-pro",
    }

    def __init__(self, config: Optional[LLMAdapterConfig] = None):
        if not LITELLM_AVAILABLE:
            raise ImportError("litellm is required. Install with: pip install litellm")

        super().__init__(config or LLMAdapterConfig())
        self.config: LLMAdapterConfig = self.config
        self.logger = logging.getLogger("vimax.adapters.llm")

    async def initialize(self) -> bool:
        """Initialize LLM adapter."""
        # litellm doesn't require explicit initialization
        self.logger.info(f"LLM adapter initialized with model: {self.config.model}")
        return True

    async def execute(self, messages: List[Message]) -> LLMResponse:
        """Execute LLM call."""
        return await self.chat(messages)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def chat(
        self,
        messages: List[Union[Message, Dict[str, str]]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Send chat messages to LLM.

        Args:
            messages: List of messages
            model: Model to use (default from config)
            temperature: Temperature (default from config)
            max_tokens: Max tokens (default from config)
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated content
        """
        await self.ensure_initialized()

        # Resolve model alias
        model = model or self.config.model
        model = self.MODEL_ALIASES.get(model, model)

        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        # Convert messages to dict format
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, Message):
                formatted_messages.append({"role": msg.role, "content": msg.content})
            else:
                formatted_messages.append(msg)

        self.logger.debug(f"Calling LLM: model={model}, messages={len(formatted_messages)}")

        try:
            response = await litellm.acompletion(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.config.timeout,
                **kwargs,
            )

            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            # Estimate cost
            cost = self._estimate_cost(model, usage)

            return LLMResponse(
                content=content,
                model=model,
                usage=usage,
                cost=cost,
            )

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    async def chat_with_structured_output(
        self,
        messages: List[Message],
        output_schema: type[BaseModel],
        **kwargs,
    ) -> BaseModel:
        """
        Chat with structured JSON output.

        Args:
            messages: Chat messages
            output_schema: Pydantic model for output
            **kwargs: Additional parameters

        Returns:
            Parsed Pydantic model instance
        """
        # Add schema instruction to system message
        schema_instruction = f"""
You must respond with valid JSON matching this schema:
{json.dumps(output_schema.model_json_schema(), indent=2)}

Respond ONLY with the JSON, no other text.
"""

        # Prepend or append schema instruction
        if messages and messages[0].role == "system":
            messages[0] = Message(
                role="system",
                content=messages[0].content + "\n\n" + schema_instruction,
            )
        else:
            messages.insert(0, Message(role="system", content=schema_instruction))

        response = await self.chat(messages, **kwargs)

        # Parse JSON response
        try:
            data = json.loads(response.content)
            return output_schema(**data)
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse structured output: {e}")
            raise ValueError(f"LLM response was not valid JSON: {response.content[:200]}")

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Simple text generation.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))

        response = await self.chat(messages, **kwargs)
        return response.content

    def _estimate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """Estimate cost based on model and token usage."""
        # Approximate costs per 1K tokens (input, output)
        costs = {
            "openrouter/anthropic/claude-3.5-sonnet": (0.003, 0.015),
            "openrouter/anthropic/claude-3-opus": (0.015, 0.075),
            "openrouter/openai/gpt-4-turbo": (0.01, 0.03),
            "openrouter/openai/gpt-4o": (0.005, 0.015),
            "openrouter/google/gemini-pro": (0.00025, 0.0005),
        }

        if model in costs:
            input_cost, output_cost = costs[model]
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            return (prompt_tokens * input_cost + completion_tokens * output_cost) / 1000

        return 0.0


# Convenience functions
async def chat(
    messages: List[Union[Message, Dict[str, str]]],
    model: str = "claude-3.5-sonnet",
    **kwargs,
) -> str:
    """Quick function for LLM chat."""
    adapter = LLMAdapter(LLMAdapterConfig(model=model))
    response = await adapter.chat(messages, **kwargs)
    return response.content


async def generate(prompt: str, model: str = "claude-3.5-sonnet", **kwargs) -> str:
    """Quick function for text generation."""
    adapter = LLMAdapter(LLMAdapterConfig(model=model))
    return await adapter.generate_text(prompt, **kwargs)
```

### Acceptance Criteria
- [ ] litellm integration works
- [ ] Multiple providers supported
- [ ] Structured output parsing works
- [ ] Retry logic implemented
- [ ] Cost estimation accurate
- [ ] Tests pass

---

## Subtask 2.4: Update Adapter Exports

**Estimated Time**: 30 minutes

### File: `packages/core/ai_content_platform/vimax/adapters/__init__.py`

```python
"""
ViMax Adapters

Bridges between agents and underlying services.
"""

from .base import BaseAdapter, AdapterConfig
from .image_adapter import (
    ImageGeneratorAdapter,
    ImageAdapterConfig,
    generate_image,
)
from .video_adapter import (
    VideoGeneratorAdapter,
    VideoAdapterConfig,
    generate_video,
)
from .llm_adapter import (
    LLMAdapter,
    LLMAdapterConfig,
    Message,
    LLMResponse,
    chat,
    generate,
)

__all__ = [
    # Base
    "BaseAdapter",
    "AdapterConfig",
    # Image
    "ImageGeneratorAdapter",
    "ImageAdapterConfig",
    "generate_image",
    # Video
    "VideoGeneratorAdapter",
    "VideoAdapterConfig",
    "generate_video",
    # LLM
    "LLMAdapter",
    "LLMAdapterConfig",
    "Message",
    "LLMResponse",
    "chat",
    "generate",
]
```

---

## Phase 2 Completion Checklist

- [ ] **2.1** ImageGeneratorAdapter implemented
- [ ] **2.2** VideoGeneratorAdapter implemented
- [ ] **2.3** LLMAdapter implemented
- [ ] **2.4** Exports updated

### Verification Commands

```bash
# Test imports
python -c "from ai_content_platform.vimax.adapters import *; print('Adapters OK')"

# Run adapter tests
pytest tests/unit/vimax/test_adapters.py -v

# Quick integration test
python -c "
import asyncio
from ai_content_platform.vimax.adapters import ImageGeneratorAdapter

async def test():
    adapter = ImageGeneratorAdapter()
    await adapter.initialize()
    print('Adapter initialized successfully')

asyncio.run(test())
"
```

---

*Previous Phase*: [PHASE_1_INFRASTRUCTURE.md](./PHASE_1_INFRASTRUCTURE.md)
*Next Phase*: [PHASE_3_AGENTS.md](./PHASE_3_AGENTS.md)
