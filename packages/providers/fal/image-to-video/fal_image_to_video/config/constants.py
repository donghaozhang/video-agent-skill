"""
Constants and configuration for FAL Image-to-Video models.
Derived from central registry - DO NOT hardcode values here.
"""

from typing import Literal, List
from ai_content_pipeline.registry import ModelRegistry

import ai_content_pipeline.registry_data  # noqa: F401

_CATEGORY = "image_to_video"
_models = ModelRegistry.list_by_category(_CATEGORY)

# Use provider_key for backward compatibility (some models have different
# registry keys to avoid collisions with text-to-video variants)
_model_keys = [m.provider_key for m in _models]

ModelType = Literal[tuple(_model_keys)]  # type: ignore
SUPPORTED_MODELS: List[str] = _model_keys
MODEL_ENDPOINTS = {m.provider_key: m.endpoint for m in _models}
MODEL_DISPLAY_NAMES = {m.provider_key: m.name for m in _models}
MODEL_PRICING = {m.provider_key: m.pricing for m in _models}
DURATION_OPTIONS = {m.provider_key: m.duration_options for m in _models}
RESOLUTION_OPTIONS = {m.provider_key: m.resolutions for m in _models}
ASPECT_RATIO_OPTIONS = {m.provider_key: m.aspect_ratios for m in _models if m.aspect_ratios}
DEFAULT_VALUES = {m.provider_key: m.defaults for m in _models}
MODEL_INFO = {
    m.provider_key: {
        "name": m.name,
        "provider": m.provider,
        "description": m.description,
        "max_duration": m.max_duration,
        "features": m.features,
        "extended_params": m.extended_params,
    }
    for m in _models
}

# Extended feature support - derived from registry
MODEL_EXTENDED_FEATURES = {m.provider_key: m.extended_features for m in _models if m.extended_features}

# API parameter mapping for extended features (static, doesn't change per model)
EXTENDED_PARAM_MAPPING = {
    "start_frame": "image_url",
    "end_frame": {
        "kling_2_1": "tail_image_url",
        "kling_2_6_pro": "tail_image_url",
        "kling_3_standard": "end_image_url",
        "kling_3_pro": "end_image_url",
    },
    "audio_generate": "generate_audio",
}
