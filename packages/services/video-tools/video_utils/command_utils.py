"""
Shared utilities for AI analysis CLI commands.

This module extracts common patterns from ai_analysis_commands.py to eliminate
code duplication and improve maintainability.
"""

from pathlib import Path
from typing import Optional, Tuple, List, Callable, Dict, Any, TypeVar
from dataclasses import dataclass

from .gemini_analyzer import check_gemini_requirements
from .ai_utils import save_analysis_result
from .file_utils import find_video_files, find_audio_files, find_image_files


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class AnalysisConfig:
    """Configuration for an analysis operation."""
    analysis_type: str
    detailed: bool = False
    include_timestamps: bool = True
    speaker_identification: bool = True
    questions: Optional[List[str]] = None


@dataclass
class PathConfig:
    """Resolved input/output paths."""
    input_dir: Path
    output_dir: Path
    output_file: Optional[Path]
    files: List[Path]


# ============================================================================
# Gemini Setup Utilities
# ============================================================================

def check_and_report_gemini_status() -> bool:
    """
    Check Gemini availability and print detailed status messages.

    Returns:
        True if Gemini is ready, False otherwise

    Usage:
        if not check_and_report_gemini_status():
            return
    """
    gemini_ready, message = check_gemini_requirements()
    if not gemini_ready:
        print(f"❌ Gemini not available: {message}")
        if "not installed" in message:
            print("📥 Install with: pip install google-generativeai")
        if "not set" in message:
            print("🔑 Set API key: export GEMINI_API_KEY=your_api_key")
            print("🌐 Get API key: https://aistudio.google.com/app/apikey")
        return False
    print("✅ Gemini API ready")
    return True


# ============================================================================
# Path Resolution Utilities
# ============================================================================

def setup_paths(
    input_path: Optional[str],
    output_path: Optional[str],
    file_finder: Callable[[Path], List[Path]],
    media_type: str,
    supported_extensions: set
) -> Optional[PathConfig]:
    """
    Set up and validate input/output paths, find media files.

    Args:
        input_path: Optional input file or directory path
        output_path: Optional output file or directory path
        file_finder: Function to find files (e.g., find_video_files)
        media_type: Type description for messages (e.g., "video", "audio")
        supported_extensions: Set of supported file extensions

    Returns:
        PathConfig with resolved paths and files, or None if setup fails
    """
    # Handle input path
    if input_path:
        input_path_obj = Path(input_path)
        if not input_path_obj.exists():
            print(f"❌ Input path not found: {input_path}")
            return None

        if input_path_obj.is_file():
            if input_path_obj.suffix.lower() not in supported_extensions:
                print(f"❌ File is not a supported {media_type} format: {input_path}")
                print(f"💡 Supported formats: {', '.join(sorted(supported_extensions))}")
                return None
            files = [input_path_obj]
            input_dir = input_path_obj.parent
        else:
            input_dir = input_path_obj
            files = file_finder(input_dir)
    else:
        input_dir = Path('input')
        if not input_dir.exists():
            print("📁 Input directory 'input' not found")
            print(f"💡 Create an 'input' directory and place your {media_type} files there")
            return None
        files = file_finder(input_dir)

    if not files:
        print(f"📁 No {media_type} files found")
        return None

    # Handle output path
    if output_path:
        output_path_obj = Path(output_path)
        # Treat as file output only if: single file, has suffix, and path doesn't exist as directory
        is_file_output = (
            len(files) == 1
            and output_path_obj.suffix
            and not output_path_obj.is_dir()
        )
        if is_file_output:
            # Single file with specific output file
            output_dir = output_path_obj.parent
            output_file = output_path_obj
        else:
            # Directory output
            output_dir = output_path_obj
            output_file = None
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        output_file = None

    return PathConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        output_file=output_file,
        files=files
    )


# ============================================================================
# Analysis Type Selection
# ============================================================================

def select_analysis_type(
    analysis_types: Dict[str, Tuple[str, str]],
    default_key: str = '1'
) -> Optional[str]:
    """
    Display analysis type menu and get user selection.

    Args:
        analysis_types: Dict mapping keys to (type_name, description) tuples
        default_key: Default selection if user presses Enter

    Returns:
        Selected analysis type name, or None if invalid
    """
    print("\n🎯 Available analysis types:")
    for key, (type_name, description) in analysis_types.items():
        print(f"   {key}. {description}")

    try:
        choice = input(f"\n📝 Select analysis type (default={default_key}): ").strip()
        if not choice:
            choice = default_key

        if choice not in analysis_types:
            print("❌ Invalid selection, using default")
            choice = default_key

        analysis_type, description = analysis_types[choice]
        print(f"📋 Selected: {description}")
        return analysis_type

    except EOFError:
        # Non-interactive mode - use default
        print(f"📋 Using default: {analysis_types[default_key][1]}")
        return analysis_types[default_key][0]
    except KeyboardInterrupt:
        # User cancelled
        print("\n👋 Operation cancelled.")
        return None


def get_analysis_options(analysis_type: str) -> Optional[AnalysisConfig]:
    """
    Get additional options for the selected analysis type.

    Args:
        analysis_type: The selected analysis type

    Returns:
        AnalysisConfig with user-selected options, or None if cancelled
    """
    config = AnalysisConfig(analysis_type=analysis_type)

    try:
        if analysis_type in ['description', 'objects']:
            detailed = input("📖 Detailed analysis? (y/N): ").strip().lower()
            config.detailed = (detailed == 'y')

        elif analysis_type == 'transcription':
            timestamps = input("⏰ Include timestamps? (Y/n): ").strip().lower()
            config.include_timestamps = (timestamps != 'n')
            speaker = input("👥 Speaker identification? (Y/n): ").strip().lower()
            config.speaker_identification = (speaker != 'n')

        elif analysis_type == 'qa':
            print("\n❓ Enter questions (one per line, empty line to finish):")
            questions = []
            while True:
                q = input("   Question: ").strip()
                if not q:
                    break
                questions.append(q)
            config.questions = questions if questions else None

    except EOFError:
        pass  # Non-interactive mode - use defaults
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled.")
        return None

    return config


# ============================================================================
# Result Display Utilities
# ============================================================================

# Mapping of analysis types to their result keys
RESULT_KEY_MAP = {
    'description': 'description',
    'transcription': 'transcription',
    'scenes': 'scene_analysis',
    'extraction': 'key_info',
    'qa': 'answers',
    'content_analysis': 'analysis',
    'events': 'events',
    'classification': 'classification',
    'objects': 'objects',
    'text': 'extracted_text',
    'composition': 'composition_analysis',
}


def show_result_preview(
    result: Dict[str, Any],
    analysis_type: str,
    max_length: int = 200
) -> None:
    """
    Display a truncated preview of the analysis result.

    Args:
        result: Analysis result dictionary
        analysis_type: Type of analysis performed
        max_length: Maximum preview length
    """
    key = RESULT_KEY_MAP.get(analysis_type)
    if not key or key not in result:
        return

    content = result[key]
    if len(content) > max_length:
        preview = content[:max_length] + "..."
    else:
        preview = content

    print(f"📋 Preview: '{preview}'")


def print_results_summary(
    successful: int,
    failed: int,
    output_dir: Optional[Path] = None
) -> None:
    """Print analysis results summary."""
    print(f"\n📊 Results: {successful} successful | {failed} failed")

    if successful > 0:
        if output_dir:
            print(f"📁 Output saved to: {output_dir}")
        print("🎉 Analysis complete!")


# ============================================================================
# File Processing Loop
# ============================================================================

T = TypeVar('T')


def process_files_with_progress(
    files: List[Path],
    analyzer_fn: Callable[[Path], Optional[Dict[str, Any]]],
    save_fn: Callable[[Dict[str, Any], Path], bool],
    output_dir: Path,
    output_suffix: str,
    media_emoji: str = "📄",
    analysis_type: str = "analysis"
) -> Tuple[int, int]:
    """
    Process multiple files with progress reporting.

    Args:
        files: List of files to process
        analyzer_fn: Function that takes a file path and returns result dict
        save_fn: Function that saves result to output path
        output_dir: Directory for output files
        output_suffix: Suffix for output filenames (e.g., "_description")
        media_emoji: Emoji to show for each file
        analysis_type: Type name for preview display

    Returns:
        Tuple of (successful_count, failed_count)
    """
    successful = 0
    failed = 0
    total = len(files)

    for i, file_path in enumerate(files, 1):
        print(f"\n{media_emoji} Processing: {file_path.name} ({i}/{total})")

        try:
            result = analyzer_fn(file_path)

            if result:
                output_file = output_dir / f"{file_path.stem}{output_suffix}"
                if save_fn(result, output_file):
                    successful += 1
                    show_result_preview(result, analysis_type)
                else:
                    failed += 1
            else:
                print(f"❌ Analysis for {file_path.name} returned no result")
                failed += 1

        except Exception as e:
            print(f"❌ Analysis failed for {file_path.name}: {e}")
            failed += 1

    return successful, failed
