# Refactoring Plan: video_understanding.py

**File:** `packages/services/video-tools/video_utils/video_understanding.py`
**Current Lines:** 1363
**Threshold:** 500 lines (per CLAUDE.md guidelines)
**Priority:** Medium
**Created:** 2026-01-13

---

## Current Structure Analysis

### Classes and Line Counts

| Component | Lines | Line Range | Description |
|-----------|-------|------------|-------------|
| Imports & Setup | 37 | 1-37 | Module imports and availability checks |
| `GeminiVideoAnalyzer` | 870 | 39-908 | Main analyzer class (TOO LARGE) |
| `WhisperTranscriber` | 224 | 911-1134 | Speech-to-text transcriber |
| Utility Functions | 227 | 1137-1363 | Helper and convenience functions |

### GeminiVideoAnalyzer Method Breakdown

| Category | Methods | Lines | Notes |
|----------|---------|-------|-------|
| **Video** | `upload_video`, `describe_video`, `transcribe_video`, `answer_questions`, `analyze_scenes`, `extract_key_info` | ~270 | Can be extracted |
| **Audio** | `upload_audio`, `describe_audio`, `transcribe_audio`, `analyze_audio_content`, `answer_audio_questions`, `detect_audio_events` | ~240 | Can be extracted |
| **Image** | `upload_image`, `describe_image`, `classify_image`, `detect_objects`, `answer_image_questions`, `extract_text_from_image`, `analyze_image_composition` | ~360 | Can be extracted |

---

## Proposed Refactoring

### New File Structure

```
packages/services/video-tools/video_utils/
├── understanding/
│   ├── __init__.py              # Package exports
│   ├── base.py                  # Base analyzer class (~100 lines)
│   ├── video_analyzer.py        # Video analysis methods (~300 lines)
│   ├── audio_analyzer.py        # Audio analysis methods (~280 lines)
│   ├── image_analyzer.py        # Image analysis methods (~400 lines)
│   ├── whisper_transcriber.py   # Whisper integration (~250 lines)
│   └── utils.py                 # Utility functions (~150 lines)
├── video_understanding.py       # Backwards-compatible facade (~50 lines)
```

### Estimated Line Counts After Refactoring

| File | Lines | Status |
|------|-------|--------|
| `base.py` | ~100 | ✅ Under 500 |
| `video_analyzer.py` | ~300 | ✅ Under 500 |
| `audio_analyzer.py` | ~280 | ✅ Under 500 |
| `image_analyzer.py` | ~400 | ✅ Under 500 |
| `whisper_transcriber.py` | ~250 | ✅ Under 500 |
| `utils.py` | ~150 | ✅ Under 500 |
| `video_understanding.py` (facade) | ~50 | ✅ Under 500 |

---

## Implementation Details

### 1. base.py - Base Analyzer Class

```python
"""Base class for Gemini media analyzers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import os
import time

# Gemini availability check
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class BaseGeminiAnalyzer(ABC):
    """Base class for Gemini-powered media analysis."""

    def __init__(self, api_key: Optional[str] = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed")

        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def _upload_file(self, file_path: Path, file_type: str) -> str:
        """Upload file to Gemini and return file ID."""
        # Common upload logic
        pass

    def _cleanup_file(self, file_id: str) -> None:
        """Delete uploaded file from Gemini."""
        genai.delete_file(file_id)
```

### 2. video_analyzer.py - Video Analysis

```python
"""Video analysis using Google Gemini."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseGeminiAnalyzer


class VideoAnalyzer(BaseGeminiAnalyzer):
    """Gemini-powered video analysis."""

    def upload_video(self, video_path: Path) -> str:
        """Upload video to Gemini."""
        return self._upload_file(video_path, "video")

    def describe(self, video_path: Path, detailed: bool = False) -> Dict[str, Any]:
        """Generate video description."""
        pass

    def transcribe(self, video_path: Path, include_timestamps: bool = True) -> Dict[str, Any]:
        """Transcribe video audio content."""
        pass

    def answer_questions(self, video_path: Path, questions: List[str]) -> Dict[str, Any]:
        """Answer questions about video."""
        pass

    def analyze_scenes(self, video_path: Path) -> Dict[str, Any]:
        """Detect and analyze video scenes."""
        pass

    def extract_key_info(self, video_path: Path) -> Dict[str, Any]:
        """Extract key information from video."""
        pass
```

### 3. audio_analyzer.py - Audio Analysis

```python
"""Audio analysis using Google Gemini."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseGeminiAnalyzer


class AudioAnalyzer(BaseGeminiAnalyzer):
    """Gemini-powered audio analysis."""

    def upload_audio(self, audio_path: Path) -> str:
        """Upload audio to Gemini."""
        return self._upload_file(audio_path, "audio")

    def describe(self, audio_path: Path, detailed: bool = False) -> Dict[str, Any]:
        """Generate audio description."""
        pass

    def transcribe(self, audio_path: Path,
                   include_timestamps: bool = True,
                   speaker_identification: bool = True) -> Dict[str, Any]:
        """Transcribe audio content."""
        pass

    def analyze_content(self, audio_path: Path) -> Dict[str, Any]:
        """Analyze audio content and features."""
        pass

    def answer_questions(self, audio_path: Path, questions: List[str]) -> Dict[str, Any]:
        """Answer questions about audio."""
        pass

    def detect_events(self, audio_path: Path) -> Dict[str, Any]:
        """Detect audio events and segments."""
        pass
```

### 4. image_analyzer.py - Image Analysis

```python
"""Image analysis using Google Gemini."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseGeminiAnalyzer


class ImageAnalyzer(BaseGeminiAnalyzer):
    """Gemini-powered image analysis."""

    def upload_image(self, image_path: Path) -> str:
        """Upload image to Gemini."""
        return self._upload_file(image_path, "image")

    def describe(self, image_path: Path, detailed: bool = False) -> Dict[str, Any]:
        """Generate image description."""
        pass

    def classify(self, image_path: Path) -> Dict[str, Any]:
        """Classify and categorize image."""
        pass

    def detect_objects(self, image_path: Path, detailed: bool = False) -> Dict[str, Any]:
        """Detect objects in image."""
        pass

    def answer_questions(self, image_path: Path, questions: List[str]) -> Dict[str, Any]:
        """Answer questions about image."""
        pass

    def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """Extract text from image (OCR)."""
        pass

    def analyze_composition(self, image_path: Path) -> Dict[str, Any]:
        """Analyze artistic composition."""
        pass
```

### 5. whisper_transcriber.py - Whisper Integration

```python
"""OpenAI Whisper speech-to-text transcription."""

from pathlib import Path
from typing import Dict, Any, Optional, List
import os

# Import checks
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import whisper
    WHISPER_LOCAL_AVAILABLE = True
except ImportError:
    WHISPER_LOCAL_AVAILABLE = False


class WhisperTranscriber:
    """Whisper-powered speech-to-text transcription."""

    def __init__(self, api_key: Optional[str] = None, use_local: bool = False):
        pass

    def transcribe_audio(self, audio_path: Path, **kwargs) -> Dict[str, Any]:
        pass

    def transcribe_video(self, video_path: Path, **kwargs) -> Dict[str, Any]:
        pass

    def _transcribe_api(self, audio_path: Path, **kwargs) -> Dict[str, Any]:
        pass

    def _transcribe_local(self, audio_path: Path, **kwargs) -> Dict[str, Any]:
        pass

    def _extract_audio_from_video(self, video_path: Path) -> Path:
        pass
```

### 6. utils.py - Utility Functions

```python
"""Utility functions for media understanding."""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json


def check_gemini_requirements() -> tuple[bool, str]:
    """Check Gemini API availability."""
    pass


def check_whisper_requirements(check_api: bool = True,
                               check_local: bool = True) -> Dict[str, tuple[bool, str]]:
    """Check Whisper availability."""
    pass


def save_analysis_result(result: Dict[str, Any], output_path: Path) -> bool:
    """Save analysis result to JSON."""
    pass


def analyze_video_file(video_path: Path, analysis_type: str = "description",
                       **kwargs) -> Optional[Dict[str, Any]]:
    """Convenience function for video analysis."""
    pass


def analyze_audio_file(audio_path: Path, analysis_type: str = "description",
                       **kwargs) -> Optional[Dict[str, Any]]:
    """Convenience function for audio analysis."""
    pass


def analyze_image_file(image_path: Path, analysis_type: str = "description",
                       **kwargs) -> Optional[Dict[str, Any]]:
    """Convenience function for image analysis."""
    pass


def transcribe_with_whisper(file_path: Path, **kwargs) -> Optional[Dict[str, Any]]:
    """Convenience function for Whisper transcription."""
    pass


def batch_transcribe_whisper(file_paths: List[Path], **kwargs) -> List[Dict[str, Any]]:
    """Batch transcribe multiple files."""
    pass
```

### 7. video_understanding.py - Backwards-Compatible Facade

```python
"""
Backwards-compatible facade for video understanding.

This module re-exports all components from the understanding package
to maintain backwards compatibility with existing code.
"""

# Re-export all classes and functions
from .understanding import (
    # Main analyzer (combines all for backwards compatibility)
    GeminiVideoAnalyzer,

    # Individual analyzers
    VideoAnalyzer,
    AudioAnalyzer,
    ImageAnalyzer,

    # Whisper
    WhisperTranscriber,

    # Utility functions
    check_gemini_requirements,
    check_whisper_requirements,
    save_analysis_result,
    analyze_video_file,
    analyze_audio_file,
    analyze_image_file,
    transcribe_with_whisper,
    batch_transcribe_whisper,
)

__all__ = [
    'GeminiVideoAnalyzer',
    'VideoAnalyzer',
    'AudioAnalyzer',
    'ImageAnalyzer',
    'WhisperTranscriber',
    'check_gemini_requirements',
    'check_whisper_requirements',
    'save_analysis_result',
    'analyze_video_file',
    'analyze_audio_file',
    'analyze_image_file',
    'transcribe_with_whisper',
    'batch_transcribe_whisper',
]
```

---

## Migration Steps

### Phase 1: Create New Structure (Non-Breaking)
1. [ ] Create `understanding/` subdirectory
2. [ ] Create `understanding/__init__.py`
3. [ ] Create `understanding/base.py` with base class
4. [ ] Create `understanding/video_analyzer.py`
5. [ ] Create `understanding/audio_analyzer.py`
6. [ ] Create `understanding/image_analyzer.py`
7. [ ] Create `understanding/whisper_transcriber.py`
8. [ ] Create `understanding/utils.py`

### Phase 2: Add Backwards Compatibility
9. [ ] Create combined `GeminiVideoAnalyzer` class that delegates to individual analyzers
10. [ ] Update `video_understanding.py` to be a facade
11. [ ] Ensure all existing imports still work

### Phase 3: Testing
12. [ ] Write unit tests for each new module
13. [ ] Test existing code paths still work
14. [ ] Run integration tests

### Phase 4: Cleanup
15. [ ] Update documentation
16. [ ] Remove deprecated code comments
17. [ ] Update any internal imports to use new structure

---

## Benefits of Refactoring

1. **Maintainability**: Each file focuses on one type of media analysis
2. **Testability**: Smaller, focused modules are easier to test
3. **Extensibility**: Easy to add new analysis types or providers
4. **Readability**: Clear separation of concerns
5. **Compliance**: All files under 500-line limit

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing imports | Facade pattern maintains backwards compatibility |
| Increased complexity | Clear module boundaries and documentation |
| Testing overhead | Focus on critical paths first |

---

## Dependencies

No new dependencies required. Uses existing:
- `google-generativeai`
- `openai`
- `whisper` (optional, for local transcription)

---

## References

- [CLAUDE.md Guidelines](../CLAUDE.md) - 500-line file limit
- [GeminiVideoAnalyzer Current Implementation](../packages/services/video-tools/video_utils/video_understanding.py)
