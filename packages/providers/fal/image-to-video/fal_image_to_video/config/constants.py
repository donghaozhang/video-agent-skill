"""
Constants and configuration for FAL Image-to-Video models.
"""

from typing import Literal, List

# Model type definitions
ModelType = Literal[
    "hailuo",
    "kling_2_1",
    "kling_2_6_pro",
    "kling_3_standard",
    "kling_3_pro",
    "kling_o3_standard_i2v",
    "kling_o3_pro_i2v",
    "kling_o3_standard_ref",
    "kling_o3_pro_ref",
    "seedance_1_5_pro",
    "sora_2",
    "sora_2_pro",
    "veo_3_1_fast",
    "wan_2_6",
    "grok_imagine"
]

SUPPORTED_MODELS: List[str] = [
    "hailuo",
    "kling_2_1",
    "kling_2_6_pro",
    "kling_3_standard",
    "kling_3_pro",
    "kling_o3_standard_i2v",
    "kling_o3_pro_i2v",
    "kling_o3_standard_ref",
    "kling_o3_pro_ref",
    "seedance_1_5_pro",
    "sora_2",
    "sora_2_pro",
    "veo_3_1_fast",
    "wan_2_6",
    "grok_imagine"
]

# Model endpoints
MODEL_ENDPOINTS = {
    "hailuo": "fal-ai/minimax/hailuo-02/standard/image-to-video",
    "kling_2_1": "fal-ai/kling-video/v2.1/standard/image-to-video",
    "kling_2_6_pro": "fal-ai/kling-video/v2.6/pro/image-to-video",
    "kling_3_standard": "fal-ai/kling-video/v3/standard/image-to-video",
    "kling_3_pro": "fal-ai/kling-video/v3/pro/image-to-video",
    "kling_o3_standard_i2v": "fal-ai/kling-video/o3/standard/image-to-video",
    "kling_o3_pro_i2v": "fal-ai/kling-video/o3/pro/image-to-video",
    "kling_o3_standard_ref": "fal-ai/kling-video/o3/standard/reference-to-video",
    "kling_o3_pro_ref": "fal-ai/kling-video/o3/pro/reference-to-video",
    "seedance_1_5_pro": "fal-ai/bytedance/seedance/v1.5/pro/image-to-video",
    "sora_2": "fal-ai/sora-2/image-to-video",
    "sora_2_pro": "fal-ai/sora-2/image-to-video/pro",
    "veo_3_1_fast": "fal-ai/veo3.1/fast/image-to-video",
    "wan_2_6": "wan/v2.6/image-to-video",
    "grok_imagine": "xai/grok-imagine-video/image-to-video"
}

# Display names
MODEL_DISPLAY_NAMES = {
    "hailuo": "MiniMax Hailuo-02",
    "kling_2_1": "Kling Video v2.1",
    "kling_2_6_pro": "Kling Video v2.6 Pro",
    "kling_3_standard": "Kling Video v3 Standard",
    "kling_3_pro": "Kling Video v3 Pro",
    "kling_o3_standard_i2v": "Kling O3 Standard Image-to-Video",
    "kling_o3_pro_i2v": "Kling O3 Pro Image-to-Video",
    "kling_o3_standard_ref": "Kling O3 Standard Reference-to-Video",
    "kling_o3_pro_ref": "Kling O3 Pro Reference-to-Video",
    "seedance_1_5_pro": "ByteDance Seedance v1.5 Pro",
    "sora_2": "Sora 2",
    "sora_2_pro": "Sora 2 Pro",
    "veo_3_1_fast": "Veo 3.1 Fast",
    "wan_2_6": "Wan v2.6",
    "grok_imagine": "xAI Grok Imagine Video"
}

# Pricing per second (USD)
# Note: Kling v3 models have variable pricing based on audio settings
MODEL_PRICING = {
    "hailuo": 0.05,
    "kling_2_1": 0.05,
    "kling_2_6_pro": 0.10,
    "kling_3_standard": {
        "no_audio": 0.168,
        "audio": 0.252,
        "voice_control": 0.308
    },
    "kling_3_pro": {
        "no_audio": 0.224,
        "audio": 0.336,
        "voice_control": 0.392
    },
    "kling_o3_standard_i2v": {
        "no_audio": 0.168,
        "audio": 0.224
    },
    "kling_o3_pro_i2v": {
        "no_audio": 0.224,
        "audio": 0.28
    },
    "kling_o3_standard_ref": {
        "no_audio": 0.084,
        "audio": 0.112
    },
    "kling_o3_pro_ref": {
        "no_audio": 0.224,
        "audio": 0.28
    },
    "seedance_1_5_pro": 0.08,
    "sora_2": 0.10,
    "sora_2_pro": 0.30,
    "veo_3_1_fast": 0.10,
    "wan_2_6": 0.10,  # Base price, 1080p is 0.15/s
    "grok_imagine": 0.05  # $0.05/s + $0.002 image input
}

# Duration options per model
DURATION_OPTIONS = {
    "hailuo": ["6", "10"],
    "kling_2_1": ["5", "10"],
    "kling_2_6_pro": ["5", "10"],
    "kling_3_standard": ["5", "10", "12"],
    "kling_3_pro": ["5", "10", "12"],
    "kling_o3_standard_i2v": ["3", "5", "10", "15"],
    "kling_o3_pro_i2v": ["3", "5", "10", "15"],
    "kling_o3_standard_ref": ["3", "5", "10", "15"],
    "kling_o3_pro_ref": ["3", "5", "10", "15"],
    "seedance_1_5_pro": ["5", "10"],
    "sora_2": [4, 8, 12],
    "sora_2_pro": [4, 8, 12],
    "veo_3_1_fast": ["4s", "6s", "8s"],
    "wan_2_6": ["5", "10", "15"],
    "grok_imagine": list(range(1, 16))  # 1-15 seconds
}

# Resolution options per model
RESOLUTION_OPTIONS = {
    "hailuo": ["768p"],
    "kling_2_1": ["720p", "1080p"],
    "kling_2_6_pro": ["720p", "1080p"],
    "kling_3_standard": ["720p", "1080p"],
    "kling_3_pro": ["720p", "1080p"],
    "kling_o3_standard_i2v": ["720p", "1080p"],
    "kling_o3_pro_i2v": ["720p", "1080p"],
    "kling_o3_standard_ref": ["720p", "1080p"],
    "kling_o3_pro_ref": ["720p", "1080p"],
    "seedance_1_5_pro": ["720p", "1080p"],
    "sora_2": ["auto", "720p"],
    "sora_2_pro": ["auto", "720p", "1080p"],
    "veo_3_1_fast": ["720p", "1080p"],
    "wan_2_6": ["720p", "1080p"],
    "grok_imagine": ["480p", "720p"]
}

# Aspect ratio options
ASPECT_RATIO_OPTIONS = {
    "kling_3_standard": ["16:9", "9:16", "1:1"],
    "kling_3_pro": ["16:9", "9:16", "1:1"],
    "kling_o3_standard_i2v": ["16:9", "9:16", "1:1"],
    "kling_o3_pro_i2v": ["16:9", "9:16", "1:1"],
    "kling_o3_standard_ref": ["16:9", "9:16", "1:1"],
    "kling_o3_pro_ref": ["16:9", "9:16", "1:1"],
    "sora_2": ["auto", "9:16", "16:9"],
    "sora_2_pro": ["auto", "9:16", "16:9"],
    "veo_3_1_fast": ["auto", "16:9", "9:16"],
    "wan_2_6": ["16:9", "9:16", "1:1"],
    "grok_imagine": ["auto", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16"]
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
    "kling_3_standard": {
        "duration": "5",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5,
        "generate_audio": False,
        "voice_ids": [],
        "multi_prompt": [],
        "elements": [],
        "aspect_ratio": "16:9"
    },
    "kling_3_pro": {
        "duration": "5",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5,
        "generate_audio": False,
        "voice_ids": [],
        "multi_prompt": [],
        "elements": [],
        "aspect_ratio": "16:9"
    },
    "kling_o3_standard_i2v": {
        "duration": "5",
        "generate_audio": True,
        "elements": [],
        "image_urls": [],
        "aspect_ratio": "16:9",
        "negative_prompt": None,
        "cfg_scale": 0.5
    },
    "kling_o3_pro_i2v": {
        "duration": "5",
        "generate_audio": True,
        "elements": [],
        "image_urls": [],
        "aspect_ratio": "16:9",
        "negative_prompt": None,
        "cfg_scale": 0.5
    },
    "kling_o3_standard_ref": {
        "duration": "5",
        "generate_audio": False,
        "elements": [],
        "image_urls": [],
        "aspect_ratio": "16:9",
        "multi_prompt": [],
        "shot_type": None
    },
    "kling_o3_pro_ref": {
        "duration": "5",
        "generate_audio": False,
        "elements": [],
        "image_urls": [],
        "aspect_ratio": "16:9"
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
    },
    "wan_2_6": {
        "duration": "5",
        "resolution": "1080p",
        "negative_prompt": "",
        "enable_prompt_expansion": True,
        "multi_shots": False,
        "seed": None,
        "enable_safety_checker": True
    },
    "grok_imagine": {
        "duration": 6,
        "resolution": "720p",
        "aspect_ratio": "auto"
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
    "kling_3_standard": {
        "name": "Kling Video v3 Standard",
        "provider": "Kuaishou",
        "description": "Latest generation with native audio, voice control, and multi-prompt support",
        "max_duration": 12,
        "features": [
            "negative_prompt", "cfg_scale", "frame_interpolation",
            "audio_generation", "voice_control", "multi_prompt", "custom_elements"
        ],
        "extended_params": ["start_frame", "end_frame", "audio_generate", "elements"]
    },
    "kling_3_pro": {
        "name": "Kling Video v3 Pro",
        "provider": "Kuaishou",
        "description": "Top-tier cinematic visuals with native audio, voice control, and multi-prompt support",
        "max_duration": 12,
        "features": [
            "negative_prompt", "cfg_scale", "professional_quality", "frame_interpolation",
            "audio_generation", "voice_control", "multi_prompt", "custom_elements"
        ],
        "extended_params": ["start_frame", "end_frame", "audio_generate", "elements"]
    },
    "kling_o3_standard_i2v": {
        "name": "Kling O3 Standard Image-to-Video",
        "provider": "Kuaishou",
        "description": "O3 (Omni) model with element-based character/object consistency",
        "max_duration": 15,
        "features": [
            "audio_generation", "elements", "end_frame", "reference_images"
        ],
        "extended_params": ["start_frame", "end_frame", "audio_generate", "elements", "image_urls"]
    },
    "kling_o3_pro_i2v": {
        "name": "Kling O3 Pro Image-to-Video",
        "provider": "Kuaishou",
        "description": "Professional O3 (Omni) model with enhanced quality and element consistency",
        "max_duration": 15,
        "features": [
            "audio_generation", "elements", "end_frame", "reference_images", "professional_quality"
        ],
        "extended_params": ["start_frame", "end_frame", "audio_generate", "elements", "image_urls"]
    },
    "kling_o3_standard_ref": {
        "name": "Kling O3 Standard Reference-to-Video",
        "provider": "Kuaishou",
        "description": "O3 reference model with @ syntax for element-based character generation",
        "max_duration": 15,
        "features": [
            "audio_generation", "elements", "reference_images", "reference_syntax", "multi_prompt"
        ],
        "extended_params": ["start_frame", "audio_generate", "elements", "image_urls"]
    },
    "kling_o3_pro_ref": {
        "name": "Kling O3 Pro Reference-to-Video",
        "provider": "Kuaishou",
        "description": "Professional O3 reference model with @ syntax and enhanced quality",
        "max_duration": 15,
        "features": [
            "audio_generation", "elements", "end_frame", "reference_images", "reference_syntax", "professional_quality"
        ],
        "extended_params": ["start_frame", "end_frame", "audio_generate", "elements", "image_urls"]
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
    },
    "wan_2_6": {
        "name": "Wan v2.6",
        "provider": "Wan",
        "description": "High-quality image-to-video with multi-shot support",
        "max_duration": 15,
        "features": ["prompt_expansion", "multi_shots", "audio_input", "seed_control", "safety_checker"],
        "extended_params": ["start_frame", "audio_input"]
    },
    "grok_imagine": {
        "name": "xAI Grok Imagine Video",
        "provider": "xAI (via FAL)",
        "description": "xAI's image-to-video with native audio generation",
        "max_duration": 15,
        "features": ["audio_generation", "flexible_duration", "multiple_aspect_ratios"],
        "extended_params": ["start_frame"]
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
    "kling_3_standard": {
        "start_frame": True,
        "end_frame": True,  # end_image_url
        "ref_images": True,  # via elements parameter
        "audio_input": False,
        "audio_generate": True,  # generate_audio parameter
        "ref_video": True,  # via elements parameter
    },
    "kling_3_pro": {
        "start_frame": True,
        "end_frame": True,  # end_image_url
        "ref_images": True,  # via elements parameter
        "audio_input": False,
        "audio_generate": True,  # generate_audio parameter
        "ref_video": True,  # via elements parameter
    },
    "kling_o3_standard_i2v": {
        "start_frame": True,
        "end_frame": True,  # end_image_url
        "ref_images": True,  # via image_urls parameter
        "audio_input": False,
        "audio_generate": True,
        "ref_video": False,
        "elements": True,  # character/object consistency
    },
    "kling_o3_pro_i2v": {
        "start_frame": True,
        "end_frame": True,  # end_image_url
        "ref_images": True,  # via image_urls parameter
        "audio_input": False,
        "audio_generate": True,
        "ref_video": False,
        "elements": True,  # character/object consistency
    },
    "kling_o3_standard_ref": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": True,  # via image_urls parameter
        "audio_input": False,
        "audio_generate": True,
        "ref_video": False,
        "elements": True,  # character/object consistency
    },
    "kling_o3_pro_ref": {
        "start_frame": True,
        "end_frame": True,  # end_image_url
        "ref_images": True,  # via image_urls parameter
        "audio_input": False,
        "audio_generate": True,
        "ref_video": False,
        "elements": True,  # character/object consistency
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
    "wan_2_6": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": False,
        "audio_input": True,  # Supports audio_url
        "audio_generate": False,
        "ref_video": False,
    },
    "grok_imagine": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,  # Audio is auto-generated
        "ref_video": False,
    },
}

# API parameter mapping for extended features
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
