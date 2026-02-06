"""
Constants and configuration for FAL Video to Video models
"""

from typing import Dict, List, Literal

# Model type definitions
ModelType = Literal[
    "thinksound",
    "topaz",
    "kling_o3_standard_edit",
    "kling_o3_pro_edit",
    "kling_o3_standard_v2v_ref",
    "kling_o3_pro_v2v_ref"
]

# Supported models
SUPPORTED_MODELS = [
    "thinksound",
    "topaz",
    "kling_o3_standard_edit",
    "kling_o3_pro_edit",
    "kling_o3_standard_v2v_ref",
    "kling_o3_pro_v2v_ref"
]

# Model endpoints mapping
MODEL_ENDPOINTS = {
    "thinksound": "fal-ai/thinksound",
    "topaz": "fal-ai/topaz/upscale/video",
    "kling_o3_standard_edit": "fal-ai/kling-video/o3/standard/video-to-video/edit",
    "kling_o3_pro_edit": "fal-ai/kling-video/o3/pro/video-to-video/edit",
    "kling_o3_standard_v2v_ref": "fal-ai/kling-video/o3/standard/video-to-video/reference",
    "kling_o3_pro_v2v_ref": "fal-ai/kling-video/o3/pro/video-to-video/reference"
}

# Model display names
MODEL_DISPLAY_NAMES = {
    "thinksound": "ThinkSound",
    "topaz": "Topaz Video Upscale",
    "kling_o3_standard_edit": "Kling O3 Standard Video Edit",
    "kling_o3_pro_edit": "Kling O3 Pro Video Edit",
    "kling_o3_standard_v2v_ref": "Kling O3 Standard V2V Reference",
    "kling_o3_pro_v2v_ref": "Kling O3 Pro V2V Reference"
}

# Model information
MODEL_INFO = {
    "thinksound": {
        "model_name": "ThinkSound",
        "description": "AI-powered video audio generation that creates realistic sound effects for any video",
        "features": [
            "Automatic sound effect generation",
            "Text prompt guidance",
            "Video context understanding",
            "High-quality audio synthesis",
            "Commercial use license"
        ],
        "pricing": "$0.001 per second",
        "supported_formats": ["mp4", "mov", "avi", "webm"],
        "max_duration": 300,  # 5 minutes
        "output_format": "mp4"
    },
    "topaz": {
        "model_name": "Topaz Video Upscale",
        "description": "Professional-grade video upscaling using Proteus v4 with optional Apollo v8 frame interpolation",
        "features": [
            "Up to 4x video upscaling",
            "Frame rate enhancement up to 120 FPS",
            "Proteus v4 upscaling engine",
            "Apollo v8 frame interpolation",
            "Professional quality enhancement",
            "Commercial use license"
        ],
        "pricing": "Commercial use pricing",
        "supported_formats": ["mp4", "mov", "avi", "webm"],
        "max_upscale": 4,
        "max_fps": 120,
        "output_format": "mp4"
    },
    "kling_o3_standard_edit": {
        "model_name": "Kling O3 Standard Video Edit",
        "provider": "Kuaishou",
        "description": "O3 video editing with element replacement and @ reference syntax",
        "features": [
            "Element-based object/character replacement",
            "Environment modification",
            "@ reference syntax",
            "Reference image integration"
        ],
        "pricing": "$0.252/second",
        "max_duration": 15,
        "output_format": "mp4"
    },
    "kling_o3_pro_edit": {
        "model_name": "Kling O3 Pro Video Edit",
        "provider": "Kuaishou",
        "description": "Professional O3 video editing with enhanced quality and element replacement",
        "features": [
            "Professional-tier quality",
            "Element-based object/character replacement",
            "Environment modification",
            "@ reference syntax",
            "Reference image integration"
        ],
        "pricing": "$0.336/second",
        "max_duration": 15,
        "output_format": "mp4"
    },
    "kling_o3_standard_v2v_ref": {
        "model_name": "Kling O3 Standard V2V Reference",
        "provider": "Kuaishou",
        "description": "O3 video-to-video with style transfer and element consistency",
        "features": [
            "Style transfer from reference images",
            "Element integration with consistency",
            "@ reference syntax",
            "Optional audio preservation"
        ],
        "pricing": "$0.252/second",
        "max_duration": 15,
        "output_format": "mp4"
    },
    "kling_o3_pro_v2v_ref": {
        "model_name": "Kling O3 Pro V2V Reference",
        "provider": "Kuaishou",
        "description": "Professional O3 video-to-video with style transfer and enhanced quality",
        "features": [
            "Professional-tier quality",
            "Style transfer from reference images",
            "Element integration with consistency",
            "@ reference syntax",
            "Optional audio preservation"
        ],
        "pricing": "$0.336/second",
        "max_duration": 15,
        "output_format": "mp4"
    }
}

# Default values
DEFAULT_VALUES = {
    "thinksound": {
        "seed": None,
        "prompt": None
    },
    "topaz": {
        "upscale_factor": 2,
        "target_fps": None
    },
    "kling_o3_standard_edit": {
        "duration": "5",
        "elements": [],
        "image_urls": [],
        "aspect_ratio": "16:9"
    },
    "kling_o3_pro_edit": {
        "duration": "5",
        "elements": [],
        "image_urls": [],
        "aspect_ratio": "16:9"
    },
    "kling_o3_standard_v2v_ref": {
        "duration": "5",
        "elements": [],
        "image_urls": [],
        "aspect_ratio": "16:9",
        "keep_audio": False
    },
    "kling_o3_pro_v2v_ref": {
        "duration": "5",
        "elements": [],
        "image_urls": [],
        "aspect_ratio": "16:9",
        "keep_audio": False
    }
}

# Duration options for O3 models
DURATION_OPTIONS = {
    "kling_o3_standard_edit": ["3", "5", "10", "15"],
    "kling_o3_pro_edit": ["3", "5", "10", "15"],
    "kling_o3_standard_v2v_ref": ["3", "5", "10", "15"],
    "kling_o3_pro_v2v_ref": ["3", "5", "10", "15"]
}

# Aspect ratio options for O3 models
ASPECT_RATIO_OPTIONS = {
    "kling_o3_standard_edit": ["16:9", "9:16", "1:1"],
    "kling_o3_pro_edit": ["16:9", "9:16", "1:1"],
    "kling_o3_standard_v2v_ref": ["16:9", "9:16", "1:1"],
    "kling_o3_pro_v2v_ref": ["16:9", "9:16", "1:1"]
}

# File size limits
MAX_VIDEO_SIZE_MB = 100
MAX_VIDEO_DURATION_SECONDS = 300

# Output settings
DEFAULT_OUTPUT_FORMAT = "mp4"
VIDEO_CODECS = {
    "mp4": "libx264",
    "webm": "libvpx",
    "mov": "libx264"
}