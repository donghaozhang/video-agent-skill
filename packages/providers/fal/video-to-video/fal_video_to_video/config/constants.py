"""Constants and configuration for FAL Video to Video models. Derived from central registry."""

from typing import Dict, List, Literal
from ai_content_pipeline.registry import ModelRegistry

import ai_content_pipeline.registry_data  # noqa: F401

# Combine categories since V2V package has audio, upscale, and edit models
_v2v_models = ModelRegistry.list_by_category("video_to_video")
_audio_models = ModelRegistry.list_by_category("add_audio")
_upscale_models = ModelRegistry.list_by_category("upscale_video")
_all_models = _audio_models + _upscale_models + _v2v_models

_model_keys = [m.key for m in _all_models]

ModelType = Literal[tuple(_model_keys)]  # type: ignore
SUPPORTED_MODELS = _model_keys
MODEL_ENDPOINTS = {m.key: m.endpoint for m in _all_models}
MODEL_DISPLAY_NAMES = {m.key: m.name for m in _all_models}
MODEL_INFO = {
    m.key: {
        "model_name": m.name,
        "provider": m.provider,
        "description": m.description,
        "features": m.features,
        "pricing": str(m.pricing),
        "max_duration": m.max_duration,
        "output_format": "mp4",
    }
    for m in _all_models
}
DEFAULT_VALUES = {m.key: m.defaults for m in _all_models}
DURATION_OPTIONS = {m.key: m.duration_options for m in _all_models if m.duration_options}
ASPECT_RATIO_OPTIONS = {m.key: m.aspect_ratios for m in _all_models if m.aspect_ratios}

# File size limits (static)
MAX_VIDEO_SIZE_MB = 100
MAX_VIDEO_DURATION_SECONDS = 300

# Output settings (static)
DEFAULT_OUTPUT_FORMAT = "mp4"
VIDEO_CODECS = {
    "mp4": "libx264",
    "webm": "libvpx",
    "mov": "libx264"
}
