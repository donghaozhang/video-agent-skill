"""
Constants and configuration for FAL Text-to-Video models.
Derived from central registry - DO NOT hardcode values here.
"""

from typing import Literal, List
from ai_content_pipeline.registry import ModelRegistry

# Ensure registry data is loaded
import ai_content_pipeline.registry_data  # noqa: F401

_CATEGORY = "text_to_video"
_models = ModelRegistry.list_by_category(_CATEGORY)

# Model type definitions (for type hints)
_model_keys = ModelRegistry.keys_for_category(_CATEGORY)
ModelType = Literal[tuple(_model_keys)]  # type: ignore

SUPPORTED_MODELS: List[str] = _model_keys

# Model endpoints
MODEL_ENDPOINTS = {m.key: m.endpoint for m in _models}

# Display names
MODEL_DISPLAY_NAMES = {m.key: m.name for m in _models}

# Pricing (USD) - preserves original nested dict structure
MODEL_PRICING = {m.key: m.pricing for m in _models}

# Duration options per model
DURATION_OPTIONS = {m.key: m.duration_options for m in _models}

# Resolution options per model
RESOLUTION_OPTIONS = {m.key: m.resolutions for m in _models}

# Aspect ratio options
ASPECT_RATIO_OPTIONS = {m.key: m.aspect_ratios for m in _models}

# Default values per model
DEFAULT_VALUES = {m.key: m.defaults for m in _models}

# Model info for documentation
MODEL_INFO = {
    m.key: {
        "name": m.name,
        "provider": m.provider,
        "description": m.description,
        "max_duration": m.max_duration,
        "features": m.features,
    }
    for m in _models
}
