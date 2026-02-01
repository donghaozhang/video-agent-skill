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
    "kling_motion_control": "fal-ai/kling-video/v2.6/standard/motion-control",
    "multitalk": "fal-ai/ai-avatar/multi",
    "grok_video_edit": "xai/grok-imagine-video/edit-video",
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
    "kling_motion_control": "Kling v2.6 Motion Control",
    "multitalk": "AI Avatar Multi (FAL)",
    "grok_video_edit": "xAI Grok Video Edit",
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
    "kling_motion_control": {"per_second": 0.06},
    "multitalk": {"base": 0.10, "720p_multiplier": 2.0, "extended_frames_multiplier": 1.25},
    "grok_video_edit": {"input_per_second": 0.01, "output_per_second": 0.05},
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
    "kling_motion_control": {
        "character_orientation": "video",
        "keep_original_sound": True,
    },
    "multitalk": {
        "num_frames": 81,
        "resolution": "480p",
        "acceleration": "regular",
    },
    "grok_video_edit": {
        "resolution": "auto",
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
    "kling_motion_control": [],  # Uses character_orientation instead
    "multitalk": ["480p", "720p"],
    "grok_video_edit": ["auto", "480p", "720p"],
}

# Supported aspect ratios
SUPPORTED_ASPECT_RATIOS = {
    "kling_ref_to_video": ["16:9", "9:16", "1:1"],
    "kling_v2v_reference": ["16:9", "9:16", "1:1"],
    "kling_v2v_edit": ["16:9", "9:16", "1:1"],
    "kling_motion_control": [],  # Determined by input image/video
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
    "kling_motion_control": {"video": 30, "image": 10},
    "grok_video_edit": 8,  # Input truncated to 8 seconds
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
    "kling_motion_control": 60,
    "multitalk": 60,
    "grok_video_edit": 45,
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
    "kling_motion_control": {
        "required": ["image_url", "video_url"],
        "optional": ["character_orientation", "keep_original_sound", "prompt"],
    },
    "multitalk": {
        "required": ["image_url", "first_audio_url", "prompt"],
        "optional": ["second_audio_url", "num_frames", "resolution", "seed", "acceleration", "use_only_first_audio"],
    },
    "grok_video_edit": {
        "required": ["video_url", "prompt"],
        "optional": ["resolution"],
    },
}

# Model categories
MODEL_CATEGORIES = {
    "avatar_lipsync": ["omnihuman_v1_5", "fabric_1_0", "fabric_1_0_fast", "fabric_1_0_text"],
    "reference_to_video": ["kling_ref_to_video"],
    "video_to_video": ["kling_v2v_reference", "kling_v2v_edit", "grok_video_edit"],
    "motion_transfer": ["kling_motion_control"],
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
    "motion_transfer": "kling_motion_control",
    "dance_video": "kling_motion_control",
    "cost_effective": "fabric_1_0",
    "conversation": "multitalk",
    "multi_person": "multitalk",
    "podcast": "multitalk",
    "colorize": "grok_video_edit",
    "video_transform": "grok_video_edit",
}
