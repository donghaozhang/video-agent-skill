"""
Constants and configuration for FAL Image-to-Video models.
"""

from typing import Literal, List

# Model type definitions
ModelType = Literal[
    "hailuo",
    "kling_2_1",
    "kling_2_6_pro",
    "seedance_1_5_pro",
    "sora_2",
    "sora_2_pro",
    "veo_3_1_fast"
]

SUPPORTED_MODELS: List[str] = [
    "hailuo",
    "kling_2_1",
    "kling_2_6_pro",
    "seedance_1_5_pro",
    "sora_2",
    "sora_2_pro",
    "veo_3_1_fast"
]

# Model endpoints
MODEL_ENDPOINTS = {
    "hailuo": "fal-ai/minimax/hailuo-02/standard/image-to-video",
    "kling_2_1": "fal-ai/kling-video/v2.1/standard/image-to-video",
    "kling_2_6_pro": "fal-ai/kling-video/v2.6/pro/image-to-video",
    "seedance_1_5_pro": "fal-ai/bytedance/seedance/v1.5/pro/image-to-video",
    "sora_2": "fal-ai/sora-2/image-to-video",
    "sora_2_pro": "fal-ai/sora-2/image-to-video/pro",
    "veo_3_1_fast": "fal-ai/veo3.1/fast/image-to-video"
}

# Display names
MODEL_DISPLAY_NAMES = {
    "hailuo": "MiniMax Hailuo-02",
    "kling_2_1": "Kling Video v2.1",
    "kling_2_6_pro": "Kling Video v2.6 Pro",
    "seedance_1_5_pro": "ByteDance Seedance v1.5 Pro",
    "sora_2": "Sora 2",
    "sora_2_pro": "Sora 2 Pro",
    "veo_3_1_fast": "Veo 3.1 Fast"
}

# Pricing per second (USD)
MODEL_PRICING = {
    "hailuo": 0.05,
    "kling_2_1": 0.05,
    "kling_2_6_pro": 0.10,
    "seedance_1_5_pro": 0.08,
    "sora_2": 0.10,
    "sora_2_pro": 0.30,
    "veo_3_1_fast": 0.10
}

# Duration options per model
DURATION_OPTIONS = {
    "hailuo": ["6", "10"],
    "kling_2_1": ["5", "10"],
    "kling_2_6_pro": ["5", "10"],
    "seedance_1_5_pro": ["5", "10"],
    "sora_2": [4, 8, 12],
    "sora_2_pro": [4, 8, 12],
    "veo_3_1_fast": ["4s", "6s", "8s"]
}

# Resolution options per model
RESOLUTION_OPTIONS = {
    "hailuo": ["768p"],
    "kling_2_1": ["720p", "1080p"],
    "kling_2_6_pro": ["720p", "1080p"],
    "seedance_1_5_pro": ["720p", "1080p"],
    "sora_2": ["auto", "720p"],
    "sora_2_pro": ["auto", "720p", "1080p"],
    "veo_3_1_fast": ["720p", "1080p"]
}

# Aspect ratio options
ASPECT_RATIO_OPTIONS = {
    "sora_2": ["auto", "9:16", "16:9"],
    "sora_2_pro": ["auto", "9:16", "16:9"],
    "veo_3_1_fast": ["auto", "16:9", "9:16"]
}

# Default values per model
DEFAULT_VALUES = {
    "hailuo": {
        "duration": "6",
        "prompt_optimizer": True
    },
    "kling_2_1": {
        "duration": "5",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5
    },
    "kling_2_6_pro": {
        "duration": "5",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5
    },
    "seedance_1_5_pro": {
        "duration": "5",
        "seed": None
    },
    "sora_2": {
        "duration": 4,
        "resolution": "auto",
        "aspect_ratio": "auto",
        "delete_video": True
    },
    "sora_2_pro": {
        "duration": 4,
        "resolution": "auto",
        "aspect_ratio": "auto",
        "delete_video": True
    },
    "veo_3_1_fast": {
        "duration": "8s",
        "resolution": "720p",
        "aspect_ratio": "auto",
        "generate_audio": True,
        "auto_fix": False
    }
}

# Model info for documentation
MODEL_INFO = {
    "hailuo": {
        "name": "MiniMax Hailuo-02",
        "provider": "MiniMax",
        "description": "Standard image-to-video with prompt optimization",
        "max_duration": 10,
        "features": ["prompt_optimizer"],
        "extended_params": ["start_frame"]
    },
    "kling_2_1": {
        "name": "Kling Video v2.1",
        "provider": "Kuaishou",
        "description": "High-quality generation with negative prompts and frame interpolation",
        "max_duration": 10,
        "features": ["negative_prompt", "cfg_scale", "frame_interpolation"],
        "extended_params": ["start_frame", "end_frame"]
    },
    "kling_2_6_pro": {
        "name": "Kling Video v2.6 Pro",
        "provider": "Kuaishou",
        "description": "Professional tier with enhanced quality and frame interpolation",
        "max_duration": 10,
        "features": ["negative_prompt", "cfg_scale", "professional_quality", "frame_interpolation"],
        "extended_params": ["start_frame", "end_frame"]
    },
    "seedance_1_5_pro": {
        "name": "ByteDance Seedance v1.5 Pro",
        "provider": "ByteDance",
        "description": "Advanced motion synthesis with seed control",
        "max_duration": 10,
        "features": ["seed_control", "motion_quality"],
        "extended_params": ["start_frame"]
    },
    "sora_2": {
        "name": "Sora 2",
        "provider": "OpenAI (via FAL)",
        "description": "OpenAI's image-to-video model",
        "max_duration": 12,
        "features": ["aspect_ratio", "resolution"],
        "extended_params": ["start_frame"]
    },
    "sora_2_pro": {
        "name": "Sora 2 Pro",
        "provider": "OpenAI (via FAL)",
        "description": "Professional Sora with 1080p support",
        "max_duration": 12,
        "features": ["aspect_ratio", "resolution", "1080p"],
        "extended_params": ["start_frame"]
    },
    "veo_3_1_fast": {
        "name": "Veo 3.1 Fast",
        "provider": "Google (via FAL)",
        "description": "Fast video generation with optional audio",
        "max_duration": 8,
        "features": ["audio_generation", "auto_fix", "fast_processing"],
        "extended_params": ["start_frame", "audio_generate"]
    }
}

# Extended parameter support per model
# This matrix defines which advanced parameters each model supports
MODEL_EXTENDED_FEATURES = {
    "hailuo": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "kling_2_1": {
        "start_frame": True,
        "end_frame": True,  # tail_image_url
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "kling_2_6_pro": {
        "start_frame": True,
        "end_frame": True,  # tail_image_url
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "seedance_1_5_pro": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "sora_2": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "sora_2_pro": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "veo_3_1_fast": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": False,
        "audio_input": False,
        "audio_generate": True,  # generate_audio parameter
        "ref_video": False,
    },
}

# API parameter mapping for extended features
EXTENDED_PARAM_MAPPING = {
    "start_frame": "image_url",
    "end_frame": {
        "kling_2_1": "tail_image_url",
        "kling_2_6_pro": "tail_image_url",
    },
    "audio_generate": "generate_audio",
}
