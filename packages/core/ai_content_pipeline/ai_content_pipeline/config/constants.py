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
    "text_to_video": [
        "sora_2",             # OpenAI Sora 2 (via FAL)
        "sora_2_pro",         # OpenAI Sora 2 Pro (via FAL) - 1080p support
        "kling_2_6_pro",      # Kling Video v2.6 Pro
        "veo3",               # Google Veo 3 (via FAL)
        "veo3_fast",          # Google Veo 3 Fast (via FAL)
        "hailuo_pro",         # MiniMax Hailuo-02 Pro
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
        "veo_3_1_fast",       # Google Veo 3.1 Fast (with audio)
        "veo2",               # Google Veo 2.0
        "hailuo",             # MiniMax Hailuo-02
        "kling",              # Kling Video 2.1
        "kling_2_1",          # Kling Video v2.1
        "kling_2_6_pro",      # Kling Video v2.6 Pro
        "sora_2",             # OpenAI Sora 2
        "sora_2_pro",         # OpenAI Sora 2 Pro
        "seedance_1_5_pro",   # ByteDance Seedance v1.5 Pro
    ],
    "add_audio": [
        "thinksound",         # ThinksSound AI audio generation
    ],
    "upscale_video": [
        "topaz",              # Topaz Video Upscale
    ],
    "avatar": [
        "omnihuman_v1_5",       # ByteDance OmniHuman - audio-driven animation
        "fabric_1_0",           # VEED Fabric - lipsync (image + audio)
        "fabric_1_0_fast",      # VEED Fabric Fast - faster lipsync
        "fabric_1_0_text",      # VEED Fabric - text-to-speech avatar
        "kling_ref_to_video",   # Kling O1 - reference image consistency
        "kling_v2v_reference",  # Kling O1 - style-guided video
        "kling_v2v_edit",       # Kling O1 - targeted video modifications
        "kling_motion_control", # Kling v2.6 - motion transfer from video to image
    ],
    "speech_to_text": [
        "scribe_v2",            # ElevenLabs Scribe v2 via FAL
    ]
}

# Pipeline step types
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
    "text_to_video": {
        "sora_2": 0.40,           # $0.10/sec * 4sec default
        "sora_2_pro": 2.00,       # $0.50/sec * 4sec default (1080p)
        "kling_2_6_pro": 0.35,    # $0.07/sec * 5sec default
        "veo3": 4.00,             # $0.50/sec * 8sec default
        "veo3_fast": 2.00,        # $0.25/sec * 8sec default
        "hailuo_pro": 0.08,       # Fixed per video
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
        "veo_3_1_fast": 1.20,     # $0.15/sec * 8sec (with audio)
        "veo2": 2.50,
        "hailuo": 0.08,
        "kling": 0.10,
        "kling_2_1": 0.50,        # $0.05/sec * 10sec
        "kling_2_6_pro": 1.00,    # $0.10/sec * 10sec
        "sora_2": 0.40,           # $0.10/sec * 4sec
        "sora_2_pro": 2.00,       # $0.50/sec * 4sec (1080p)
        "seedance_1_5_pro": 0.80, # $0.08/sec * 10sec
    },
    "add_audio": {
        "thinksound": 0.05,
    },
    "upscale_video": {
        "topaz": 1.50,
    },
    "avatar": {
        "omnihuman_v1_5": 0.80,        # ~$0.16/sec * 5sec
        "fabric_1_0": 0.75,            # ~$0.15/sec * 5sec
        "fabric_1_0_fast": 0.94,       # +25% for fast mode
        "fabric_1_0_text": 0.75,       # ~$0.15/sec * 5sec
        "kling_ref_to_video": 0.56,    # ~$0.112/sec * 5sec
        "kling_v2v_reference": 0.84,   # ~$0.168/sec * 5sec
        "kling_v2v_edit": 0.84,        # ~$0.168/sec * 5sec
        "kling_motion_control": 0.60,  # ~$0.06/sec * 10sec
    },
    "speech_to_text": {
        "scribe_v2": 0.08,             # ~$0.008/min * 10min average
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
    "text_to_video": {
        "sora_2": 120,            # ~2 min for 4sec video
        "sora_2_pro": 180,        # ~3 min for 4sec video (1080p)
        "kling_2_6_pro": 90,      # ~1.5 min for 5sec video
        "veo3": 300,              # ~5 min for 8sec video
        "veo3_fast": 120,         # ~2 min for 8sec video
        "hailuo_pro": 60,         # ~1 min for 6sec video
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
        "veo_3_1_fast": 120,      # ~2 min for 8sec video
        "veo2": 240,
        "hailuo": 60,
        "kling": 90,
        "kling_2_1": 90,
        "kling_2_6_pro": 120,
        "sora_2": 120,
        "sora_2_pro": 180,
        "seedance_1_5_pro": 90,
    },
    "add_audio": {
        "thinksound": 45,
    },
    "upscale_video": {
        "topaz": 120,
    },
    "avatar": {
        "omnihuman_v1_5": 60,          # 60 seconds for 5s video
        "fabric_1_0": 45,              # 45 seconds for 5s video
        "fabric_1_0_fast": 30,         # 30 seconds (fast mode)
        "fabric_1_0_text": 50,         # 50 seconds (includes TTS)
        "kling_ref_to_video": 90,      # 90 seconds for 5s video
        "kling_v2v_reference": 90,     # 90 seconds for 5s video
        "kling_v2v_edit": 60,          # 60 seconds for editing
        "kling_motion_control": 60,    # 60 seconds for motion transfer
    },
    "speech_to_text": {
        "scribe_v2": 15,               # ~15 seconds for average audio
    }
}

# File format mappings
SUPPORTED_FORMATS = {
    "image": [".jpg", ".jpeg", ".png", ".webp"],
    "video": [".mp4", ".mov", ".avi", ".webm"],
    "audio": [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
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