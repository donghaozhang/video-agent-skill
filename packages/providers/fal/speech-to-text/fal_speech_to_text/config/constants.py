"""Constants for FAL speech-to-text models."""

# Model endpoints
MODEL_ENDPOINTS = {
    "scribe_v2": "fal-ai/elevenlabs/speech-to-text/scribe-v2",
}

# Display names for UI/CLI
MODEL_DISPLAY_NAMES = {
    "scribe_v2": "ElevenLabs Scribe v2",
}

# Pricing structure
MODEL_PRICING = {
    "scribe_v2": {
        "per_minute": 0.008,
        "keyterms_surcharge": 0.30,  # 30% additional when using keyterms
    },
}

# Default values
MODEL_DEFAULTS = {
    "scribe_v2": {
        "language_code": None,  # Auto-detect
        "diarize": True,
        "tag_audio_events": True,
    },
}

# Input requirements
INPUT_REQUIREMENTS = {
    "scribe_v2": {
        "required": ["audio_url"],
        "optional": ["language_code", "diarize", "tag_audio_events", "keyterms"],
    },
}

# Supported language codes (ISO 639-3)
SUPPORTED_LANGUAGES = [
    "eng",  # English
    "spa",  # Spanish
    "fra",  # French
    "deu",  # German
    "ita",  # Italian
    "por",  # Portuguese
    "nld",  # Dutch
    "pol",  # Polish
    "rus",  # Russian
    "jpn",  # Japanese
    "kor",  # Korean
    "cmn",  # Mandarin Chinese
    "ara",  # Arabic
    "hin",  # Hindi
    "ben",  # Bengali
    "vie",  # Vietnamese
    "tur",  # Turkish
    "ukr",  # Ukrainian
    "tha",  # Thai
    "ind",  # Indonesian
    # ... 99 total languages supported
]

# Model categories
MODEL_CATEGORIES = {
    "transcription": ["scribe_v2"],
    "diarization": ["scribe_v2"],
}

# Model recommendations
MODEL_RECOMMENDATIONS = {
    "quality": "scribe_v2",
    "speed": "scribe_v2",
    "diarization": "scribe_v2",
    "multilingual": "scribe_v2",
}

# Processing time estimates (seconds per minute of audio)
PROCESSING_TIME_ESTIMATES = {
    "scribe_v2": 5,  # ~5 seconds per minute of audio
}
