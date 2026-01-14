"""
Video analysis commands using Google Gemini.

Provides CLI commands for video description, transcription, scene analysis,
and key information extraction.
"""

from pathlib import Path
from typing import Optional

from ..command_utils import (
    check_and_report_gemini_status,
    setup_paths,
    select_analysis_type,
    get_analysis_options,
    process_files_with_progress,
    print_results_summary,
)
from ..file_utils import find_video_files
from ..ai_utils import analyze_video_file, save_analysis_result
from ..core import get_video_info

# Supported video extensions (keep in sync with file_utils.py)
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}


def _save_result_with_format(result: dict, output_path: Path, format_type: str, content_key: str) -> bool:
    """Save analysis result based on format_type.

    Args:
        result: Analysis result dictionary
        output_path: Base output path (without extension)
        format_type: Output format ('describe-video', 'json', 'txt')
        content_key: Key in result dict containing main content

    Returns:
        True if successful, False otherwise
    """
    import json

    try:
        json_file = output_path.with_suffix('.json')
        txt_file = output_path.with_suffix('.txt')

        # Save JSON if format allows
        if format_type in ['describe-video', 'json']:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved JSON: {json_file.name}")

        # Save TXT if format allows
        if format_type in ['describe-video', 'txt']:
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"Analysis Result\n")
                f.write("=" * 50 + "\n\n")
                if content_key in result:
                    f.write(result[content_key])
                else:
                    f.write(str(result))
                f.write(f"\n\nGenerated: {result.get('timestamp', 'Unknown')}")
            print(f"💾 Saved TXT: {txt_file.name}")

        return True

    except Exception as e:
        print(f"❌ Error saving results: {e}")
        return False

# Analysis types for video
VIDEO_ANALYSIS_TYPES = {
    '1': ('description', 'Video Description (summary and overview)'),
    '2': ('transcription', 'Audio Transcription (speech to text)'),
    '3': ('scenes', 'Scene Analysis (timeline breakdown)'),
    '4': ('extraction', 'Key Information Extraction'),
    '5': ('qa', 'Custom Q&A (ask specific questions)'),
}


def _print_video_list(video_files: list) -> None:
    """Print list of found video files with info."""
    print(f"📹 Found {len(video_files)} video file(s):")
    for video in video_files:
        info = get_video_info(video)
        duration_str = f"{info['duration']:.1f}s" if info['duration'] else "unknown"
        file_size = video.stat().st_size / (1024 * 1024)
        print(f"   - {video.name} ({duration_str}, {file_size:.1f}MB)")


def cmd_analyze_videos() -> None:
    """Analyze videos using Google Gemini AI."""
    print("🤖 AI VIDEO ANALYSIS - Google Gemini")
    print("=" * 50)
    print("💡 Analyze video content with AI-powered understanding")

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(None, None, find_video_files, "video", VIDEO_EXTENSIONS)
    if not paths:
        return

    _print_video_list(paths.files)

    analysis_type = select_analysis_type(VIDEO_ANALYSIS_TYPES)
    if not analysis_type:
        return

    config = get_analysis_options(analysis_type)

    print(f"\n🚀 Starting {analysis_type} analysis...")

    def analyzer(file_path: Path):
        return analyze_video_file(
            file_path,
            config.analysis_type,
            questions=config.questions,
            detailed=config.detailed
        )

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix=f"_{analysis_type}_analysis",
        media_emoji="📺",
        analysis_type=analysis_type
    )

    print_results_summary(successful, failed, paths.output_dir)


def cmd_transcribe_videos() -> None:
    """Quick transcription of video audio using Gemini."""
    print("🎤 VIDEO TRANSCRIPTION - Google Gemini")
    print("=" * 50)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(None, None, find_video_files, "video", VIDEO_EXTENSIONS)
    if not paths:
        return

    print(f"📹 Found {len(paths.files)} video file(s)")

    config = get_analysis_options('transcription')

    def analyzer(file_path: Path):
        from ..gemini_analyzer import GeminiVideoAnalyzer
        gemini_analyzer = GeminiVideoAnalyzer()
        return gemini_analyzer.transcribe_video(file_path, config.include_timestamps)

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix="_transcription",
        media_emoji="📺",
        analysis_type="transcription"
    )

    print_results_summary(successful, failed, paths.output_dir)


def cmd_describe_videos() -> None:
    """Quick description of videos using Gemini."""
    print("📝 VIDEO DESCRIPTION - Google Gemini")
    print("=" * 50)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(None, None, find_video_files, "video", VIDEO_EXTENSIONS)
    if not paths:
        return

    print(f"📹 Found {len(paths.files)} video file(s)")

    config = get_analysis_options('description')

    def analyzer(file_path: Path):
        from ..gemini_analyzer import GeminiVideoAnalyzer
        gemini_analyzer = GeminiVideoAnalyzer()
        return gemini_analyzer.describe_video(file_path, config.detailed)

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix="_description",
        media_emoji="📺",
        analysis_type="description"
    )

    print_results_summary(successful, failed, paths.output_dir)


def cmd_describe_videos_with_params(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    format_type: str = 'describe-video'
) -> None:
    """Enhanced describe-videos command with parameter support.

    Args:
        input_path: Path to input video file or directory
        output_path: Path to output file or directory
        format_type: Output format ('describe-video', 'json', 'txt')
    """
    print("📝 VIDEO DESCRIPTION - Enhanced with Parameters")
    print("=" * 60)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(input_path, output_path, find_video_files, "video", VIDEO_EXTENSIONS)
    if not paths:
        return

    print(f"📹 Found {len(paths.files)} video file(s)")
    print(f"📁 Output directory: {paths.output_dir}")
    print(f"📋 Format: {format_type}")

    # Determine detailed based on format_type
    if format_type == 'describe-video':
        config = get_analysis_options('description')
    else:
        # Default to detailed for specific formats (json, txt)
        from ..command_utils import AnalysisConfig
        config = AnalysisConfig(analysis_type='description', detailed=True)

    def analyzer(file_path: Path):
        from ..gemini_analyzer import GeminiVideoAnalyzer
        gemini_analyzer = GeminiVideoAnalyzer()
        return gemini_analyzer.describe_video(file_path, config.detailed)

    # Custom save function based on format_type
    def save_with_format(result, output_path):
        return _save_result_with_format(result, output_path, format_type, 'description')

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_with_format,
        output_dir=paths.output_dir,
        output_suffix="_description",
        media_emoji="📺",
        analysis_type="description"
    )

    print_results_summary(successful, failed, paths.output_dir)


def cmd_transcribe_videos_with_params(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    format_type: str = 'describe-video'
) -> None:
    """Enhanced transcribe-videos command with parameter support.

    Args:
        input_path: Path to input video file or directory
        output_path: Path to output file or directory
        format_type: Output format ('describe-video', 'json', 'txt')
    """
    print("🎤 VIDEO TRANSCRIPTION - Enhanced with Parameters")
    print("=" * 60)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(input_path, output_path, find_video_files, "video", VIDEO_EXTENSIONS)
    if not paths:
        return

    print(f"📹 Found {len(paths.files)} video file(s)")
    print(f"📁 Output directory: {paths.output_dir}")
    print(f"📋 Format: {format_type}")

    # Determine options based on format_type
    if format_type == 'describe-video':
        config = get_analysis_options('transcription')
    else:
        # Default options for specific formats
        from ..command_utils import AnalysisConfig
        config = AnalysisConfig(analysis_type='transcription', include_timestamps=True)

    def analyzer(file_path: Path):
        from ..gemini_analyzer import GeminiVideoAnalyzer
        gemini_analyzer = GeminiVideoAnalyzer()
        return gemini_analyzer.transcribe_video(file_path, config.include_timestamps)

    # Custom save function based on format_type
    def save_with_format(result, output_path):
        return _save_result_with_format(result, output_path, format_type, 'transcription')

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_with_format,
        output_dir=paths.output_dir,
        output_suffix="_transcription",
        media_emoji="📺",
        analysis_type="transcription"
    )

    print_results_summary(successful, failed, paths.output_dir)
