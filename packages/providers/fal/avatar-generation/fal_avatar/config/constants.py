"""Constants for FAL avatar generation models."""

# Model endpoints
MODEL_ENDPOINTS = {
    "omnihuman_v1_5": "fal-ai/bytedance/omnihuman/v1.5",
    "fabric_1_0": "veed/fabric-1.0",
    "fabric_1_0_fast": "veed/fabric-1.0/fast",
    "fabric_1_0_text": "veed/fabric-1.0/text",
    "kling_ref_to_video": "fal-ai/kling-video/o1/standard/reference-to-video",
    "kling_v2v_reference": "fal-ai/kling-video/o1/standard/video-to-video/reference",
    "kling_v2v_edit": "fal-ai/kling-video/o1/standard/video-to-video/edit",
    "multitalk": "fal-ai/ai-avatar/multi",
}

# Display names for UI/CLI
MODEL_DISPLAY_NAMES = {
    "omnihuman_v1_5": "OmniHuman v1.5 (ByteDance)",
    "fabric_1_0": "VEED Fabric 1.0",
    "fabric_1_0_fast": "VEED Fabric 1.0 Fast",
    "fabric_1_0_text": "VEED Fabric 1.0 Text-to-Speech",
    "kling_ref_to_video": "Kling O1 Reference-to-Video",
    "kling_v2v_reference": "Kling O1 V2V Reference",
    "kling_v2v_edit": "Kling O1 V2V Edit",
    "multitalk": "AI Avatar Multi (FAL)",
}

# Pricing per second
MODEL_PRICING = {
    "omnihuman_v1_5": {"per_second": 0.16},
    "fabric_1_0": {"480p": 0.08, "720p": 0.15},
    "fabric_1_0_fast": {"480p": 0.10, "720p": 0.19},
    "fabric_1_0_text": {"480p": 0.08, "720p": 0.15},
    "kling_ref_to_video": {"per_second": 0.112},
    "kling_v2v_reference": {"per_second": 0.168},
    "kling_v2v_edit": {"per_second": 0.168},
    "multitalk": {"base": 0.10, "720p_multiplier": 2.0, "extended_frames_multiplier": 1.25},
}

# Default values
MODEL_DEFAULTS = {
    "omnihuman_v1_5": {
        "resolution": "1080p",
        "turbo_mode": False,
    },
    "fabric_1_0": {
        "resolution": "720p",
    },
    "fabric_1_0_fast": {
        "resolution": "720p",
    },
    "fabric_1_0_text": {
        "resolution": "720p",
    },
    "kling_ref_to_video": {
        "duration": "5",
        "aspect_ratio": "16:9",
    },
    "kling_v2v_reference": {
        "duration": "5",
        "aspect_ratio": "16:9",
    },
    "kling_v2v_edit": {
        "aspect_ratio": "16:9",
    },
    "multitalk": {
        "num_frames": 81,
        "resolution": "480p",
        "acceleration": "regular",
    },
}

# Supported resolutions per model
SUPPORTED_RESOLUTIONS = {
    "omnihuman_v1_5": ["720p", "1080p"],
    "fabric_1_0": ["480p", "720p"],
    "fabric_1_0_fast": ["480p", "720p"],
    "fabric_1_0_text": ["480p", "720p"],
    "kling_ref_to_video": [],  # Uses aspect_ratio instead
    "kling_v2v_reference": [],
    "kling_v2v_edit": [],
    "multitalk": ["480p", "720p"],
}

# Supported aspect ratios
SUPPORTED_ASPECT_RATIOS = {
    "kling_ref_to_video": ["16:9", "9:16", "1:1"],
    "kling_v2v_reference": ["16:9", "9:16", "1:1"],
    "kling_v2v_edit": ["16:9", "9:16", "1:1"],
}

# Max durations (seconds)
MAX_DURATIONS = {
    "omnihuman_v1_5": {"1080p": 30, "720p": 60},
    "fabric_1_0": 120,
    "fabric_1_0_fast": 120,
    "fabric_1_0_text": 120,
    "kling_ref_to_video": 10,
    "kling_v2v_reference": 10,
    "kling_v2v_edit": 10,
}

# Processing time estimates (seconds)
PROCESSING_TIME_ESTIMATES = {
    "omnihuman_v1_5": 60,
    "fabric_1_0": 45,
    "fabric_1_0_fast": 30,
    "fabric_1_0_text": 45,
    "kling_ref_to_video": 45,
    "kling_v2v_reference": 30,
    "kling_v2v_edit": 30,
    "multitalk": 60,
}

# Input requirements
INPUT_REQUIREMENTS = {
    "omnihuman_v1_5": {
        "required": ["image_url", "audio_url"],
        "optional": ["prompt", "turbo_mode", "resolution"],
    },
    "fabric_1_0": {
        "required": ["image_url", "audio_url", "resolution"],
        "optional": [],
    },
    "fabric_1_0_fast": {
        "required": ["image_url", "audio_url", "resolution"],
        "optional": [],
    },
    "fabric_1_0_text": {
        "required": ["image_url", "text", "resolution"],
        "optional": ["voice_description"],
    },
    "kling_ref_to_video": {
        "required": ["prompt", "reference_images"],
        "optional": ["duration", "aspect_ratio", "audio_url", "face_id"],
    },
    "kling_v2v_reference": {
        "required": ["prompt", "video_url"],
        "optional": ["duration", "aspect_ratio", "audio_url", "face_id"],
    },
    "kling_v2v_edit": {
        "required": ["video_url", "prompt"],
        "optional": ["mask_url"],
    },
    "multitalk": {
        "required": ["image_url", "first_audio_url", "prompt"],
        "optional": ["second_audio_url", "num_frames", "resolution", "seed", "acceleration", "use_only_first_audio"],
    },
}

# Model categories
MODEL_CATEGORIES = {
    "avatar_lipsync": ["omnihuman_v1_5", "fabric_1_0", "fabric_1_0_fast", "fabric_1_0_text"],
    "reference_to_video": ["kling_ref_to_video"],
    "video_to_video": ["kling_v2v_reference", "kling_v2v_edit"],
    "conversational": ["multitalk"],
}

# Model recommendations
MODEL_RECOMMENDATIONS = {
    "quality": "omnihuman_v1_5",
    "speed": "fabric_1_0_fast",
    "text_to_avatar": "fabric_1_0_text",
    "character_consistency": "kling_ref_to_video",
    "style_transfer": "kling_v2v_reference",
    "video_editing": "kling_v2v_edit",
    "cost_effective": "fabric_1_0",
    "conversation": "multitalk",
    "multi_person": "multitalk",
    "podcast": "multitalk",
}
