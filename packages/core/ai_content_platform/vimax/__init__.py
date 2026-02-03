"""
ViMax Integration Module

Novel-to-video pipeline integration with character consistency,
storyboard generation, and multi-agent collaboration.

This module provides:
- Character extraction and portrait generation
- Screenplay/script generation from ideas
- Visual storyboard creation
- Video generation from storyboards
- End-to-end pipelines (Idea2Video, Script2Video, Novel2Movie)

Usage:
    from ai_content_platform.vimax import Idea2VideoPipeline

    pipeline = Idea2VideoPipeline()
    result = await pipeline.run("A samurai's journey at sunrise")
"""

__version__ = "1.0.0"

# Import interfaces
from .interfaces import (
    CharacterInNovel,
    CharacterPortrait,
    ShotDescription,
    Scene,
    Storyboard,
    ImageOutput,
    VideoOutput,
    PipelineOutput,
)

# Import base classes
from .agents import BaseAgent, AgentConfig, AgentResult
from .adapters import BaseAdapter, AdapterConfig

__all__ = [
    # Version
    "__version__",
    # Interfaces
    "CharacterInNovel",
    "CharacterPortrait",
    "ShotDescription",
    "Scene",
    "Storyboard",
    "ImageOutput",
    "VideoOutput",
    "PipelineOutput",
    # Base classes
    "BaseAgent",
    "AgentConfig",
    "AgentResult",
    "BaseAdapter",
    "AdapterConfig",
]
