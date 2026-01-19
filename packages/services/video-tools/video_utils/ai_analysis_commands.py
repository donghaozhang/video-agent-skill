"""
AI analysis command implementations using Google Gemini.

NOTE: This module re-exports from ai_commands package for backwards compatibility.
For new code, import directly from video_utils.ai_commands.

Example:
    # Old way (still works)
    from video_utils.ai_analysis_commands import cmd_analyze_videos

    # New way (preferred)
    from video_utils.ai_commands import cmd_analyze_videos
"""

# Re-export all commands for backwards compatibility
from .ai_commands import (
    # Video commands
    cmd_analyze_videos,
    cmd_transcribe_videos,
    cmd_describe_videos,
    cmd_describe_videos_with_params,
    cmd_transcribe_videos_with_params,
    # Audio commands
    cmd_analyze_audio,
    cmd_transcribe_audio,
    cmd_describe_audio,
    cmd_analyze_audio_with_params,
    # Image commands
    cmd_analyze_images,
    cmd_describe_images,
    cmd_extract_text,
    cmd_analyze_images_with_params,
)

__all__ = [
    'cmd_analyze_videos',
    'cmd_transcribe_videos',
    'cmd_describe_videos',
    'cmd_describe_videos_with_params',
    'cmd_transcribe_videos_with_params',
    'cmd_analyze_audio',
    'cmd_transcribe_audio',
    'cmd_describe_audio',
    'cmd_analyze_audio_with_params',
    'cmd_analyze_images',
    'cmd_describe_images',
    'cmd_extract_text',
    'cmd_analyze_images_with_params',
]
