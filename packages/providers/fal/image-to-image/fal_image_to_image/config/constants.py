"""
Constants and configuration for FAL Image-to-Image models
"""

from typing import Dict, List, Literal

# Model type definitions
ModelType = Literal["photon", "photon_base", "kontext", "kontext_multi", "seededit", "clarity", "nano_banana_pro_edit", "gpt_image_1_5_edit"]
AspectRatio = Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]

# Supported models
SUPPORTED_MODELS = ["photon", "photon_base", "kontext", "kontext_multi", "seededit", "clarity", "nano_banana_pro_edit", "gpt_image_1_5_edit"]

# Model endpoints mapping
MODEL_ENDPOINTS = {
    "photon": "fal-ai/luma-photon/flash/modify",
    "photon_base": "fal-ai/luma-photon/modify",
    "kontext": "fal-ai/flux-kontext/dev",
    "kontext_multi": "fal-ai/flux-pro/kontext/max/multi",
    "seededit": "fal-ai/bytedance/seededit/v3/edit-image",
    "clarity": "fal-ai/clarity-upscaler",
    "nano_banana_pro_edit": "fal-ai/nano-banana-pro/edit",
    "gpt_image_1_5_edit": "fal-ai/gpt-image-1.5/edit"
}

# Reframe endpoints for aspect ratio changes
REFRAME_ENDPOINTS = {
    "photon": "fal-ai/luma-photon/flash/reframe",
    "photon_base": "fal-ai/luma-photon/reframe"
}

# Aspect ratios for different models
ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]
KONTEXT_MULTI_ASPECT_RATIOS = ["21:9", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "9:21"]

# Parameter ranges
PHOTON_STRENGTH_RANGE = (0.0, 1.0)
KONTEXT_INFERENCE_STEPS_RANGE = (1, 50)
KONTEXT_GUIDANCE_SCALE_RANGE = (1.0, 20.0)
SEEDEDIT_GUIDANCE_SCALE_RANGE = (0.0, 1.0)

# Default values
DEFAULT_VALUES = {
    "photon": {
        "strength": 0.8,
        "aspect_ratio": "1:1"
    },
    "kontext": {
        "num_inference_steps": 28,
        "guidance_scale": 2.5,
        "resolution_mode": "auto"
    },
    "seededit": {
        "guidance_scale": 0.5
    },
    "clarity": {
        "scale": 2,
        "enable_enhancement": True
    },
    "nano_banana_pro_edit": {
        "strength": 0.75,
        "num_inference_steps": 4
    },
    "gpt_image_1_5_edit": {
        "strength": 0.75
    }
}

# Model display names
MODEL_DISPLAY_NAMES = {
    "photon": "Luma Photon Flash",
    "photon_base": "Luma Photon Base",
    "kontext": "FLUX Kontext Dev",
    "kontext_multi": "FLUX Kontext [max] Multi",
    "seededit": "ByteDance SeedEdit v3",
    "clarity": "Clarity Upscaler",
    "nano_banana_pro_edit": "Nano Banana Pro Edit",
    "gpt_image_1_5_edit": "GPT Image 1.5 Edit"
}

# Model features and descriptions
MODEL_INFO = {
    "photon": {
        "model_name": "Luma Photon Flash",
        "description": "Creative, personalizable, and intelligent image modification model",
        "supported_aspect_ratios": ASPECT_RATIOS,
        "strength_range": "0.0 - 1.0",
        "features": [
            "Fast processing",
            "High-quality results", 
            "Creative modifications",
            "Personalizable outputs",
            "Aspect ratio control"
        ]
    },
    "photon_base": {
        "model_name": "Luma Photon Base",
        "description": "Most creative, personalizable, and intelligent visual model for creatives",
        "supported_aspect_ratios": ASPECT_RATIOS,
        "strength_range": "0.0 - 1.0",
        "cost_per_megapixel": "$0.019",
        "features": [
            "Step-function change in cost",
            "High-quality image generation",
            "Creative image editing",
            "Prompt-based modifications",
            "Commercial use ready"
        ]
    },
    "kontext": {
        "model_name": "FLUX Kontext Dev",
        "description": "Frontier image editing model focused on contextual understanding",
        "supported_aspect_ratios": ["auto", "match_input"],
        "inference_steps_range": "1 - 50 (default: 28)",
        "guidance_scale_range": "1.0 - 20.0 (default: 2.5)",
        "features": [
            "Contextual understanding",
            "Nuanced modifications",
            "Style preservation",
            "Iterative editing",
            "Precise control"
        ]
    },
    "kontext_multi": {
        "model_name": "FLUX Kontext [max] Multi",
        "description": "Experimental multi-image version of FLUX Kontext [max] with advanced capabilities",
        "supported_aspect_ratios": KONTEXT_MULTI_ASPECT_RATIOS,
        "guidance_scale_range": "1.0 - 20.0 (default: 3.5)",
        "num_images_range": "1 - 10 (default: 1)",
        "features": [
            "Multi-image input support",
            "Advanced contextual understanding",
            "Experimental capabilities",
            "High-quality results",
            "Safety tolerance control",
            "Multiple output formats"
        ]
    },
    "seededit": {
        "model_name": "ByteDance SeedEdit v3",
        "description": "Accurate image editing model with excellent content preservation",
        "guidance_scale_range": "0.0 - 1.0 (default: 0.5)",
        "seed_support": "Yes (optional)",
        "features": [
            "Accurate editing instruction following",
            "Effective content preservation",
            "Commercial use ready",
            "Simple parameter set",
            "High-quality results",
            "ByteDance developed"
        ]
    },
    "clarity": {
        "model_name": "Clarity Upscaler",
        "description": "High-quality image upscaling with optional creative enhancement",
        "scale_factor_range": "1 - 4 (default: 2)",
        "seed_support": "Yes (optional)",
        "features": [
            "Up to 4x upscaling",
            "Optional creative enhancement",
            "Maintains image quality",
            "Fast processing",
            "Commercial use ready",
            "Prompt-based enhancement"
        ]
    },
    "nano_banana_pro_edit": {
        "model_name": "Nano Banana Pro Edit",
        "description": "Fast image editing with Nano Banana Pro model",
        "strength_range": "0.0 - 1.0 (default: 0.75)",
        "num_inference_steps_range": "1 - 8 (default: 4)",
        "features": [
            "Fast processing",
            "High-quality edits",
            "Cost-effective",
            "Simple parameter set",
            "Commercial use ready"
        ]
    },
    "gpt_image_1_5_edit": {
        "model_name": "GPT Image 1.5 Edit",
        "description": "GPT-powered image editing with natural language understanding",
        "strength_range": "0.0 - 1.0 (default: 0.75)",
        "features": [
            "GPT-powered editing",
            "Natural language understanding",
            "High-quality results",
            "Creative modifications",
            "Commercial use ready"
        ]
    }
}