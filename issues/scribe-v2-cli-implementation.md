# Scribe v2 CLI Implementation Plan

**Feature:** Add CLI command for ElevenLabs Scribe v2 speech-to-text transcription
**Created:** 2026-01-22
**Estimated Time:** 25-30 minutes
**Priority:** Medium

## Overview

Implement a CLI command `transcribe` for the AI Content Pipeline that allows users to transcribe audio files using the ElevenLabs Scribe v2 model via FAL AI.

## Current State

- **API Ready:** `packages/providers/fal/speech-to-text/fal_speech_to_text/generator.py` provides full Python API
- **Missing:** CLI wrapper in `packages/core/ai_content_pipeline/`
- **Pattern Reference:** `motion_transfer.py` and `video_analysis.py` provide CLI implementation patterns

## Target CLI Usage

```bash
# Basic transcription (auto-saves to output/)
aicp transcribe -i audio.mp3

# With all options
aicp transcribe -i audio.mp3 -o output/ --language eng --diarize --tag-events

# Disable diarization for faster processing
aicp transcribe -i audio.mp3 --no-diarize

# With keyterms for better accuracy (increases cost by 30%)
aicp transcribe -i audio.mp3 --keyterms "Claude" "Anthropic" "AI"

# Save detailed JSON metadata
aicp transcribe -i audio.mp3 --save-json metadata.json

# List available models
aicp list-speech-models
```

## Implementation Subtasks

### Subtask 1: Create Speech-to-Text CLI Module (10 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/speech_to_text.py`

**Description:** Create the main CLI module following the `motion_transfer.py` pattern.

**Implementation:**

```python
"""
Speech-to-text CLI command implementation.

Provides transcribe command for ElevenLabs Scribe v2 model
to transcribe audio files with speaker diarization.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Try to import FAL client for file uploads
try:
    import fal_client
    FAL_CLIENT_AVAILABLE = True
except ImportError:
    FAL_CLIENT_AVAILABLE = False

# Try to import speech-to-text generator
try:
    # Add package path for direct import
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent /
                           "providers/fal/speech-to-text"))
    from fal_speech_to_text import FALSpeechToTextGenerator
    from fal_speech_to_text.models.base import TranscriptionResult
    FAL_SPEECH_AVAILABLE = True
except ImportError:
    FAL_SPEECH_AVAILABLE = False
    TranscriptionResult = None


# Model information
MODEL_INFO = {
    "scribe_v2": {
        "name": "ElevenLabs Scribe v2",
        "provider": "FAL AI",
        "cost_per_minute": 0.008,
        "keyterm_cost_increase": 0.30,  # +30%
        "features": [
            "99 language support",
            "Word-level timestamps",
            "Speaker diarization",
            "Audio event tagging",
            "Fast inference",
        ],
    }
}

# Default values
DEFAULTS = {
    "model": "scribe_v2",
    "output_dir": "output",
    "diarize": True,
    "tag_events": True,
}


@dataclass
class TranscriptionCLIResult:
    """Result from transcription CLI operation."""
    success: bool
    text: str = ""
    txt_path: Optional[str] = None
    json_path: Optional[str] = None
    speakers: Optional[List[str]] = None
    duration: Optional[float] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    language_detected: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def check_dependencies() -> Tuple[bool, str]:
    """Check if required dependencies are available."""
    if not FAL_CLIENT_AVAILABLE:
        return False, "fal-client not installed. Run: pip install fal-client"
    if not FAL_SPEECH_AVAILABLE:
        return False, "fal_speech_to_text module not available. Check package installation."
    if not os.getenv("FAL_KEY"):
        return False, "FAL_KEY environment variable not set"
    return True, ""


def upload_if_local(file_path: str, file_type: str = "audio") -> str:
    """Upload local file to FAL if it's a local path, otherwise return as-is."""
    if file_path.startswith(("http://", "https://")):
        return file_path

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"{file_type.title()} not found: {file_path}")

    print(f"📤 Uploading {file_type}: {path.name}")
    try:
        url = fal_client.upload_file(str(path))
        print(f"✅ {file_type.title()} uploaded: {url[:60]}...")
        return url
    except Exception as e:
        raise ValueError(f"Failed to upload {file_type}: {e}")


def transcribe(
    audio_path: str,
    output_dir: str = "output",
    model: str = "scribe_v2",
    language_code: Optional[str] = None,
    diarize: bool = True,
    tag_audio_events: bool = True,
    keyterms: Optional[List[str]] = None,
) -> TranscriptionCLIResult:
    """
    Transcribe audio file with full workflow.

    Handles file upload, API call, and output file saving.

    Args:
        audio_path: Audio file path or URL
        output_dir: Output directory for transcription files
        model: Model to use (default: scribe_v2)
        language_code: Language code (e.g., "eng"). None for auto-detect.
        diarize: Enable speaker diarization
        tag_audio_events: Tag audio events (laughter, music, etc.)
        keyterms: List of terms to bias transcription toward

    Returns:
        TranscriptionCLIResult with all operation details
    """
    # Check dependencies
    ok, error = check_dependencies()
    if not ok:
        return TranscriptionCLIResult(success=False, error=error)

    try:
        # Upload file if local
        audio_url = upload_if_local(audio_path, "audio")

        # Call API
        print(f"\n🎤 Starting transcription...")
        print(f"   Model: {model}")
        print(f"   Diarize: {diarize}")
        print(f"   Tag events: {tag_audio_events}")
        if language_code:
            print(f"   Language: {language_code}")
        if keyterms:
            print(f"   Keyterms: {', '.join(keyterms)}")

        generator = FALSpeechToTextGenerator()
        result = generator.transcribe(
            audio_url=audio_url,
            model=model,
            language_code=language_code,
            diarize=diarize,
            tag_audio_events=tag_audio_events,
            keyterms=keyterms,
        )

        if not result.success:
            return TranscriptionCLIResult(
                success=False,
                error=result.error,
                processing_time=result.processing_time,
            )

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        input_name = Path(audio_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{input_name}_transcript_{timestamp}"

        # Save text file
        txt_path = output_path / f"{base_filename}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(result.text)

        return TranscriptionCLIResult(
            success=True,
            text=result.text,
            txt_path=str(txt_path),
            speakers=result.speakers,
            duration=result.duration,
            cost=result.cost,
            processing_time=result.processing_time,
            language_detected=result.language_detected,
            metadata={
                "model": model,
                "diarize": diarize,
                "tag_audio_events": tag_audio_events,
                "keyterms": keyterms,
                "words_count": len(result.words) if result.words else 0,
                "audio_events_count": len(result.audio_events) if result.audio_events else 0,
            },
        )

    except FileNotFoundError as e:
        return TranscriptionCLIResult(success=False, error=str(e))
    except ValueError as e:
        return TranscriptionCLIResult(success=False, error=str(e))
    except Exception as e:
        return TranscriptionCLIResult(success=False, error=f"Unexpected error: {e}")


def transcribe_command(args) -> None:
    """Handle transcribe CLI command."""
    load_dotenv()

    # Print header
    print(f"\n🎤 SPEECH-TO-TEXT TRANSCRIPTION")
    print("=" * 50)
    print(f"📁 Input: {args.input}")
    print(f"📁 Output: {args.output}")
    print(f"🤖 Model: scribe_v2 (ElevenLabs Scribe v2)")
    if args.language:
        print(f"🌐 Language: {args.language}")
    else:
        print(f"🌐 Language: auto-detect")
    print(f"🔊 Diarize: {args.diarize}")
    print(f"🎵 Tag events: {args.tag_events}")
    if args.keyterms:
        print(f"📌 Keyterms: {', '.join(args.keyterms)} (+30% cost)")
    print()

    # Execute transcription
    result = transcribe(
        audio_path=args.input,
        output_dir=args.output,
        language_code=args.language,
        diarize=args.diarize,
        tag_audio_events=args.tag_events,
        keyterms=args.keyterms,
    )

    # Display results
    if result.success:
        print(f"\n✅ Transcription complete!")
        print(f"📝 Text preview: {result.text[:100]}..." if len(result.text) > 100 else f"📝 Text: {result.text}")
        if result.speakers:
            print(f"🎤 Speakers detected: {len(result.speakers)}")
        if result.language_detected:
            print(f"🌐 Language detected: {result.language_detected}")
        if result.duration:
            print(f"⏱️  Duration: {result.duration:.1f}s")
        if result.cost:
            print(f"💰 Cost: ${result.cost:.4f}")
        if result.processing_time:
            print(f"⏱️  Processing: {result.processing_time:.1f}s")
        if result.txt_path:
            print(f"📄 Text file: {result.txt_path}")

        # Save JSON if requested
        if args.save_json:
            json_path = Path(args.output) / args.save_json
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "success": True,
                    "text": result.text,
                    "txt_path": result.txt_path,
                    "speakers": result.speakers,
                    "duration": result.duration,
                    "cost": result.cost,
                    "processing_time": result.processing_time,
                    "language_detected": result.language_detected,
                    "metadata": result.metadata,
                }, f, indent=2)
            print(f"📄 Metadata: {json_path}")
    else:
        print(f"\n❌ Transcription failed!")
        print(f"   Error: {result.error}")
        sys.exit(1)


def list_speech_models() -> None:
    """Print available speech-to-text models."""
    print("\n🎤 Speech-to-Text Models")
    print("=" * 50)

    for model_key, info in MODEL_INFO.items():
        print(f"\n  {model_key}")
        print(f"    Name: {info['name']}")
        print(f"    Provider: {info['provider']}")
        print(f"    Cost: ${info['cost_per_minute']:.3f}/minute")
        print(f"    Keyterms: +{int(info['keyterm_cost_increase'] * 100)}% cost increase")
        print(f"    Features:")
        for feature in info['features']:
            print(f"      • {feature}")

    print("\n  Common Language Codes:")
    print("    eng (English), spa (Spanish), fra (French), deu (German)")
    print("    zho (Chinese), jpn (Japanese), kor (Korean), ara (Arabic)")
    print("    por (Portuguese), rus (Russian), ita (Italian), nld (Dutch)")
    print("\n  Audio Event Types:")
    print("    laughter, applause, music, silence, speech, noise")
```

**Dependencies:**
- `fal_speech_to_text` package (already exists)
- `fal_client` for file uploads
- `dotenv` for environment variables

---

### Subtask 2: Integrate CLI into Main Entry Point (5 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

**Changes Required:**

1. **Add import** (around line 40):
```python
from .speech_to_text import (
    transcribe_command,
    list_speech_models,
)
```

2. **Add subparser** (around line 690, after transfer-motion parser):
```python
# Transcribe command
transcribe_parser = subparsers.add_parser(
    "transcribe",
    help="Transcribe audio using ElevenLabs Scribe v2"
)
transcribe_parser.add_argument(
    "-i", "--input",
    required=True,
    help="Input audio file path or URL"
)
transcribe_parser.add_argument(
    "-o", "--output",
    default="output",
    help="Output directory (default: output)"
)
transcribe_parser.add_argument(
    "--language",
    help="Language code (e.g., eng, spa, fra). Default: auto-detect"
)
transcribe_parser.add_argument(
    "--diarize",
    action="store_true",
    default=True,
    help="Enable speaker diarization (default: enabled)"
)
transcribe_parser.add_argument(
    "--no-diarize",
    action="store_false",
    dest="diarize",
    help="Disable speaker diarization"
)
transcribe_parser.add_argument(
    "--tag-events",
    action="store_true",
    default=True,
    help="Tag audio events (default: enabled)"
)
transcribe_parser.add_argument(
    "--no-tag-events",
    action="store_false",
    dest="tag_events",
    help="Disable audio event tagging"
)
transcribe_parser.add_argument(
    "--keyterms",
    nargs="+",
    help="Terms to bias transcription toward (increases cost by 30%%)"
)
transcribe_parser.add_argument(
    "--save-json",
    metavar="FILENAME",
    help="Save detailed metadata as JSON file"
)

# List speech models command
list_speech_parser = subparsers.add_parser(
    "list-speech-models",
    help="List available speech-to-text models"
)
```

3. **Add command dispatch** (around line 730, in main() function):
```python
elif args.command == "transcribe":
    transcribe_command(args)
elif args.command == "list-speech-models":
    list_speech_models()
```

4. **Update help examples** (in epilog around line 540):
```python
  # Transcribe audio
  python -m ai_content_pipeline transcribe -i audio.mp3
  # With diarization disabled
  python -m ai_content_pipeline transcribe -i audio.mp3 --no-diarize
```

---

### Subtask 3: Update Skill Documentation (3 min)

**File:** `.claude/skills/ai-content-pipeline/Skill.md`

**Add new section** (after Transfer Motion section, around line 115):

```markdown
### Transcribe Audio
```bash
# Basic transcription (auto-detect language)
./venv/Scripts/aicp.exe transcribe -i audio.mp3

# With language specified
./venv/Scripts/aicp.exe transcribe -i audio.mp3 --language eng

# Disable diarization for faster processing
./venv/Scripts/aicp.exe transcribe -i audio.mp3 --no-diarize

# With keyterms for better accuracy
./venv/Scripts/aicp.exe transcribe -i audio.mp3 --keyterms "Claude" "Anthropic"

# Save detailed JSON metadata
./venv/Scripts/aicp.exe transcribe -i audio.mp3 --save-json metadata.json

# List speech models
./venv/Scripts/aicp.exe list-speech-models
```

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input` | `-i` | required | Audio file path or URL |
| `--output` | `-o` | `output/` | Output directory |
| `--language` | | auto-detect | Language code (eng, spa, fra, etc.) |
| `--diarize` | | true | Enable speaker diarization |
| `--no-diarize` | | | Disable diarization |
| `--tag-events` | | true | Tag audio events |
| `--keyterms` | | | Terms to bias toward (+30% cost) |
| `--save-json` | | | Save metadata as JSON |

**Pricing:** $0.008/minute (+30% with keyterms)
```

---

### Subtask 4: Write Unit Tests (7 min)

**File:** `tests/test_speech_to_text_cli.py`

```python
"""
Unit tests for Speech-to-Text CLI command.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "packages/core/ai_content_pipeline"))

from ai_content_pipeline.speech_to_text import (
    check_dependencies,
    upload_if_local,
    transcribe,
    TranscriptionCLIResult,
    MODEL_INFO,
    DEFAULTS,
)


class TestCheckDependencies:
    """Tests for dependency checking."""

    @patch.dict('os.environ', {'FAL_KEY': 'test-key'})
    @patch('ai_content_pipeline.speech_to_text.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.speech_to_text.FAL_SPEECH_AVAILABLE', True)
    def test_all_dependencies_available(self):
        """Test returns success when all dependencies available."""
        ok, error = check_dependencies()
        assert ok is True
        assert error == ""

    @patch('ai_content_pipeline.speech_to_text.FAL_CLIENT_AVAILABLE', False)
    def test_missing_fal_client(self):
        """Test returns error when fal-client missing."""
        ok, error = check_dependencies()
        assert ok is False
        assert "fal-client" in error

    @patch('ai_content_pipeline.speech_to_text.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.speech_to_text.FAL_SPEECH_AVAILABLE', False)
    def test_missing_speech_module(self):
        """Test returns error when speech module missing."""
        ok, error = check_dependencies()
        assert ok is False
        assert "fal_speech_to_text" in error

    @patch.dict('os.environ', {}, clear=True)
    @patch('ai_content_pipeline.speech_to_text.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.speech_to_text.FAL_SPEECH_AVAILABLE', True)
    def test_missing_api_key(self):
        """Test returns error when FAL_KEY missing."""
        ok, error = check_dependencies()
        assert ok is False
        assert "FAL_KEY" in error


class TestUploadIfLocal:
    """Tests for file upload handling."""

    def test_url_passthrough(self):
        """Test URLs are returned as-is."""
        url = "https://example.com/audio.mp3"
        result = upload_if_local(url)
        assert result == url

    def test_http_url_passthrough(self):
        """Test HTTP URLs are returned as-is."""
        url = "http://example.com/audio.mp3"
        result = upload_if_local(url)
        assert result == url

    def test_missing_local_file(self):
        """Test FileNotFoundError for missing local file."""
        with pytest.raises(FileNotFoundError, match="Audio not found"):
            upload_if_local("/nonexistent/audio.mp3")

    @patch('ai_content_pipeline.speech_to_text.fal_client')
    def test_local_file_upload(self, mock_fal_client, tmp_path):
        """Test local file is uploaded."""
        # Create temp file
        audio_file = tmp_path / "test.mp3"
        audio_file.write_text("fake audio")

        mock_fal_client.upload_file.return_value = "https://fal.media/uploaded.mp3"

        result = upload_if_local(str(audio_file))

        assert result == "https://fal.media/uploaded.mp3"
        mock_fal_client.upload_file.assert_called_once()


class TestTranscribe:
    """Tests for transcribe function."""

    @patch('ai_content_pipeline.speech_to_text.check_dependencies')
    def test_dependency_failure(self, mock_check):
        """Test returns error when dependencies unavailable."""
        mock_check.return_value = (False, "Missing dependency")

        result = transcribe("audio.mp3")

        assert result.success is False
        assert "Missing dependency" in result.error

    @patch('ai_content_pipeline.speech_to_text.check_dependencies')
    @patch('ai_content_pipeline.speech_to_text.upload_if_local')
    @patch('ai_content_pipeline.speech_to_text.FALSpeechToTextGenerator')
    def test_successful_transcription(self, mock_generator_class, mock_upload, mock_check, tmp_path):
        """Test successful transcription workflow."""
        mock_check.return_value = (True, "")
        mock_upload.return_value = "https://fal.media/audio.mp3"

        # Mock generator and result
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.text = "Hello world"
        mock_result.speakers = ["speaker_1"]
        mock_result.duration = 5.0
        mock_result.cost = 0.001
        mock_result.processing_time = 2.5
        mock_result.language_detected = "eng"
        mock_result.words = []
        mock_result.audio_events = []
        mock_generator.transcribe.return_value = mock_result

        result = transcribe("audio.mp3", output_dir=str(tmp_path))

        assert result.success is True
        assert result.text == "Hello world"
        assert result.speakers == ["speaker_1"]
        assert result.duration == 5.0
        assert result.txt_path is not None


class TestModelInfo:
    """Tests for model constants."""

    def test_scribe_v2_exists(self):
        """Test scribe_v2 model is configured."""
        assert "scribe_v2" in MODEL_INFO

    def test_scribe_v2_pricing(self):
        """Test scribe_v2 has correct pricing."""
        assert MODEL_INFO["scribe_v2"]["cost_per_minute"] == 0.008

    def test_defaults_configured(self):
        """Test default values are set."""
        assert DEFAULTS["model"] == "scribe_v2"
        assert DEFAULTS["diarize"] is True
        assert DEFAULTS["output_dir"] == "output"


class TestTranscriptionCLIResult:
    """Tests for result dataclass."""

    def test_success_result(self):
        """Test successful result creation."""
        result = TranscriptionCLIResult(
            success=True,
            text="Hello world",
            txt_path="/output/transcript.txt",
            duration=5.0,
            cost=0.001,
        )
        assert result.success is True
        assert result.text == "Hello world"

    def test_error_result(self):
        """Test error result creation."""
        result = TranscriptionCLIResult(
            success=False,
            error="API error"
        )
        assert result.success is False
        assert result.error == "API error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## File Summary

| File | Action | Description |
|------|--------|-------------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/speech_to_text.py` | **Create** | Main CLI module with transcribe command |
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | **Modify** | Add import, subparser, and dispatch |
| `.claude/skills/ai-content-pipeline/Skill.md` | **Modify** | Add transcribe command documentation |
| `tests/test_speech_to_text_cli.py` | **Create** | Unit tests for CLI functionality |

## Testing Plan

1. **Unit Tests:** Run `pytest tests/test_speech_to_text_cli.py -v`
2. **Integration Test:**
   ```bash
   ./venv/Scripts/aicp.exe transcribe -i test_audio.mp3 -o output/
   ```
3. **Edge Cases:**
   - Missing FAL_KEY
   - Invalid audio file
   - URL input vs local file
   - Keyterms with special characters

## Rollback Plan

If issues arise:
1. Remove import from `__main__.py`
2. Remove subparser and dispatch code
3. Delete `speech_to_text.py`
4. Revert skill documentation changes

## Long-term Considerations

1. **Package Installation:** Consider adding `setup.py` to `fal_speech_to_text` package for proper pip installation
2. **Batch Processing:** Future enhancement to transcribe multiple files
3. **Output Formats:** Support SRT/VTT subtitle output formats
4. **Streaming:** Support for real-time transcription of audio streams
