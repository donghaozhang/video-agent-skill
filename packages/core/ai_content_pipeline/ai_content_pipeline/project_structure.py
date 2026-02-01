"""
Project Structure Utilities for AI Content Pipeline.

This module provides utilities for initializing and organizing project
structures according to the standard input/output folder pattern.

File: packages/core/ai_content_pipeline/ai_content_pipeline/project_structure.py
"""

import fnmatch
import logging
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Default project structure definition
DEFAULT_STRUCTURE = {
    "input": {
        "images": [], "videos": [], "audio": [],
        "pipelines": {
            "video": [], "image": [], "storyboard": [], "analysis": [], "examples": [],
        },
        "prompts": [], "subtitles": [], "text": [], "metadata": [],
    },
    "output": {
        "images": [], "videos": [], "audio": [], "transcripts": [],
        "analysis": [], "pipelines": [], "temp": [],
    },
    "issues": {"todo": [], "implemented": []},
    "docs": [],
}

# Output folder structure definition
OUTPUT_STRUCTURE = {
    "images": [], "videos": [], "audio": [], "transcripts": [],
    "analysis": [], "pipelines": [], "temp": [],
}

# Output file extension/pattern mappings
OUTPUT_FILE_PATTERNS = {
    "images": {
        "extensions": [".png", ".jpg", ".jpeg", ".webp", ".gif"],
        "patterns": ["generated_image_*", "upscaled_*", "grid_*"],
    },
    "videos": {
        "extensions": [".mp4", ".webm", ".mov"],
        "patterns": ["generated_video_*", "motion_*", "avatar_*"],
    },
    "audio": {
        "extensions": [".mp3", ".wav", ".m4a"],
        "patterns": ["generated_audio_*", "tts_*", "voice_*"],
    },
    "transcripts": {
        "extensions": [".srt", ".vtt"],
        "patterns": ["*_transcript*", "*_words.json", "*_raw.json"],
    },
    "analysis": {
        "extensions": [],
        "patterns": ["*_analysis*", "*_timeline*", "*_describe*"],
    },
    "pipelines": {
        "extensions": [".yaml", ".yml"],
        "patterns": ["*_pipeline*", "*_chain*", "*_config*"],
    },
    "temp": {
        "extensions": [".tmp", ".temp"],
        "patterns": ["step_*_output.*"],
    },
}

# File extension mappings for organization
FILE_EXTENSIONS = {
    "images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg"],
    "videos": [".mp4", ".mov", ".webm", ".avi", ".mkv", ".m4v", ".wmv"],
    "audio": [".mp3", ".wav", ".aac", ".m4a", ".ogg", ".flac", ".wma"],
    "pipelines": [".yaml", ".yml"],
    "prompts": [".txt", ".md"],
    "subtitles": [".srt", ".vtt", ".ass", ".sub"],
}


@dataclass
class OrganizeResult:
    """Result of organizing files into project structure."""

    success: bool
    files_moved: int = 0
    files_skipped: int = 0
    errors: List[str] = field(default_factory=list)
    moves: List[Tuple[str, str]] = field(default_factory=list)  # (source, destination)

    def add_move(self, source: str, destination: str) -> None:
        """Record a file move."""
        self.moves.append((source, destination))
        self.files_moved += 1

    def add_error(self, error: str) -> None:
        """Record an error."""
        self.errors.append(error)

    def add_skip(self) -> None:
        """Record a skipped file."""
        self.files_skipped += 1


@dataclass
class InitResult:
    """Result of initializing project structure."""

    success: bool
    directories_created: int = 0
    directories_existed: int = 0
    errors: List[str] = field(default_factory=list)
    created_paths: List[str] = field(default_factory=list)


def get_all_directories(structure: dict, prefix: str = "") -> List[str]:
    """
    Recursively get all directory paths from structure definition.

    Args:
        structure: Nested dict defining folder structure
        prefix: Current path prefix

    Returns:
        List of directory paths to create
    """
    paths = []
    for key, value in structure.items():
        current_path = os.path.join(prefix, key) if prefix else key
        paths.append(current_path)
        if isinstance(value, dict):
            paths.extend(get_all_directories(value, current_path))
    return paths


def init_project(
    root_dir: str = ".",
    structure: Optional[dict] = None,
    dry_run: bool = False
) -> InitResult:
    """
    Initialize project with default directory structure.

    Args:
        root_dir: Root directory for the project
        structure: Custom structure dict (uses DEFAULT_STRUCTURE if None)
        dry_run: If True, only report what would be created

    Returns:
        InitResult with creation details
    """
    result = InitResult(success=True)
    root = Path(root_dir).resolve()
    structure = structure or DEFAULT_STRUCTURE

    # Get all directories to create
    directories = get_all_directories(structure)

    for dir_path in directories:
        full_path = root / dir_path

        if full_path.exists():
            result.directories_existed += 1
        else:
            if not dry_run:
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    result.directories_created += 1
                    result.created_paths.append(str(full_path))
                except OSError as e:
                    logger.exception("Failed to create directory %s", full_path)
                    result.errors.append(f"Failed to create {full_path}: {e}")
                    result.success = False
            else:
                result.directories_created += 1
                result.created_paths.append(str(full_path))

    return result


def get_destination_folder(file_path: Path) -> Optional[str]:
    """
    Determine the destination folder for a file based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        Destination folder path relative to root, or None if unknown type
    """
    ext = file_path.suffix.lower()

    for folder, extensions in FILE_EXTENSIONS.items():
        if ext in extensions:
            return f"input/{folder}"

    return None


def organize_project(
    root_dir: str = ".",
    source_dir: Optional[str] = None,
    dry_run: bool = False,
    recursive: bool = False
) -> OrganizeResult:
    """
    Organize files into the standard project structure.

    Moves files from source directory (or root) into appropriate
    input/ subfolders based on file extension.

    Args:
        root_dir: Root directory of the project
        source_dir: Source directory to scan (defaults to root_dir)
        dry_run: If True, only report what would be moved
        recursive: If True, scan subdirectories

    Returns:
        OrganizeResult with move details
    """
    result = OrganizeResult(success=True)
    root = Path(root_dir).resolve()
    source = Path(source_dir).resolve() if source_dir else root

    # Ensure structure exists
    if not dry_run:
        init_result = init_project(root_dir)
        if not init_result.success:
            result.errors.extend(init_result.errors)
            result.success = False
            return result

    # Scan for files
    if recursive:
        files = list(source.rglob("*"))
    else:
        files = list(source.glob("*"))

    # Filter to files only (not directories)
    files = [f for f in files if f.is_file()]

    # Skip files already in the correct location
    input_dir = root / "input"
    output_dir = root / "output"

    for file_path in files:
        # Skip files already in input/ or output/
        try:
            file_path.relative_to(input_dir)
            result.add_skip()
            continue
        except ValueError:
            pass

        try:
            file_path.relative_to(output_dir)
            result.add_skip()
            continue
        except ValueError:
            pass

        # Determine destination
        dest_folder = get_destination_folder(file_path)

        if dest_folder is None:
            result.add_skip()
            continue

        dest_path = root / dest_folder / file_path.name

        # Check if destination already exists
        if dest_path.exists():
            result.add_error(f"Destination exists, skipping: {file_path.name}")
            result.add_skip()
            continue

        # Move file
        if not dry_run:
            try:
                shutil.move(str(file_path), str(dest_path))
                result.add_move(str(file_path), str(dest_path))
            except (OSError, shutil.Error) as e:
                logger.exception("Failed to move %s to %s", file_path, dest_path)
                result.add_error(f"Failed to move {file_path}: {e}")
                result.success = False
        else:
            result.add_move(str(file_path), str(dest_path))

    return result


def get_output_destination(file_path: Path) -> Optional[str]:
    """
    Determine the output subfolder for a file based on extension and name pattern.

    Args:
        file_path: Path to the file

    Returns:
        Output subfolder name (e.g., "images", "videos"), or None if unknown
    """
    name = file_path.name.lower()
    ext = file_path.suffix.lower()

    for folder, config in OUTPUT_FILE_PATTERNS.items():
        # Check extension match
        if ext in config["extensions"]:
            return folder

        # Check pattern match
        for pattern in config["patterns"]:
            if fnmatch.fnmatch(name, pattern.lower()):
                return folder

    return None


def organize_output(
    root_dir: str = ".",
    dry_run: bool = False
) -> OrganizeResult:
    """
    Organize files in output/ folder into categorized subfolders.

    Moves files from output/ root into appropriate subfolders
    (images/, videos/, audio/, transcripts/, analysis/) based on
    file extension and naming patterns.

    Args:
        root_dir: Root directory of the project
        dry_run: If True, only report what would be moved

    Returns:
        OrganizeResult with move details
    """
    result = OrganizeResult(success=True)
    root = Path(root_dir).resolve()
    output_dir = root / "output"

    if not output_dir.exists():
        result.add_error("Output directory does not exist")
        result.success = False
        return result

    # Ensure output subfolders exist
    if not dry_run:
        for subfolder in OUTPUT_STRUCTURE.keys():
            (output_dir / subfolder).mkdir(exist_ok=True)

    # Get files in output root (not in subfolders)
    for file_path in output_dir.glob("*"):
        if not file_path.is_file():
            continue

        # Determine destination subfolder
        dest_folder = get_output_destination(file_path)

        if dest_folder is None:
            result.add_skip()
            continue

        dest_path = output_dir / dest_folder / file_path.name

        # Check if destination already exists
        if dest_path.exists():
            result.add_error(f"Destination exists, skipping: {file_path.name}")
            result.add_skip()
            continue

        # Move file
        if not dry_run:
            try:
                shutil.move(str(file_path), str(dest_path))
                result.add_move(str(file_path), str(dest_path))
            except (OSError, shutil.Error) as e:
                logger.exception("Failed to move %s to %s", file_path, dest_path)
                result.add_error(f"Failed to move {file_path}: {e}")
                result.success = False
        else:
            result.add_move(str(file_path), str(dest_path))

    return result


def cleanup_temp_files(
    root_dir: str = ".",
    dry_run: bool = False
) -> Tuple[int, List[str]]:
    """
    Clean up temporary and intermediate files from output directory.

    Removes:
    - Files matching step_*_output.* pattern
    - Empty directories in output/

    Args:
        root_dir: Root directory of the project
        dry_run: If True, only report what would be deleted

    Returns:
        Tuple of (files_deleted, list of deleted paths)
    """
    root = Path(root_dir).resolve()
    output_dir = root / "output"

    deleted = []

    if not output_dir.exists():
        return 0, []

    # Find temp files
    temp_patterns = ["step_*_output.*", "*.tmp", "*.temp"]

    for pattern in temp_patterns:
        for temp_file in output_dir.rglob(pattern):
            if temp_file.is_file():
                if not dry_run:
                    try:
                        temp_file.unlink()
                        deleted.append(str(temp_file))
                    except OSError as e:
                        logger.warning("Failed to delete %s: %s", temp_file, e)
                else:
                    deleted.append(str(temp_file))

    # Remove empty directories
    for dirpath in sorted(output_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            if not dry_run:
                try:
                    dirpath.rmdir()
                    deleted.append(str(dirpath))
                except OSError as e:
                    logger.warning("Failed to remove directory %s: %s", dirpath, e)
            else:
                deleted.append(str(dirpath))

    return len(deleted), deleted


def get_structure_info(root_dir: str = ".") -> Dict[str, Any]:
    """
    Get information about the current project structure.

    Args:
        root_dir: Root directory of the project

    Returns:
        Dict with structure information
    """
    root = Path(root_dir).resolve()

    info: Dict[str, Any] = {
        "root": str(root),
        "has_structure": False,
        "directories": {},
        "file_counts": {},
        "output_counts": {},
    }

    # Check for key directories
    key_dirs = ["input", "output", "input/images", "input/videos",
                "input/audio", "input/pipelines"]

    existing_dirs = 0
    for dir_name in key_dirs:
        dir_path = root / dir_name
        exists = dir_path.exists()
        info["directories"][dir_name] = exists
        if exists:
            existing_dirs += 1

    info["has_structure"] = existing_dirs >= 2

    # Count files in each input folder
    input_dir = root / "input"
    if input_dir.exists():
        for folder in ["images", "videos", "audio", "pipelines", "prompts"]:
            folder_path = input_dir / folder
            if folder_path.exists():
                count = len([p for p in folder_path.glob("*") if p.is_file()])
                info["file_counts"][folder] = count

    # Count output files by category
    output_dir = root / "output"
    if output_dir.exists():
        # Count files in output root (unorganized)
        root_files = len([f for f in output_dir.glob("*") if f.is_file()])
        info["output_counts"]["root_files"] = root_files

        # Count files in each output subfolder
        for folder in ["images", "videos", "audio", "transcripts", "analysis", "pipelines"]:
            folder_path = output_dir / folder
            if folder_path.exists():
                count = len([p for p in folder_path.rglob("*") if p.is_file()])
                info["output_counts"][folder] = count

        # Total output files
        info["file_counts"]["output"] = len([p for p in output_dir.rglob("*") if p.is_file()])

    return info
