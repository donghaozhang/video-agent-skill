"""
ViMax Adapters

Bridges between agents and underlying services.
"""

from .base import BaseAdapter, AdapterConfig
from .image_adapter import (
    ImageGeneratorAdapter,
    ImageAdapterConfig,
    ImageOutput,
    generate_image,
)
from .video_adapter import (
    VideoGeneratorAdapter,
    VideoAdapterConfig,
    VideoOutput,
    generate_video,
)
from .llm_adapter import (
    LLMAdapter,
    LLMAdapterConfig,
    LLMResponse,
    Message,
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
    "ImageOutput",
    "generate_image",
    # Video
    "VideoGeneratorAdapter",
    "VideoAdapterConfig",
    "VideoOutput",
    "generate_video",
    # LLM
    "LLMAdapter",
    "LLMAdapterConfig",
    "LLMResponse",
    "Message",
    "chat",
    "generate",
]
