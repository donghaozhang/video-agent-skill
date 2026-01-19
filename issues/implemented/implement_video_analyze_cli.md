# Implementation Plan: Video Analyze CLI Command

## Overview

Add a direct CLI command `analyze-video` to the `ai-content-pipeline` (aicp) tool for video understanding and analysis using Gemini models via FAL OpenRouter or direct Gemini API.

**Estimated Total Time**: ~75 minutes

## Target Usage

```bash
# Basic usage (uses defaults: gemini-3-pro, timeline, fal provider)
aicp analyze-video --input video.mp4

# With all options
aicp analyze-video --input video.mp4 --output output/ --model gemini-3-pro --type timeline

# Short form
aicp analyze-video -i video.mp4 -o output/ -m gemini-3-pro -t timeline

# Different analysis types
aicp analyze-video -i video.mp4 -t describe      # Quick description
aicp analyze-video -i video.mp4 -t transcribe    # Audio transcription
aicp analyze-video -i video.mp4 -t timeline      # Detailed timeline (default)
```

---

## Subtasks

### Subtask 1: Create Video Analysis Module (25 min)

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/video_analysis.py`

**Description**: Create a new module that handles the `analyze-video` CLI command logic.

**Implementation**:

```python
"""
Video analysis CLI command implementation.

Provides analyze-video command for AI-powered video understanding
using Gemini models via FAL OpenRouter or direct Gemini API.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Model mapping: CLI key -> (provider, full_model_id)
MODEL_MAP = {
    "gemini-3-pro": ("fal", "google/gemini-3-pro-preview"),
    "gemini-2.5-pro": ("fal", "google/gemini-2.5-pro"),
    "gemini-2.5-flash": ("fal", "google/gemini-2.5-flash"),
    "gemini-direct": ("gemini", "gemini-2.0-flash-exp"),
}

# Analysis type mapping
ANALYSIS_TYPES = {
    "timeline": "Detailed second-by-second timeline",
    "describe": "Video description and summary",
    "transcribe": "Audio transcription with timestamps",
}


def analyze_video_command(args) -> None:
    """Handle analyze-video CLI command.

    Args:
        args: Parsed argparse arguments with:
            - input: Input video file or directory path
            - output: Output directory (default: output/)
            - model: Model key (default: gemini-3-pro)
            - type: Analysis type (default: timeline)
            - format: Output format (md, json, both)
    """
    # Load environment variables
    load_dotenv()

    # Resolve model
    model_key = args.model
    if model_key not in MODEL_MAP:
        print(f"❌ Unknown model: {model_key}")
        print(f"   Available: {', '.join(MODEL_MAP.keys())}")
        sys.exit(1)

    provider, model_id = MODEL_MAP[model_key]

    # Check API keys
    if provider == "fal" and not os.getenv("FAL_KEY"):
        print("❌ FAL_KEY environment variable not set")
        print("   Set it in your .env file or export FAL_KEY=your_key")
        sys.exit(1)
    elif provider == "gemini" and not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Set it in your .env file or export GEMINI_API_KEY=your_key")
        sys.exit(1)

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input not found: {args.input}")
        sys.exit(1)

    # Import and call appropriate analysis function
    analysis_type = args.type
    output_dir = args.output

    print(f"🎬 VIDEO ANALYSIS - {ANALYSIS_TYPES.get(analysis_type, analysis_type)}")
    print("=" * 60)
    print(f"📹 Input: {args.input}")
    print(f"📁 Output: {output_dir}")
    print(f"🤖 Model: {model_key} ({model_id})")
    print(f"📊 Type: {analysis_type}")
    print()

    try:
        # Add video-tools to path
        video_tools_path = Path(__file__).parent.parent.parent.parent / "services" / "video-tools"
        sys.path.insert(0, str(video_tools_path))

        if analysis_type == "timeline":
            from video_utils.ai_commands import cmd_detailed_timeline_with_params
            result = cmd_detailed_timeline_with_params(
                input_path=str(input_path),
                output_path=output_dir,
                provider=provider,
                model=model_id
            )
        elif analysis_type == "describe":
            from video_utils.ai_commands import cmd_describe_videos_with_params
            result = cmd_describe_videos_with_params(
                input_path=str(input_path),
                output_path=output_dir,
                format_type="describe-video"
            )
        elif analysis_type == "transcribe":
            from video_utils.ai_commands import cmd_transcribe_videos_with_params
            result = cmd_transcribe_videos_with_params(
                input_path=str(input_path),
                output_path=output_dir,
                format_type="describe-video"
            )
        else:
            print(f"❌ Unknown analysis type: {analysis_type}")
            sys.exit(1)

        if result:
            print("\n✅ Analysis complete!")
        else:
            print("\n❌ Analysis failed")
            sys.exit(1)

    except ImportError as e:
        print(f"❌ Failed to import video analysis module: {e}")
        print("   Ensure video-tools package is available")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def list_video_models() -> None:
    """Print available video analysis models."""
    print("\n🎬 Video Analysis Models")
    print("=" * 50)

    for key, (provider, model_id) in MODEL_MAP.items():
        print(f"\n  {key}")
        print(f"    Provider: {provider.upper()}")
        print(f"    Model ID: {model_id}")

    print("\n📊 Analysis Types")
    print("=" * 50)
    for key, desc in ANALYSIS_TYPES.items():
        print(f"  {key}: {desc}")
```

**Tests**: `tests/test_video_analysis_cli.py`

---

### Subtask 2: Update Main CLI Entry Point (15 min)

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

**Description**: Add `analyze-video` subparser and handler to the main CLI.

**Changes**:

1. Add import at top:
```python
from .video_analysis import analyze_video_command, list_video_models, MODEL_MAP, ANALYSIS_TYPES
```

2. Add subparser after `list-avatar-models` (around line 575):
```python
# Analyze video command
analyze_video_parser = subparsers.add_parser(
    "analyze-video",
    help="Analyze video content using AI (Gemini via FAL/Direct)"
)
analyze_video_parser.add_argument(
    "-i", "--input",
    required=True,
    help="Input video file or directory"
)
analyze_video_parser.add_argument(
    "-o", "--output",
    default="output",
    help="Output directory (default: output)"
)
analyze_video_parser.add_argument(
    "-m", "--model",
    default="gemini-3-pro",
    choices=list(MODEL_MAP.keys()),
    help="Model to use (default: gemini-3-pro)"
)
analyze_video_parser.add_argument(
    "-t", "--type",
    default="timeline",
    choices=list(ANALYSIS_TYPES.keys()),
    help="Analysis type (default: timeline)"
)
analyze_video_parser.add_argument(
    "-f", "--format",
    default="both",
    choices=["md", "json", "both"],
    help="Output format (default: both)"
)

# List video models command
subparsers.add_parser(
    "list-video-models",
    help="List available video analysis models"
)
```

3. Add handler in main() (around line 596):
```python
elif args.command == "analyze-video":
    analyze_video_command(args)
elif args.command == "list-video-models":
    list_video_models()
```

4. Update epilog examples to include:
```python
  # Analyze video with AI
  python -m ai_content_pipeline analyze-video -i video.mp4

  # Analyze with specific model and type
  python -m ai_content_pipeline analyze-video -i video.mp4 -m gemini-3-pro -t timeline

  # List video analysis models
  python -m ai_content_pipeline list-video-models
```

---

### Subtask 3: Add FAL Provider Support to describe/transcribe (20 min)

**File**: `packages/services/video-tools/video_utils/ai_commands/video_commands.py`

**Description**: Update `cmd_describe_videos_with_params` and `cmd_transcribe_videos_with_params` to support FAL provider option (currently only Gemini direct).

**Changes**:

1. Add provider parameter to `cmd_describe_videos_with_params`:
```python
def cmd_describe_videos_with_params(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    format_type: str = 'describe-video',
    provider: str = 'gemini',
    model: str = None
) -> Optional[dict]:
```

2. Add provider parameter to `cmd_transcribe_videos_with_params`:
```python
def cmd_transcribe_videos_with_params(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    format_type: str = 'describe-video',
    provider: str = 'gemini',
    model: str = None
) -> Optional[dict]:
```

3. Add FAL-based describe/transcribe using `FalVideoAnalyzer`:
```python
if provider == 'fal':
    from ..fal_video_analyzer import FalVideoAnalyzer
    analyzer = FalVideoAnalyzer(model=model or 'google/gemini-2.5-flash')
else:
    from ..gemini_analyzer import GeminiVideoAnalyzer
    analyzer = GeminiVideoAnalyzer()
```

---

### Subtask 4: Create Unit Tests (10 min)

**File**: `tests/test_video_analysis_cli.py`

**Description**: Create unit tests for the new CLI command.

```python
"""Unit tests for video analysis CLI command."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages/core/ai_content_pipeline"))

from ai_content_pipeline.video_analysis import (
    MODEL_MAP,
    ANALYSIS_TYPES,
    analyze_video_command,
    list_video_models,
)


class TestVideoAnalysisModels:
    """Test model configuration."""

    def test_model_map_has_required_models(self):
        """Ensure all expected models are present."""
        assert "gemini-3-pro" in MODEL_MAP
        assert "gemini-2.5-pro" in MODEL_MAP
        assert "gemini-2.5-flash" in MODEL_MAP
        assert "gemini-direct" in MODEL_MAP

    def test_model_map_structure(self):
        """Ensure model map has correct structure."""
        for key, value in MODEL_MAP.items():
            assert isinstance(value, tuple)
            assert len(value) == 2
            provider, model_id = value
            assert provider in ("fal", "gemini")
            assert isinstance(model_id, str)

    def test_analysis_types(self):
        """Ensure analysis types are defined."""
        assert "timeline" in ANALYSIS_TYPES
        assert "describe" in ANALYSIS_TYPES
        assert "transcribe" in ANALYSIS_TYPES


class TestListVideoModels:
    """Test list_video_models function."""

    def test_list_video_models_runs(self, capsys):
        """Ensure list_video_models prints output."""
        list_video_models()
        captured = capsys.readouterr()
        assert "Video Analysis Models" in captured.out
        assert "gemini-3-pro" in captured.out


class TestAnalyzeVideoCommand:
    """Test analyze_video_command function."""

    def test_missing_input_file(self):
        """Test error handling for missing input."""
        args = MagicMock()
        args.input = "/nonexistent/video.mp4"
        args.model = "gemini-3-pro"
        args.type = "timeline"
        args.output = "output"

        with pytest.raises(SystemExit):
            analyze_video_command(args)

    def test_invalid_model(self):
        """Test error handling for invalid model."""
        args = MagicMock()
        args.input = "test.mp4"
        args.model = "invalid-model"
        args.type = "timeline"
        args.output = "output"

        with pytest.raises(SystemExit):
            analyze_video_command(args)
```

---

### Subtask 5: Update Documentation and Skill (5 min)

**Files**:
- `CLAUDE.md` - Add CLI command documentation
- `.claude/skills/ai-content-pipeline/Skill.md` - Update skill with new command

**Changes to CLAUDE.md**:
```markdown
### Video Analysis CLI
```bash
# Analyze video with AI (Gemini 3 Pro via FAL)
ai-content-pipeline analyze-video -i video.mp4

# With options
ai-content-pipeline analyze-video -i video.mp4 -m gemini-3-pro -t timeline -o output/

# List available models
ai-content-pipeline list-video-models
```
```

**Changes to Skill.md**:
```markdown
### Video Analysis CLI
```bash
# Analyze video (default: gemini-3-pro, timeline)
aicp analyze-video -i video.mp4

# Options
aicp analyze-video -i video.mp4 -m gemini-3-pro -t timeline -o output/
aicp analyze-video -i video.mp4 -m gemini-2.5-flash -t describe
aicp analyze-video -i video.mp4 -t transcribe

# List models
aicp list-video-models
```
```

---

## File Summary

| File | Action | Description |
|------|--------|-------------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/video_analysis.py` | CREATE | New module for video analysis CLI |
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | MODIFY | Add analyze-video subparser and handler |
| `packages/services/video-tools/video_utils/ai_commands/video_commands.py` | MODIFY | Add provider support to describe/transcribe |
| `packages/services/video-tools/video_utils/ai_commands/__init__.py` | MODIFY | Export updated functions |
| `tests/test_video_analysis_cli.py` | CREATE | Unit tests for CLI |
| `CLAUDE.md` | MODIFY | Add CLI documentation |
| `.claude/skills/ai-content-pipeline/Skill.md` | MODIFY | Update skill documentation |

---

## Command Options Reference

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--input` | `-i` | Yes | - | Path to video file or directory |
| `--output` | `-o` | No | `output/` | Output directory for results |
| `--model` | `-m` | No | `gemini-3-pro` | Model to use |
| `--type` | `-t` | No | `timeline` | Analysis type |
| `--format` | `-f` | No | `both` | Output format (md, json, both) |

## Available Models

| Model Key | Provider | Full Model ID | Best For |
|-----------|----------|---------------|----------|
| `gemini-3-pro` | FAL | `google/gemini-3-pro-preview` | Highest quality analysis |
| `gemini-2.5-pro` | FAL | `google/gemini-2.5-pro` | Detailed reasoning |
| `gemini-2.5-flash` | FAL | `google/gemini-2.5-flash` | Fast, cost-effective |
| `gemini-direct` | Gemini | `gemini-2.0-flash-exp` | Local files, no upload |

## Analysis Types

| Type | Description | Output |
|------|-------------|--------|
| `timeline` | Second-by-second breakdown | Detailed MD with timestamps, transcript, people |
| `describe` | Video description | Summary MD with key points |
| `transcribe` | Audio transcription | Text with speaker labels and timestamps |

---

## Environment Variables Required

```bash
# For FAL provider (default)
FAL_KEY=your_fal_api_key

# For Gemini direct provider
GEMINI_API_KEY=your_gemini_api_key
```

---

## Success Criteria

1. ✅ `aicp analyze-video --help` shows all options
2. ✅ `aicp analyze-video -i video.mp4` works with defaults
3. ✅ All model options work correctly
4. ✅ All analysis types produce correct output
5. ✅ Both md and json formats are generated
6. ✅ Error handling for missing API keys
7. ✅ Error handling for invalid input files
8. ✅ `aicp list-video-models` shows available models
9. ✅ Unit tests pass
10. ✅ Documentation updated

---

## Long-term Considerations

1. **Extensibility**: The `MODEL_MAP` can easily be extended with new models
2. **Provider abstraction**: Clear separation between FAL and Gemini direct
3. **Analysis types**: New types can be added by extending `ANALYSIS_TYPES`
4. **Output formats**: Support for additional formats (SRT, VTT) can be added
5. **Batch processing**: Directory input already supported for multiple videos
6. **Cost tracking**: Usage stats returned from FAL can be logged/reported
