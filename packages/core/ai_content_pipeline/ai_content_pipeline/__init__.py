"""
AI Content Pipeline - Unified Content Generation Chain System

This package provides a seamless pipeline for chaining multiple AI operations:
Text → Image → Video → Audio Enhancement → Video Upscaling

Features:
- Multi-model text-to-image generation with smart selection
- Seamless integration with existing FAL AI modules
- Cost estimation and optimization
- Progress tracking and error handling
- YAML/JSON configuration system
"""

__version__ = "1.0.18"
__author__ = "AI Content Pipeline Team"

from .pipeline.manager import AIPipelineManager
from .models.text_to_image import UnifiedTextToImageGenerator
from .pipeline.chain import ContentCreationChain
from .config.constants import SUPPORTED_MODELS, PIPELINE_STEPS

__all__ = [
    "AIPipelineManager",
    "UnifiedTextToImageGenerator", 
    "ContentCreationChain",
    "SUPPORTED_MODELS",
    "PIPELINE_STEPS"
]