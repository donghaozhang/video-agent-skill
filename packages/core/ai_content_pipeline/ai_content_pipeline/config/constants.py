"""Configuration constants for AI Content Pipeline. Derived from central registry."""

from ai_content_pipeline.registry import ModelRegistry

import ai_content_pipeline.registry_data  # side-effect: registers models

# Supported models for each pipeline step - derived from registry
SUPPORTED_MODELS = ModelRegistry.get_supported_models()

# Pipeline step types (static)
PIPELINE_STEPS = [
    "text_to_image",
    "text_to_video",
    "image_understanding",
    "prompt_generation",
    "image_to_image",
    "image_to_video",
    "text_to_speech",
    "speech_to_text",
    "add_audio",
    "upscale_video",
    "avatar"
]

# Model recommendations based on use case (static - these are editorial choices)
MODEL_RECOMMENDATIONS = {
    "text_to_image": {
        "quality": "flux_dev",
        "speed": "flux_schnell",
        "cost_effective": "seedream_v3",
        "photorealistic": "imagen4",
        "high_resolution": "seedream3",
        "cinematic": "gen4",
        "reference_guided": "gen4"
    },
    "text_to_video": {
        "quality": "sora_2_pro",
        "speed": "veo3_fast",
        "cost_effective": "hailuo_pro",
        "balanced": "sora_2",
        "long_duration": "sora_2",
        "cinematic": "veo3",
        "1080p": "sora_2_pro"
    },
    "text_to_speech": {
        "quality": "elevenlabs_v3",
        "speed": "elevenlabs_turbo",
        "cost_effective": "elevenlabs",
        "professional": "elevenlabs"
    },
    "image_understanding": {
        "basic": "gemini_describe",
        "detailed": "gemini_detailed",
        "classification": "gemini_classify",
        "objects": "gemini_objects",
        "text_extraction": "gemini_ocr",
        "artistic": "gemini_composition",
        "interactive": "gemini_qa"
    },
    "prompt_generation": {
        "general": "openrouter_video_prompt",
        "cinematic": "openrouter_video_cinematic",
        "realistic": "openrouter_video_realistic",
        "artistic": "openrouter_video_artistic",
        "dramatic": "openrouter_video_dramatic"
    },
    "image_to_image": {
        "quality": "photon_base",
        "speed": "photon_flash",
        "cost_effective": "photon_flash",
        "creative": "photon_flash",
        "precise": "seededit_v3",
        "upscale": "clarity_upscaler"
    },
    "image_to_video": {
        "quality": "veo3",
        "speed": "hailuo",
        "cost_effective": "hailuo",
        "balanced": "veo3_fast",
        "cinematic": "veo3"
    },
    "avatar": {
        "quality": "omnihuman_v1_5",
        "speed": "fabric_1_0_fast",
        "cost_effective": "fabric_1_0",
        "lipsync": "omnihuman_v1_5",
        "text_to_avatar": "fabric_1_0_text",
        "character_consistency": "kling_ref_to_video",
        "style_transfer": "kling_v2v_reference",
        "video_editing": "kling_v2v_edit",
        "motion_transfer": "kling_motion_control"
    },
    "speech_to_text": {
        "quality": "scribe_v2",
        "speed": "scribe_v2",
        "diarization": "scribe_v2",
        "multilingual": "scribe_v2"
    }
}

# Cost estimates (USD) - derived from registry
COST_ESTIMATES = ModelRegistry.get_cost_estimates()

# Processing time estimates (seconds) - derived from registry
PROCESSING_TIME_ESTIMATES = ModelRegistry.get_processing_times()

# File format mappings (static)
SUPPORTED_FORMATS = {
    "image": [".jpg", ".jpeg", ".png", ".webp"],
    "video": [".mp4", ".mov", ".avi", ".webm"],
    "audio": [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
}

# Default configuration (static)
DEFAULT_CHAIN_CONFIG = {
    "steps": [
        {
            "type": "text_to_image",
            "model": "flux_dev",
            "params": {
                "aspect_ratio": "16:9",
                "style": "cinematic"
            }
        },
        {
            "type": "image_to_video",
            "model": "veo3",
            "params": {
                "duration": 8,
                "motion_level": "medium"
            }
        }
    ],
    "output_dir": "output",
    "temp_dir": "temp",
    "cleanup_temp": True
}
