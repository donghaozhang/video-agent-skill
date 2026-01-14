# Refactoring Plan: ai_analysis_commands.py (1633 lines)

## Overview

The `packages/services/video-tools/video_utils/ai_analysis_commands.py` file has grown to **1633 lines** and violates the project guideline of maximum 500 lines per file. This plan outlines a systematic refactoring to improve maintainability, testability, and code organization.

---

## Current State Analysis

### File Structure (ai_analysis_commands.py)
- **Lines 1-19**: Imports
- **Lines 21-161**: `cmd_analyze_videos()` - Video analysis with Gemini
- **Lines 163-227**: `cmd_transcribe_videos()` - Video transcription
- **Lines 229-294**: `cmd_describe_videos()` - Video description
- **Lines 296-448**: `cmd_describe_videos_with_params()` - Enhanced video description with parameters
- **Lines 450-621**: `cmd_transcribe_videos_with_params()` - Enhanced transcription with parameters
- **Lines 623-748**: `cmd_analyze_audio()` - Comprehensive audio analysis
- **Lines 750-815**: `cmd_transcribe_audio()` - Audio transcription
- **Lines 817-882**: `cmd_describe_audio()` - Audio description
- **Lines 884-1009**: `cmd_analyze_images()` - Comprehensive image analysis
- **Lines 1011-1076**: `cmd_describe_images()` - Image description
- **Lines 1078-1148**: `cmd_extract_text()` - OCR text extraction
- **Lines 1150-1393**: `cmd_analyze_audio_with_params()` - Enhanced audio analysis with parameters
- **Lines 1395-1633**: `cmd_analyze_images_with_params()` - Enhanced image analysis with parameters

### Identified Concerns
1. **Single Responsibility Violation**: One file handles video, audio, and image analysis commands
2. **Massive Code Duplication**: Nearly identical patterns repeated across all command functions:
   - Gemini requirement checking
   - Input/output directory setup
   - File discovery and iteration
   - Result saving with JSON/TXT output
   - Progress reporting
3. **Long Functions**: Many functions exceed 100+ lines
4. **Repeated Path Handling**: Output path logic duplicated in every `*_with_params` function

---

## Refactoring Plan

### Subtask 1: Create Base Command Utilities Module

**Goal**: Extract common patterns into reusable utilities

**File to create**:
- `packages/services/video-tools/video_utils/command_utils.py`

**Functions to extract**:
```python
def check_and_report_gemini_status() -> bool
def setup_directories(input_path=None, output_path=None) -> Tuple[Path, Path, Path|None]
def resolve_output_file(output_dir, output_file, base_name, format_type) -> Tuple[Path, Path]
def save_analysis_with_format(result, json_file, txt_file, format_type, header_fn)
def show_analysis_preview(result, analysis_type, content_keys)
def run_analysis_loop(files, analyzer_fn, save_fn, description) -> Tuple[int, int]
```

**Estimated lines**: ~150 lines

---

### Subtask 2: Create Video Analysis Commands Module

**Goal**: Extract all video-related commands

**File to create**:
- `packages/services/video-tools/video_utils/ai_commands/video_commands.py`

**Functions to move**:
- `cmd_analyze_videos()` - simplified using utilities
- `cmd_transcribe_videos()` - simplified using utilities
- `cmd_describe_videos()` - simplified using utilities
- `cmd_describe_videos_with_params()` - simplified using utilities
- `cmd_transcribe_videos_with_params()` - simplified using utilities

**Estimated lines**: ~200 lines (down from ~600)

---

### Subtask 3: Create Audio Analysis Commands Module

**Goal**: Extract all audio-related commands

**File to create**:
- `packages/services/video-tools/video_utils/ai_commands/audio_commands.py`

**Functions to move**:
- `cmd_analyze_audio()` - simplified using utilities
- `cmd_transcribe_audio()` - simplified using utilities
- `cmd_describe_audio()` - simplified using utilities
- `cmd_analyze_audio_with_params()` - simplified using utilities

**Estimated lines**: ~180 lines (down from ~400)

---

### Subtask 4: Create Image Analysis Commands Module

**Goal**: Extract all image-related commands

**File to create**:
- `packages/services/video-tools/video_utils/ai_commands/image_commands.py`

**Functions to move**:
- `cmd_analyze_images()` - simplified using utilities
- `cmd_describe_images()` - simplified using utilities
- `cmd_extract_text()` - simplified using utilities
- `cmd_analyze_images_with_params()` - simplified using utilities

**Estimated lines**: ~180 lines (down from ~450)

---

### Subtask 5: Create Module Initialization and Backwards Compatibility

**Goal**: Ensure all imports continue to work

**Files to create/modify**:
- `packages/services/video-tools/video_utils/ai_commands/__init__.py` - New package init
- `packages/services/video-tools/video_utils/ai_analysis_commands.py` - Keep as thin re-export layer

**ai_commands/__init__.py**:
```python
from .video_commands import (
    cmd_analyze_videos,
    cmd_transcribe_videos,
    cmd_describe_videos,
    cmd_describe_videos_with_params,
    cmd_transcribe_videos_with_params,
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
```

**ai_analysis_commands.py** (backwards compatibility):
```python
"""
AI analysis command implementations using Google Gemini and OpenRouter.

NOTE: This module re-exports from ai_commands package for backwards compatibility.
For new code, import directly from video_utils.ai_commands.
"""
from .ai_commands import *
```

**Estimated lines**: ~50 lines total

---

### Subtask 6: Add Unit Tests

**Goal**: Ensure refactored code works correctly

**File to create**:
- `tests/unit/test_ai_analysis_commands.py`

**Test coverage**:
1. Test `check_and_report_gemini_status()` returns correct status
2. Test `setup_directories()` handles various input combinations
3. Test `resolve_output_file()` generates correct file paths
4. Test each command function can be imported and called (mock Gemini)
5. Test backwards compatibility of imports from `ai_analysis_commands.py`

**Estimated lines**: ~150 lines

---

## Final File Structure

```
packages/services/video-tools/video_utils/
├── ai_analysis_commands.py     # Thin re-export layer (~20 lines)
├── command_utils.py            # NEW: Shared utilities (~150 lines)
└── ai_commands/                # NEW: Modular command package
    ├── __init__.py             # Package exports (~30 lines)
    ├── video_commands.py       # Video analysis commands (~200 lines)
    ├── audio_commands.py       # Audio analysis commands (~180 lines)
    └── image_commands.py       # Image analysis commands (~180 lines)
```

---

## Line Count Summary

| File | Before | After |
|------|--------|-------|
| ai_analysis_commands.py | 1633 | ~20 |
| command_utils.py | 0 | ~150 |
| ai_commands/__init__.py | 0 | ~30 |
| ai_commands/video_commands.py | 0 | ~200 |
| ai_commands/audio_commands.py | 0 | ~180 |
| ai_commands/image_commands.py | 0 | ~180 |

**Total lines**: ~760 (down from 1633, well-organized with no file exceeding 500 lines)

---

## Implementation Order

1. **Subtask 1**: Create command_utils.py (foundation for all other subtasks)
2. **Subtask 2**: Create video_commands.py (largest portion)
3. **Subtask 3**: Create audio_commands.py
4. **Subtask 4**: Create image_commands.py
5. **Subtask 5**: Create package init and backwards compatibility layer
6. **Subtask 6**: Add unit tests

---

## Detailed Implementation: Subtask 1 - command_utils.py

### Relevant File Paths
- **Create**: `packages/services/video-tools/video_utils/command_utils.py`

### Extracted Utilities

```python
"""Shared utilities for AI analysis commands."""

from pathlib import Path
from typing import Optional, Tuple, List, Callable, Dict, Any

from .gemini_analyzer import check_gemini_requirements
from .ai_utils import save_analysis_result


def check_and_report_gemini_status() -> bool:
    """Check Gemini availability and print status messages."""
    # Extract repeated pattern from lines 27-36, 168-172, 235-238, etc.

def setup_input_directory(input_path: Optional[str] = None,
                          file_finder: Callable = None,
                          media_type: str = "file") -> Tuple[List[Path], bool]:
    """Set up input directory and find files."""
    # Extract pattern from lines 40-56, 174-189, etc.

def setup_output_directory(output_path: Optional[str] = None,
                           num_files: int = 1) -> Tuple[Path, Optional[Path]]:
    """Set up output directory and optional output file."""
    # Extract pattern from lines 345-366, 498-520, etc.

def resolve_output_files(output_dir: Path,
                         output_file: Optional[Path],
                         input_stem: str,
                         suffix: str,
                         format_type: str) -> Tuple[Path, Path]:
    """Resolve JSON and TXT output file paths."""
    # Extract pattern from lines 397-413, 550-567, etc.

def save_with_format(result: Dict[str, Any],
                     json_file: Path,
                     txt_file: Path,
                     format_type: str,
                     content_formatter: Callable[[Dict], str]) -> None:
    """Save analysis result in specified format(s)."""
    # Extract pattern from lines 415-429, 569-602, etc.

def show_preview(content: str, max_length: int = 200) -> None:
    """Show truncated preview of analysis result."""
    # Extract repeated preview pattern

def print_results_summary(successful: int, failed: int, output_dir: Path = None) -> None:
    """Print analysis results summary."""
    # Extract pattern from lines 153-157, 226, etc.
```

---

## Detailed Implementation: Subtask 2 - video_commands.py

### Relevant File Paths
- **Create**: `packages/services/video-tools/video_utils/ai_commands/__init__.py`
- **Create**: `packages/services/video-tools/video_utils/ai_commands/video_commands.py`

### Simplified Structure

```python
"""Video analysis commands using Google Gemini."""

from pathlib import Path
from typing import Optional

from ..command_utils import (
    check_and_report_gemini_status,
    setup_input_directory,
    setup_output_directory,
    resolve_output_files,
    save_with_format,
    show_preview,
    print_results_summary,
)
from ..file_utils import find_video_files
from ..gemini_analyzer import GeminiVideoAnalyzer
from ..ai_utils import analyze_video_file, save_analysis_result


def cmd_analyze_videos():
    """Analyze videos using Google Gemini AI."""
    # Simplified: ~40 lines using utilities

def cmd_transcribe_videos():
    """Quick transcription of video audio using Gemini."""
    # Simplified: ~35 lines using utilities

def cmd_describe_videos():
    """Quick description of videos using Gemini."""
    # Simplified: ~35 lines using utilities

def cmd_describe_videos_with_params(input_path=None, output_path=None, format_type='describe-video'):
    """Enhanced describe-videos command with parameter support."""
    # Simplified: ~50 lines using utilities

def cmd_transcribe_videos_with_params(input_path=None, output_path=None, format_type='describe-video'):
    """Enhanced transcribe-videos command with parameter support."""
    # Simplified: ~50 lines using utilities
```

---

## Detailed Implementation: Subtask 3 - audio_commands.py

### Relevant File Paths
- **Create**: `packages/services/video-tools/video_utils/ai_commands/audio_commands.py`

### Simplified Structure

```python
"""Audio analysis commands using Google Gemini."""

from pathlib import Path
from typing import Optional

from ..command_utils import (
    check_and_report_gemini_status,
    setup_input_directory,
    setup_output_directory,
    resolve_output_files,
    save_with_format,
    show_preview,
    print_results_summary,
)
from ..file_utils import find_audio_files
from ..gemini_analyzer import GeminiVideoAnalyzer
from ..ai_utils import analyze_audio_file, save_analysis_result


def cmd_analyze_audio():
    """Comprehensive audio analysis using Gemini."""
    # Simplified: ~40 lines using utilities

def cmd_transcribe_audio():
    """Quick transcription of audio files using Gemini."""
    # Simplified: ~35 lines using utilities

def cmd_describe_audio():
    """Quick description of audio files using Gemini."""
    # Simplified: ~35 lines using utilities

def cmd_analyze_audio_with_params(input_path=None, output_path=None, format_type='json'):
    """Enhanced analyze-audio command with parameter support."""
    # Simplified: ~60 lines using utilities
```

---

## Detailed Implementation: Subtask 4 - image_commands.py

### Relevant File Paths
- **Create**: `packages/services/video-tools/video_utils/ai_commands/image_commands.py`

### Simplified Structure

```python
"""Image analysis commands using Google Gemini."""

from pathlib import Path
from typing import Optional

from ..command_utils import (
    check_and_report_gemini_status,
    setup_input_directory,
    setup_output_directory,
    resolve_output_files,
    save_with_format,
    show_preview,
    print_results_summary,
)
from ..file_utils import find_image_files
from ..gemini_analyzer import GeminiVideoAnalyzer
from ..ai_utils import analyze_image_file, save_analysis_result


def cmd_analyze_images():
    """Comprehensive image analysis using Gemini."""
    # Simplified: ~45 lines using utilities

def cmd_describe_images():
    """Quick description of images using Gemini."""
    # Simplified: ~35 lines using utilities

def cmd_extract_text():
    """Extract text from images using Gemini OCR."""
    # Simplified: ~35 lines using utilities

def cmd_analyze_images_with_params(input_path=None, output_path=None, format_type='json'):
    """Enhanced analyze-images command with parameter support."""
    # Simplified: ~60 lines using utilities
```

---

## Risk Mitigation

1. **Backwards Compatibility**: Original `ai_analysis_commands.py` becomes a re-export layer
2. **Incremental Approach**: Each subtask can be tested independently
3. **Test First**: Create tests before modifying original code
4. **Git Workflow**: Commit after each successful subtask

---

## Success Criteria

- [ ] All files under 500 lines
- [ ] Existing tests pass (if any)
- [ ] New unit tests for extracted modules
- [ ] All command functions maintain same public API
- [ ] No duplicate code between modules
- [ ] Backwards compatibility imports work

---

## Dependencies

This refactoring depends on:
- `video_utils/gemini_analyzer.py` - GeminiVideoAnalyzer class
- `video_utils/ai_utils.py` - analyze_*_file and save_analysis_result functions
- `video_utils/file_utils.py` - find_*_files functions
- `video_utils/core.py` - get_video_info function
- `video_utils/openrouter_analyzer.py` - OpenRouterAnalyzer (unused in current file)

---

## Notes

- The OpenRouterAnalyzer import on line 18 is unused and can be removed
- Several functions have EOFError/KeyboardInterrupt handling for non-interactive mode
- The `*_with_params` variants add significant complexity for CLI parameter support
- Consider consolidating basic and enhanced versions in future iteration
