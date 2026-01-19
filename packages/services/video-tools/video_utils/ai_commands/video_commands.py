"""
Video analysis commands using Google Gemini and FAL.

Provides CLI commands for video description, transcription, scene analysis,
detailed timeline analysis, and key information extraction.
"""

import os
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


# Detailed timeline prompt for second-by-second analysis
DETAILED_TIMELINE_PROMPT = """Analyze this video and provide an extremely detailed second-by-second or few-seconds breakdown.

For EVERY 2-5 second interval throughout the entire video, provide:

## Timeline Format (use this exact format):

### [MM:SS - MM:SS] Scene Title
- **Visual**: What is shown on screen (people, graphics, text overlays, locations)
- **Audio**: What is being said (transcribe key dialogue) or sounds heard
- **Action**: What is happening, movements, transitions
- **On-screen text**: Any chyrons, lower-thirds, graphics text

## Requirements:
1. Cover the ENTIRE video from start to finish
2. Use 2-5 second intervals (more granular during important moments)
3. Transcribe ALL spoken dialogue accurately
4. Note ALL on-screen graphics and text
5. Identify ALL people who appear
6. Note camera changes, cuts, and transitions
7. Include mood/tone shifts

## Additional Sections to Include:
- **Complete Transcript**: Full word-for-word transcript with speaker labels and timestamps
- **People Directory**: List of all individuals with descriptions and when they appear
- **Graphics/Text Log**: All on-screen text and graphics with timestamps
- **Key Quotes**: Most important statements with exact timestamps

Be extremely thorough - this should be a complete second-by-second record of everything in the video."""

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
    if not config:
        return

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
    if not config:
        return

    from ..gemini_analyzer import GeminiVideoAnalyzer
    gemini_analyzer = GeminiVideoAnalyzer()

    def analyzer(file_path: Path):
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
    if not config:
        return

    from ..gemini_analyzer import GeminiVideoAnalyzer
    gemini_analyzer = GeminiVideoAnalyzer()

    def analyzer(file_path: Path):
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
        if not config:
            return
    else:
        # Default to detailed for specific formats (json, txt)
        from ..command_utils import AnalysisConfig
        config = AnalysisConfig(analysis_type='description', detailed=True)

    from ..gemini_analyzer import GeminiVideoAnalyzer
    gemini_analyzer = GeminiVideoAnalyzer()

    def analyzer(file_path: Path):
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
        if not config:
            return
    else:
        # Default options for specific formats
        from ..command_utils import AnalysisConfig
        config = AnalysisConfig(analysis_type='transcription', include_timestamps=True)

    from ..gemini_analyzer import GeminiVideoAnalyzer
    gemini_analyzer = GeminiVideoAnalyzer()

    def analyzer(file_path: Path):
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


# =============================================================================
# Detailed Timeline Analysis Commands (FAL + Gemini support)
# =============================================================================

TIMELINE_PROVIDER_OPTIONS = {
    '1': ('fal', 'google/gemini-3-pro-preview', 'FAL + Gemini 3 Pro Preview (Recommended)'),
    '2': ('fal', 'google/gemini-2.5-pro', 'FAL + Gemini 2.5 Pro'),
    '3': ('fal', 'google/gemini-2.5-flash', 'FAL + Gemini 2.5 Flash (Faster)'),
    '4': ('gemini', 'gemini-2.0-flash-exp', 'Gemini Direct (Local files, no upload)'),
}


def _select_timeline_provider() -> tuple:
    """Let user select provider and model for timeline analysis.

    Returns:
        Tuple of (provider, model) or (None, None) if cancelled
    """
    print("\n📡 Select AI Provider and Model:")
    for key, (provider, model, desc) in TIMELINE_PROVIDER_OPTIONS.items():
        print(f"   {key}. {desc}")
    print("   0. Cancel")

    choice = input("\nSelect option [1]: ").strip() or '1'

    if choice == '0':
        return None, None

    if choice in TIMELINE_PROVIDER_OPTIONS:
        provider, model, _ = TIMELINE_PROVIDER_OPTIONS[choice]
        return provider, model

    print("Invalid choice, using default (FAL + Gemini 3 Pro)")
    return 'fal', 'google/gemini-3-pro-preview'


def _analyze_with_fal(video_path: Path, model: str) -> dict:
    """Analyze video using FAL OpenRouter API.

    Args:
        video_path: Path to video file
        model: Model ID (e.g., 'google/gemini-3-pro-preview')

    Returns:
        Analysis result dictionary
    """
    try:
        import fal_client
    except ImportError:
        raise ImportError("FAL client not installed. Run: pip install fal-client")

    fal_key = os.getenv('FAL_KEY')
    if not fal_key:
        raise ValueError("FAL_KEY environment variable not set")

    # Upload to FAL storage
    print(f"   Uploading {video_path.name} to FAL storage...")
    video_url = fal_client.upload_file(str(video_path))
    print(f"   Upload complete: {video_url[:50]}...")

    # Prepare request
    input_params = {
        "video_url": video_url,
        "prompt": DETAILED_TIMELINE_PROMPT,
        "model": model,
    }

    # Enable reasoning for models that require it
    reasoning_models = ["google/gemini-2.5-pro", "google/gemini-3-pro-preview"]
    if model in reasoning_models:
        input_params["reasoning"] = True

    print(f"   Analyzing with {model}...")
    result = fal_client.subscribe(
        "openrouter/router/video/enterprise",
        arguments=input_params
    )

    return {
        'timeline': result.get('output', ''),
        'analysis_type': 'detailed_timeline',
        'provider': 'fal',
        'model': model,
        'usage': result.get('usage', {}),
    }


def _analyze_with_gemini(video_path: Path, model: str = 'gemini-2.0-flash-exp') -> dict:
    """Analyze video using Gemini direct API.

    Args:
        video_path: Path to video file
        model: Gemini model name

    Returns:
        Analysis result dictionary
    """
    from ..gemini_analyzer import GeminiVideoAnalyzer

    # Use custom prompt via the analyzer
    import google.generativeai as genai

    analyzer = GeminiVideoAnalyzer()

    print(f"   Uploading {video_path.name} to Gemini...")
    file_id = analyzer.upload_video(video_path)
    video_file = genai.get_file(file_id)

    print(f"   Analyzing with {model}...")
    response = analyzer.model.generate_content([video_file, DETAILED_TIMELINE_PROMPT])

    # Cleanup
    genai.delete_file(file_id)

    return {
        'timeline': response.text,
        'analysis_type': 'detailed_timeline',
        'provider': 'gemini',
        'model': model,
    }


def _save_timeline_result(result: dict, output_path: Path) -> bool:
    """Save detailed timeline result as markdown.

    Args:
        result: Analysis result with 'timeline' key
        output_path: Output path (without extension)

    Returns:
        True if successful
    """
    import json
    from datetime import datetime

    try:
        md_file = output_path.with_suffix('.md')
        json_file = output_path.with_suffix('.json')

        # Save markdown
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Detailed Video Timeline Analysis\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Provider**: {result.get('provider', 'unknown')}\n")
            f.write(f"**Model**: {result.get('model', 'unknown')}\n")
            if result.get('usage'):
                usage = result['usage']
                f.write(f"**Tokens**: {usage.get('total_tokens', 'N/A')}\n")
                f.write(f"**Cost**: ${usage.get('cost', 'N/A')}\n")
            f.write("\n---\n\n")
            f.write(result.get('timeline', ''))

        print(f"   Saved: {md_file.name}")

        # Save JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)

        print(f"   Saved: {json_file.name}")

        return True

    except Exception as e:
        print(f"   Error saving: {e}")
        return False


def cmd_detailed_timeline() -> None:
    """Generate detailed second-by-second video timeline analysis.

    Supports both FAL (with Gemini 2.5/3 Pro) and Gemini direct providers.
    Creates comprehensive timeline with transcripts, people directory, and quotes.
    """
    print("🎬 DETAILED VIDEO TIMELINE - Second-by-Second Analysis")
    print("=" * 60)
    print("Creates comprehensive timeline with:")
    print("  - 2-5 second interval breakdowns")
    print("  - Complete transcript with speaker labels")
    print("  - People directory with timestamps")
    print("  - All on-screen text and graphics")
    print("  - Key quotes with timestamps")

    # Select provider
    provider, model = _select_timeline_provider()
    if not provider:
        print("Cancelled.")
        return

    # Check requirements based on provider
    if provider == 'fal':
        if not os.getenv('FAL_KEY'):
            print("\n❌ FAL_KEY environment variable not set")
            print("   Set it in your .env file or export FAL_KEY=your_key")
            return
    else:
        if not check_and_report_gemini_status():
            return

    # Setup paths
    paths = setup_paths(None, None, find_video_files, "video", VIDEO_EXTENSIONS)
    if not paths:
        return

    _print_video_list(paths.files)

    print(f"\n🚀 Starting detailed timeline analysis...")
    print(f"   Provider: {provider}")
    print(f"   Model: {model}")

    successful = 0
    failed = 0

    for i, video_file in enumerate(paths.files, 1):
        print(f"\n[{i}/{len(paths.files)}] Processing: {video_file.name}")

        try:
            if provider == 'fal':
                result = _analyze_with_fal(video_file, model)
            else:
                result = _analyze_with_gemini(video_file, model)

            # Save result
            output_name = video_file.stem + "_detailed_timeline"
            output_path = paths.output_dir / output_name

            if _save_timeline_result(result, output_path):
                successful += 1
                print(f"   ✅ Complete")
            else:
                failed += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1

    print_results_summary(successful, failed, paths.output_dir)


def cmd_detailed_timeline_with_params(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    provider: str = 'fal',
    model: str = 'google/gemini-3-pro-preview'
) -> Optional[dict]:
    """Generate detailed timeline with explicit parameters.

    Args:
        input_path: Path to video file or directory
        output_path: Path to output directory
        provider: 'fal' or 'gemini'
        model: Model ID (e.g., 'google/gemini-3-pro-preview')

    Returns:
        Analysis result dictionary or None on failure
    """
    print(f"🎬 DETAILED TIMELINE - {provider.upper()} + {model}")
    print("=" * 60)

    # Validate provider requirements
    if provider == 'fal':
        if not os.getenv('FAL_KEY'):
            print("❌ FAL_KEY not set")
            return None
    else:
        if not check_and_report_gemini_status():
            return None

    paths = setup_paths(input_path, output_path, find_video_files, "video", VIDEO_EXTENSIONS)
    if not paths:
        return None

    print(f"📹 Found {len(paths.files)} video file(s)")
    print(f"📁 Output: {paths.output_dir}")

    results = []
    successful = 0
    failed = 0

    for i, video_file in enumerate(paths.files, 1):
        print(f"\n[{i}/{len(paths.files)}] {video_file.name}")

        try:
            if provider == 'fal':
                result = _analyze_with_fal(video_file, model)
            else:
                result = _analyze_with_gemini(video_file, model)

            output_name = video_file.stem + "_detailed_timeline"
            output_file = paths.output_dir / output_name

            if _save_timeline_result(result, output_file):
                successful += 1
                results.append(result)
            else:
                failed += 1

        except Exception as e:
            print(f"   ❌ {e}")
            failed += 1

    print_results_summary(successful, failed, paths.output_dir)

    return results[0] if len(results) == 1 else results if results else None
