"""
Constants and configuration for FAL Text-to-Video models.
"""

from typing import Literal, List

# Model type definitions
ModelType = Literal[
    "hailuo_pro",
    "veo3",
    "veo3_fast",
    "kling_2_6_pro",
    "kling_3_standard",
    "kling_3_pro",
    "kling_o3_pro_t2v",
    "sora_2",
    "sora_2_pro",
    "grok_imagine"
]

SUPPORTED_MODELS: List[str] = [
    "hailuo_pro",
    "veo3",
    "veo3_fast",
    "kling_2_6_pro",
    "kling_3_standard",
    "kling_3_pro",
    "kling_o3_pro_t2v",
    "sora_2",
    "sora_2_pro",
    "grok_imagine"
]

# Model endpoints
MODEL_ENDPOINTS = {
    "hailuo_pro": "fal-ai/minimax/hailuo-02/pro/text-to-video",
    "veo3": "fal-ai/veo3",
    "veo3_fast": "fal-ai/veo3/fast",
    "kling_2_6_pro": "fal-ai/kling-video/v2.6/pro/text-to-video",
    "kling_3_standard": "fal-ai/kling-video/v3/standard/text-to-video",
    "kling_3_pro": "fal-ai/kling-video/v3/pro/text-to-video",
    "kling_o3_pro_t2v": "fal-ai/kling-video/o3/pro/text-to-video",
    "sora_2": "fal-ai/sora-2/text-to-video",
    "sora_2_pro": "fal-ai/sora-2/text-to-video/pro",
    "grok_imagine": "xai/grok-imagine-video/text-to-video"
}

# Display names
MODEL_DISPLAY_NAMES = {
    "hailuo_pro": "MiniMax Hailuo-02 Pro",
    "veo3": "Google Veo 3",
    "veo3_fast": "Google Veo 3 Fast",
    "kling_2_6_pro": "Kling Video v2.6 Pro",
    "kling_3_standard": "Kling Video v3 Standard",
    "kling_3_pro": "Kling Video v3 Pro",
    "kling_o3_pro_t2v": "Kling O3 Pro Text-to-Video",
    "sora_2": "Sora 2",
    "sora_2_pro": "Sora 2 Pro",
    "grok_imagine": "xAI Grok Imagine Video"
}

# Pricing (USD)
MODEL_PRICING = {
    "hailuo_pro": {
        "type": "per_video",
        "cost": 0.08
    },
    "veo3": {
        "type": "per_second",
        "cost_no_audio": 0.50,
        "cost_with_audio": 0.75
    },
    "veo3_fast": {
        "type": "per_second",
        "cost_no_audio": 0.25,
        "cost_with_audio": 0.40
    },
    "kling_2_6_pro": {
        "type": "per_second",
        "cost_no_audio": 0.07,
        "cost_with_audio": 0.14
    },
    "kling_3_standard": {
        "type": "per_second",
        "cost_no_audio": 0.168,
        "cost_with_audio": 0.252,
        "cost_voice_control": 0.308
    },
    "kling_3_pro": {
        "type": "per_second",
        "cost_no_audio": 0.224,
        "cost_with_audio": 0.336,
        "cost_voice_control": 0.392
    },
    "kling_o3_pro_t2v": {
        "type": "per_second",
        "cost_no_audio": 0.224,
        "cost_with_audio": 0.28
    },
    "sora_2": {
        "type": "per_second",
        "cost": 0.10
    },
    "sora_2_pro": {
        "type": "per_second",
        "cost_720p": 0.30,
        "cost_1080p": 0.50
    },
    "grok_imagine": {
        "type": "per_second",
        "base_duration": 6,
        "base_cost_6s": 0.30,
        "cost_per_additional_second": 0.05
    }
}

# Duration options per model
DURATION_OPTIONS = {
    "hailuo_pro": ["6"],  # Fixed 6 seconds
    "veo3": ["5s", "6s", "7s", "8s"],
    "veo3_fast": ["5s", "6s", "7s", "8s"],
    "kling_2_6_pro": ["5", "10"],
    "kling_3_standard": ["5", "10", "12"],
    "kling_3_pro": ["5", "10", "12"],
    "kling_o3_pro_t2v": ["3", "5", "10", "15"],
    "sora_2": [4, 8, 12],
    "sora_2_pro": [4, 8, 12],
    "grok_imagine": list(range(1, 16))  # 1-15 seconds
}

# Resolution options per model
RESOLUTION_OPTIONS = {
    "hailuo_pro": ["1080p"],
    "veo3": ["720p"],
    "veo3_fast": ["720p"],
    "kling_2_6_pro": ["720p"],  # Text-to-video only supports 720p
    "kling_3_standard": ["720p"],
    "kling_3_pro": ["720p"],
    "kling_o3_pro_t2v": ["720p", "1080p"],
    "sora_2": ["720p"],
    "sora_2_pro": ["720p", "1080p"],
    "grok_imagine": ["480p", "720p"]
}

# Aspect ratio options
ASPECT_RATIO_OPTIONS = {
    "hailuo_pro": ["16:9"],  # Fixed
    "veo3": ["16:9", "9:16", "1:1"],
    "veo3_fast": ["16:9", "9:16", "1:1"],
    "kling_2_6_pro": ["16:9", "9:16", "1:1"],
    "kling_3_standard": ["16:9", "9:16", "1:1"],
    "kling_3_pro": ["16:9", "9:16", "1:1"],
    "kling_o3_pro_t2v": ["16:9", "9:16", "1:1"],
    "sora_2": ["16:9", "9:16"],
    "sora_2_pro": ["16:9", "9:16"],
    "grok_imagine": ["16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16"]
}

# Default values per model
DEFAULT_VALUES = {
    "hailuo_pro": {
        "prompt_optimizer": True
    },
    "veo3": {
        "duration": "8s",
        "aspect_ratio": "16:9",
        "generate_audio": True,
        "enhance_prompt": True
    },
    "veo3_fast": {
        "duration": "8s",
        "aspect_ratio": "16:9",
        "generate_audio": True
    },
    "kling_2_6_pro": {
        "duration": "5",
        "aspect_ratio": "16:9",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5,
        "generate_audio": True
    },
    "kling_3_standard": {
        "duration": "5",
        "aspect_ratio": "16:9",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5,
        "generate_audio": False,
        "voice_ids": [],
        "multi_prompt": [],
        "shot_type": None
    },
    "kling_3_pro": {
        "duration": "5",
        "aspect_ratio": "16:9",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5,
        "generate_audio": False,
        "voice_ids": [],
        "multi_prompt": [],
        "shot_type": None
    },
    "kling_o3_pro_t2v": {
        "duration": "5",
        "aspect_ratio": "16:9",
        "negative_prompt": None,
        "cfg_scale": 0.5,
        "generate_audio": True,
        "elements": [],
        "image_urls": [],
        "multi_prompt": [],
        "shot_type": None
    },
    "sora_2": {
        "duration": 4,
        "resolution": "720p",
        "aspect_ratio": "16:9",
        "delete_video": True
    },
    "sora_2_pro": {
        "duration": 4,
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "delete_video": True
    },
    "grok_imagine": {
        "duration": 6,
        "resolution": "720p",
        "aspect_ratio": "16:9"
    }
}

# Model info for documentation
MODEL_INFO = {
    "hailuo_pro": {
        "name": "MiniMax Hailuo-02 Pro",
        "provider": "MiniMax",
        "description": "Cost-effective text-to-video with prompt optimization",
        "max_duration": 6,
        "features": ["prompt_optimizer", "1080p", "cost_effective"]
    },
    "veo3": {
        "name": "Google Veo 3",
        "provider": "Google (via FAL)",
        "description": "Premium quality with audio generation",
        "max_duration": 8,
        "features": ["audio_generation", "enhance_prompt", "negative_prompt", "seed_control"]
    },
    "veo3_fast": {
        "name": "Google Veo 3 Fast",
        "provider": "Google (via FAL)",
        "description": "Fast generation with good quality",
        "max_duration": 8,
        "features": ["audio_generation", "fast_processing", "seed_control"]
    },
    "kling_2_6_pro": {
        "name": "Kling Video v2.6 Pro",
        "provider": "Kuaishou",
        "description": "Professional text-to-video with audio support",
        "max_duration": 10,
        "features": ["audio_generation", "negative_prompt", "cfg_scale", "multilingual"]
    },
    "kling_3_standard": {
        "name": "Kling Video v3 Standard",
        "provider": "Kuaishou",
        "description": "Latest generation with native audio, voice control, and multi-prompt support",
        "max_duration": 12,
        "features": [
            "audio_generation", "voice_control", "multi_prompt", "shot_type",
            "negative_prompt", "cfg_scale", "multilingual"
        ]
    },
    "kling_3_pro": {
        "name": "Kling Video v3 Pro",
        "provider": "Kuaishou",
        "description": "Top-tier cinematic visuals with native audio, voice control, and multi-prompt support",
        "max_duration": 12,
        "features": [
            "audio_generation", "voice_control", "multi_prompt", "shot_type",
            "negative_prompt", "cfg_scale", "multilingual", "professional_quality"
        ]
    },
    "kling_o3_pro_t2v": {
        "name": "Kling O3 Pro Text-to-Video",
        "provider": "Kuaishou",
        "description": "O3 (Omni) model with element-based character/object consistency and @ reference syntax",
        "max_duration": 15,
        "features": [
            "audio_generation", "elements", "reference_images", "reference_syntax",
            "multi_prompt", "shot_type", "negative_prompt", "cfg_scale", "professional_quality"
        ]
    },
    "sora_2": {
        "name": "Sora 2",
        "provider": "OpenAI (via FAL)",
        "description": "OpenAI's text-to-video model",
        "max_duration": 12,
        "features": ["aspect_ratio", "long_duration"]
    },
    "sora_2_pro": {
        "name": "Sora 2 Pro",
        "provider": "OpenAI (via FAL)",
        "description": "Professional Sora with 1080p support",
        "max_duration": 12,
        "features": ["aspect_ratio", "1080p", "long_duration"]
    },
    "grok_imagine": {
        "name": "xAI Grok Imagine Video",
        "provider": "xAI (via FAL)",
        "description": "xAI's text-to-video with native audio generation",
        "max_duration": 15,
        "features": ["audio_generation", "flexible_duration", "multiple_aspect_ratios"]
    }
}
