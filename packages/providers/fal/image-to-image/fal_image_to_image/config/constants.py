"""Constants and configuration for FAL Image-to-Image models. Derived from central registry."""

from typing import Dict, List, Literal
from ai_content_pipeline.registry import ModelRegistry

import ai_content_pipeline.registry_data  # side-effect: registers models

_CATEGORY = "image_to_image"
_models = ModelRegistry.list_by_category(_CATEGORY)
_model_keys = ModelRegistry.keys_for_category(_CATEGORY)

ModelType = Literal[tuple(_model_keys)]  # type: ignore
SUPPORTED_MODELS = _model_keys
MODEL_ENDPOINTS = {m.key: m.endpoint for m in _models}
MODEL_DISPLAY_NAMES = {m.key: m.name for m in _models}
DEFAULT_VALUES = {m.key: m.defaults for m in _models}
MODEL_INFO = {
    m.key: {
        "model_name": m.name,
        "description": m.description,
        "features": m.features,
    }
    for m in _models
}

# Aspect ratios - common sets used by model classes
AspectRatio = Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]
ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]
KONTEXT_MULTI_ASPECT_RATIOS = ["21:9", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "9:21"]
NANO_BANANA_ASPECT_RATIOS = [
    "auto", "21:9", "16:9", "3:2", "4:3", "5:4",
    "1:1", "4:5", "3:4", "2:3", "9:16"
]

# Reframe endpoints (static, model-specific API feature)
REFRAME_ENDPOINTS = {
    "photon": "fal-ai/luma-photon/flash/reframe",
    "photon_base": "fal-ai/luma-photon/reframe"
}

# Resolution and format options (static)
RESOLUTIONS = ["1K", "2K", "4K"]
OUTPUT_FORMATS = ["jpeg", "png", "webp"]

# Parameter ranges (static validation constraints)
PHOTON_STRENGTH_RANGE = (0.0, 1.0)
KONTEXT_INFERENCE_STEPS_RANGE = (1, 50)
KONTEXT_GUIDANCE_SCALE_RANGE = (1.0, 20.0)
SEEDEDIT_GUIDANCE_SCALE_RANGE = (0.0, 1.0)
