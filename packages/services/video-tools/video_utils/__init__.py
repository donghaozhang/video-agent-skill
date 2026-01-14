"""
Video utilities package for video and audio manipulation.

Enhanced with class-based architecture for better maintainability and extensibility.

This package provides both legacy function-based utilities and new class-based processors:

LEGACY FUNCTION-BASED (for backward compatibility):
- Video processing and cutting
- Audio manipulation and mixing
- Subtitle generation and overlay
- File format support and validation

NEW CLASS-BASED ARCHITECTURE:
- Enhanced video and audio processors
- Command controllers for organized operations
- AI analysis with Gemini and Whisper
- Unified command dispatcher for all operations
"""

# Legacy function-based imports (for backward compatibility)
from .core import check_ffmpeg, check_ffprobe, get_video_info
from .file_utils import find_video_files, find_audio_files, find_image_files
from .video_processor import cut_video_duration
from .audio_processor import (
    add_audio_to_video, 
    extract_audio_from_video, 
    mix_multiple_audio_files, 
    concatenate_multiple_audio_files
)
from .subtitle_generator import (
    generate_srt_subtitle_file,
    generate_vtt_subtitle_file,
    generate_subtitle_for_video,
    add_subtitles_to_video,
    add_text_subtitles_to_video
)
from .interactive import interactive_audio_selection, interactive_multiple_audio_selection

# Enhanced class-based imports
from .enhanced_video_processor import VideoProcessor
from .enhanced_audio_processor import AudioProcessor
from .base_controller import BaseController
from .media_processing_controller import MediaProcessingController
from .command_dispatcher import CommandDispatcher

# AI analysis imports (split from large video_understanding.py)
from .gemini_analyzer import GeminiVideoAnalyzer, check_gemini_requirements
from .whisper_transcriber import WhisperTranscriber, check_whisper_requirements
from .ai_utils import (
    analyze_video_file,
    analyze_audio_file,
    analyze_image_file,
    save_analysis_result,
    transcribe_with_whisper,
    batch_transcribe_whisper,
    analyze_media_comprehensively,
    check_ai_requirements,
    print_ai_status
)

# Analyzer abstraction layer (for multi-provider support)
from .analyzer_protocol import MediaAnalyzerProtocol
from .analyzer_factory import AnalyzerFactory, get_analyzer, print_provider_status

# Optional: FAL analyzer (only if fal-client is installed)
try:
    from .fal_video_analyzer import FalVideoAnalyzer, check_fal_requirements
except ImportError:
    FalVideoAnalyzer = None
    check_fal_requirements = None

__all__ = [
    # Legacy function-based utilities (for backward compatibility)
    'check_ffmpeg', 'check_ffprobe', 'get_video_info',
    'find_video_files', 'find_audio_files', 'find_image_files',
    'cut_video_duration',
    'add_audio_to_video', 'extract_audio_from_video',
    'mix_multiple_audio_files', 'concatenate_multiple_audio_files',
    'generate_srt_subtitle_file', 'generate_vtt_subtitle_file',
    'generate_subtitle_for_video', 'add_subtitles_to_video', 'add_text_subtitles_to_video',
    'interactive_audio_selection', 'interactive_multiple_audio_selection',

    # Enhanced class-based architecture
    'VideoProcessor', 'AudioProcessor',
    'BaseController', 'MediaProcessingController', 'CommandDispatcher',

    # AI analysis classes and functions
    'GeminiVideoAnalyzer', 'WhisperTranscriber',
    'check_gemini_requirements', 'check_whisper_requirements',
    'analyze_video_file', 'analyze_audio_file', 'analyze_image_file',
    'save_analysis_result', 'transcribe_with_whisper', 'batch_transcribe_whisper',
    'analyze_media_comprehensively', 'check_ai_requirements', 'print_ai_status',

    # Analyzer abstraction layer (multi-provider support)
    'MediaAnalyzerProtocol',
    'AnalyzerFactory', 'get_analyzer', 'print_provider_status',
    'FalVideoAnalyzer', 'check_fal_requirements',
]