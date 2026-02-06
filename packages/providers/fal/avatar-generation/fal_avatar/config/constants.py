"""Constants for FAL avatar generation models. Derived from central registry."""

from ai_content_pipeline.registry import ModelRegistry

import ai_content_pipeline.registry_data  # side-effect: registers models

_CATEGORY = "avatar"
_models = ModelRegistry.list_by_category(_CATEGORY)

MODEL_ENDPOINTS = {m.key: m.endpoint for m in _models}
MODEL_DISPLAY_NAMES = {m.key: m.name for m in _models}
MODEL_PRICING = {m.key: m.pricing for m in _models}
MODEL_DEFAULTS = {m.key: m.defaults for m in _models}
SUPPORTED_RESOLUTIONS = {m.key: m.resolutions for m in _models}
SUPPORTED_ASPECT_RATIOS = {m.key: m.aspect_ratios for m in _models if m.aspect_ratios}
# MAX_DURATIONS preserves original dict structure for models with
# orientation-dependent durations (e.g., {"video": 30, "image": 10})
MAX_DURATIONS = {
    m.key: m.model_info.get("max_durations", m.max_duration)
    for m in _models
}
PROCESSING_TIME_ESTIMATES = {m.key: m.processing_time for m in _models}
INPUT_REQUIREMENTS = {m.key: m.input_requirements for m in _models if m.input_requirements}

# Model categories (static grouping within avatar domain)
MODEL_CATEGORIES = {
    "avatar_lipsync": ["omnihuman_v1_5", "fabric_1_0", "fabric_1_0_fast", "fabric_1_0_text"],
    "reference_to_video": ["kling_ref_to_video"],
    "video_to_video": ["kling_v2v_reference", "kling_v2v_edit", "grok_video_edit"],
    "motion_transfer": ["kling_motion_control"],
    "conversational": ["multitalk"],
}

# Model recommendations (static)
MODEL_RECOMMENDATIONS = {
    "quality": "omnihuman_v1_5",
    "speed": "fabric_1_0_fast",
    "text_to_avatar": "fabric_1_0_text",
    "character_consistency": "kling_ref_to_video",
    "style_transfer": "kling_v2v_reference",
    "video_editing": "kling_v2v_edit",
    "motion_transfer": "kling_motion_control",
    "dance_video": "kling_motion_control",
    "cost_effective": "fabric_1_0",
    "conversation": "multitalk",
    "multi_person": "multitalk",
    "podcast": "multitalk",
    "colorize": "grok_video_edit",
    "video_transform": "grok_video_edit",
}
