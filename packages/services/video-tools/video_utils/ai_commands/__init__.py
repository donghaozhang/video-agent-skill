"""
AI analysis commands package.

Provides modular CLI commands for video, audio, and image analysis using Google Gemini.

This package contains:
- video_commands: Video analysis, transcription, and description
- audio_commands: Audio analysis, transcription, and description
- image_commands: Image analysis, description, OCR, and classification
"""

from .video_commands import (
    cmd_analyze_videos,
    cmd_transcribe_videos,
    cmd_describe_videos,
    cmd_describe_videos_with_params,
    cmd_transcribe_videos_with_params,
    cmd_detailed_timeline,
    cmd_detailed_timeline_with_params,
)
from .audio_commands import (
    cmd_analyze_audio,
    cmd_transcribe_audio,
    cmd_describe_audio,
    cmd_analyze_audio_with_params,
)
from .image_commands import (
    cmd_analyze_images,
    cmd_describe_images,
    cmd_extract_text,
    cmd_analyze_images_with_params,
)

__all__ = [
    # Video commands
    'cmd_analyze_videos',
    'cmd_transcribe_videos',
    'cmd_describe_videos',
    'cmd_describe_videos_with_params',
    'cmd_transcribe_videos_with_params',
    'cmd_detailed_timeline',
    'cmd_detailed_timeline_with_params',
    # Audio commands
    'cmd_analyze_audio',
    'cmd_transcribe_audio',
    'cmd_describe_audio',
    'cmd_analyze_audio_with_params',
    # Image commands
    'cmd_analyze_images',
    'cmd_describe_images',
    'cmd_extract_text',
    'cmd_analyze_images_with_params',
]
