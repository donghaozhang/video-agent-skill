"""
Configuration constants for AI Content Pipeline
"""

# Supported models for each pipeline step
SUPPORTED_MODELS = {
    "text_to_image": [
        "flux_dev",           # FLUX.1 Dev (high quality)
        "flux_schnell",       # FLUX.1 Schnell (fast)
        "imagen4",            # Google Imagen 4
        "seedream_v3",        # Seedream v3 (bilingual) - FAL
        "seedream3",          # Seedream-3 (high-res) - Replicate
        "gen4",               # Runway Gen-4 (multi-reference guided) - Replicate
        "nano_banana_pro",    # Nano Banana Pro (fast, high-quality) - FAL
        "gpt_image_1_5",      # GPT Image 1.5 (GPT-powered) - FAL
        "dalle3",             # OpenAI DALL-E 3 (planned)
        "stable_diffusion",   # Stability AI (planned)
    ],
    "text_to_speech": [
        "elevenlabs",         # ElevenLabs TTS (high quality)
        "elevenlabs_turbo",   # ElevenLabs Turbo (fast)
        "elevenlabs_v3",      # ElevenLabs v3 (latest)
    ],
    "image_understanding": [
        "gemini_describe",    # Basic image description
        "gemini_detailed",    # Detailed image analysis
        "gemini_classify",    # Image classification and categorization
        "gemini_objects",     # Object detection and identification
        "gemini_ocr",         # Text extraction (OCR)
        "gemini_composition", # Artistic and technical analysis
        "gemini_qa",          # Question and answer system
    ],
    "prompt_generation": [
        "openrouter_video_prompt",     # OpenRouter-based video prompt generation
        "openrouter_video_cinematic",  # Cinematic style video prompts
        "openrouter_video_realistic",  # Realistic style video prompts
        "openrouter_video_artistic",   # Artistic style video prompts
        "openrouter_video_dramatic",   # Dramatic style video prompts
    ],
    "image_to_image": [
        "photon_flash",           # Luma Photon Flash (creative, fast)
        "photon_base",            # Luma Photon Base (high quality)
        "flux_kontext",           # FLUX Kontext Dev (contextual editing)
        "flux_kontext_multi",     # FLUX Kontext Multi (multi-image)
        "seededit_v3",            # ByteDance SeedEdit v3 (precise editing)
        "clarity_upscaler",       # Clarity AI upscaler
        "nano_banana_pro_edit",   # Nano Banana Pro Edit (fast editing) - FAL
        "gpt_image_1_5_edit",     # GPT Image 1.5 Edit (GPT-powered editing) - FAL
    ],
    "image_to_video": [
        "veo3",               # Google Veo 3.0
        "veo3_fast",          # Google Veo 3.0 Fast
        "veo2",               # Google Veo 2.0  
        "hailuo",             # MiniMax Hailuo-02
        "kling",              # Kling Video 2.1
    ],
    "add_audio": [
        "thinksound",         # ThinksSound AI audio generation
    ],
    "upscale_video": [
        "topaz",              # Topaz Video Upscale
    ]
}

# Pipeline step types
PIPELINE_STEPS = [
    "text_to_image",
    "image_understanding",
    "prompt_generation",
    "image_to_image",
    "image_to_video",
    "text_to_speech", 
    "add_audio",
    "upscale_video"
]

# Model recommendations based on use case
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
    }
}

# Cost estimates (USD)
COST_ESTIMATES = {
    "text_to_image": {
        "flux_dev": 0.003,
        "flux_schnell": 0.001,
        "imagen4": 0.004,
        "seedream_v3": 0.002,
        "seedream3": 0.003,
        "gen4": 0.08,
        "nano_banana_pro": 0.002,
        "gpt_image_1_5": 0.003,
    },
    "text_to_speech": {
        "elevenlabs": 0.05,
        "elevenlabs_turbo": 0.03,
        "elevenlabs_v3": 0.08,
    },
    "image_understanding": {
        "gemini_describe": 0.001,
        "gemini_detailed": 0.002,
        "gemini_classify": 0.001,
        "gemini_objects": 0.002,
        "gemini_ocr": 0.001,
        "gemini_composition": 0.002,
        "gemini_qa": 0.001,
    },
    "prompt_generation": {
        "openrouter_video_prompt": 0.002,
        "openrouter_video_cinematic": 0.002,
        "openrouter_video_realistic": 0.002,
        "openrouter_video_artistic": 0.002,
        "openrouter_video_dramatic": 0.002,
    },
    "image_to_image": {
        "photon_flash": 0.02,
        "photon_base": 0.03,
        "flux_kontext": 0.025,
        "flux_kontext_multi": 0.04,
        "seededit_v3": 0.02,
        "clarity_upscaler": 0.05,
        "nano_banana_pro_edit": 0.015,
        "gpt_image_1_5_edit": 0.02,
    },
    "image_to_video": {
        "veo3": 3.00,
        "veo3_fast": 2.00,
        "veo2": 2.50,
        "hailuo": 0.08,
        "kling": 0.10,
    },
    "add_audio": {
        "thinksound": 0.05,
    },
    "upscale_video": {
        "topaz": 1.50,
    }
}

# Processing time estimates (seconds)
PROCESSING_TIME_ESTIMATES = {
    "text_to_image": {
        "flux_dev": 15,
        "flux_schnell": 5,
        "imagen4": 20,
        "seedream_v3": 10,
    },
    "text_to_speech": {
        "elevenlabs": 15,
        "elevenlabs_turbo": 8,
        "elevenlabs_v3": 20,
    },
    "image_understanding": {
        "gemini_describe": 3,
        "gemini_detailed": 5,
        "gemini_classify": 3,
        "gemini_objects": 4,
        "gemini_ocr": 3,
        "gemini_composition": 5,
        "gemini_qa": 4,
    },
    "prompt_generation": {
        "openrouter_video_prompt": 4,
        "openrouter_video_cinematic": 5,
        "openrouter_video_realistic": 4,
        "openrouter_video_artistic": 5,
        "openrouter_video_dramatic": 5,
    },
    "image_to_image": {
        "photon_flash": 8,
        "photon_base": 12,
        "flux_kontext": 15,
        "flux_kontext_multi": 25,
        "seededit_v3": 10,
        "clarity_upscaler": 30,
    },
    "image_to_video": {
        "veo3": 300,
        "veo3_fast": 180,
        "veo2": 240,
        "hailuo": 60,
        "kling": 90,
    },
    "add_audio": {
        "thinksound": 45,
    },
    "upscale_video": {
        "topaz": 120,
    }
}

# File format mappings
SUPPORTED_FORMATS = {
    "image": [".jpg", ".jpeg", ".png", ".webp"],
    "video": [".mp4", ".mov", ".avi", ".webm"]
}

# Default configuration
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