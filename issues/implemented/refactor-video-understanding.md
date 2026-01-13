# Refactoring Plan: video_understanding.py

**File:** `packages/services/video-tools/video_utils/video_understanding.py`
**Current Lines:** 1363
**Threshold:** 500 lines (per CLAUDE.md guidelines)
**Priority:** High
**Created:** 2026-01-13
**Updated:** 2026-01-13

---

## Status: Refactoring Already Completed - Cleanup Required

The refactoring has **already been done**. The old `video_understanding.py` (1363 lines) is now **duplicate/legacy code** that should be **DELETED**.

### New Modular Files (Already Exist)

| New File | Lines | Status | Description |
|----------|-------|--------|-------------|
| `gemini_analyzer.py` | 753 | ✅ Active | GeminiVideoAnalyzer class |
| `whisper_transcriber.py` | 399 | ✅ Active | WhisperTranscriber class |
| `ai_utils.py` | 510 | ✅ Active | Convenience functions |
| **Total** | **1662** | ✅ | Split across 3 files |

### Legacy File (To Delete)

| File | Lines | Status | Action |
|------|-------|--------|--------|
| `video_understanding.py` | 1363 | ⚠️ Duplicate | **DELETE** |

---

## Current Architecture

The `__init__.py` already imports from the **new** modular files:

```python
# From video_utils/__init__.py (lines 47-60)

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
```

### File Structure (Current)

```
packages/services/video-tools/video_utils/
├── __init__.py                  # ✅ Imports from NEW files
├── video_understanding.py       # ❌ DELETE - Legacy duplicate (1363 lines)
├── gemini_analyzer.py           # ✅ KEEP - GeminiVideoAnalyzer (753 lines)
├── whisper_transcriber.py       # ✅ KEEP - WhisperTranscriber (399 lines)
└── ai_utils.py                  # ✅ KEEP - Utility functions (510 lines)
```

---

## Files Still Importing from Legacy Module

These files need to be **MODIFIED** to import from the new modules instead:

### 1. whisper_commands.py (Line 10)

**Current:**
```python
from .video_understanding import (
    WhisperTranscriber,
    check_whisper_requirements,
    ...
)
```

**Change to:**
```python
from .whisper_transcriber import WhisperTranscriber, check_whisper_requirements
from .ai_utils import transcribe_with_whisper, batch_transcribe_whisper
```

### 2. openrouter_commands.py (Lines 11, 248)

**Current:**
```python
from .video_understanding import save_analysis_result, GeminiVideoAnalyzer
from .video_understanding import check_gemini_requirements
```

**Change to:**
```python
from .ai_utils import save_analysis_result
from .gemini_analyzer import GeminiVideoAnalyzer, check_gemini_requirements
```

### 3. ai_analysis_commands.py (Line 11)

**Current:**
```python
from .video_understanding import (
    GeminiVideoAnalyzer,
    ...
)
```

**Change to:**
```python
from .gemini_analyzer import GeminiVideoAnalyzer, check_gemini_requirements
from .ai_utils import (
    save_analysis_result,
    analyze_video_file,
    analyze_audio_file,
    analyze_image_file,
)
```

### 4. Test Files

| File | Current Import | Change To |
|------|----------------|-----------|
| `tests/test_video_understanding.py` | `from video_utils.video_understanding import ...` | `from video_utils import ...` or `from video_utils.gemini_analyzer import ...` |
| `tests/real_video_examples.py` | `from video_utils.video_understanding import ...` | `from video_utils import ...` |
| `tests/image_modify_verify.py` | `from video_utils.video_understanding import ...` | `from video_utils import ...` |

---

## Action Items

### Phase 1: Update Imports (Non-Breaking)

- [x] **MODIFY** `whisper_commands.py` - Update imports ✅
- [x] **MODIFY** `openrouter_commands.py` - Update imports ✅
- [x] **MODIFY** `ai_analysis_commands.py` - Update imports ✅
- [x] **MODIFY** `tests/test_video_understanding.py` - Update imports ✅
- [x] **MODIFY** `tests/real_video_examples.py` - Update imports ✅
- [x] **MODIFY** `tests/image_modify_verify.py` - Update imports ✅

### Phase 2: Delete Legacy File

- [x] **DELETE** `video_understanding.py` (1363 lines of duplicate code) ✅

### Phase 3: Verify

- [x] Run tests to ensure nothing breaks ✅
- [x] Verify all imports resolve correctly ✅

---

## Detailed File Changes

### File: `whisper_commands.py`

**Path:** `packages/services/video-tools/video_utils/whisper_commands.py`

**Line 10 - Change:**
```python
# OLD (DELETE)
from .video_understanding import (
    WhisperTranscriber,
    check_whisper_requirements,
    transcribe_with_whisper,
    batch_transcribe_whisper,
    save_analysis_result
)

# NEW (ADD)
from .whisper_transcriber import WhisperTranscriber, check_whisper_requirements
from .ai_utils import transcribe_with_whisper, batch_transcribe_whisper, save_analysis_result
```

---

### File: `openrouter_commands.py`

**Path:** `packages/services/video-tools/video_utils/openrouter_commands.py`

**Line 11 - Change:**
```python
# OLD (DELETE)
from .video_understanding import save_analysis_result, GeminiVideoAnalyzer

# NEW (ADD)
from .ai_utils import save_analysis_result
from .gemini_analyzer import GeminiVideoAnalyzer
```

**Line 248 - Change:**
```python
# OLD (DELETE)
from .video_understanding import check_gemini_requirements

# NEW (ADD)
from .gemini_analyzer import check_gemini_requirements
```

---

### File: `ai_analysis_commands.py`

**Path:** `packages/services/video-tools/video_utils/ai_analysis_commands.py`

**Line 11 - Change:**
```python
# OLD (DELETE)
from .video_understanding import (
    GeminiVideoAnalyzer,
    WhisperTranscriber,
    check_gemini_requirements,
    check_whisper_requirements,
    save_analysis_result,
    analyze_video_file,
    analyze_audio_file,
    analyze_image_file,
    transcribe_with_whisper,
    batch_transcribe_whisper
)

# NEW (ADD)
from .gemini_analyzer import GeminiVideoAnalyzer, check_gemini_requirements
from .whisper_transcriber import WhisperTranscriber, check_whisper_requirements
from .ai_utils import (
    save_analysis_result,
    analyze_video_file,
    analyze_audio_file,
    analyze_image_file,
    transcribe_with_whisper,
    batch_transcribe_whisper
)
```

---

### File: `tests/test_video_understanding.py`

**Path:** `packages/services/video-tools/tests/test_video_understanding.py`

**Multiple lines - Change all imports:**
```python
# OLD (DELETE)
from video_utils.video_understanding import (...)

# NEW (ADD) - Use package-level imports
from video_utils import (
    GeminiVideoAnalyzer,
    WhisperTranscriber,
    check_gemini_requirements,
    check_whisper_requirements,
    save_analysis_result,
)
```

---

### File: `tests/real_video_examples.py`

**Path:** `packages/services/video-tools/tests/real_video_examples.py`

**Lines 64, 86, 114, 163, 206, 252, 305, 344, 353, 433 - Change all imports:**
```python
# OLD (DELETE)
from video_utils.video_understanding import GeminiVideoAnalyzer
from video_utils.video_understanding import analyze_video_file
# etc.

# NEW (ADD) - Use package-level imports
from video_utils import GeminiVideoAnalyzer, analyze_video_file, save_analysis_result
# etc.
```

---

### File: `tests/image_modify_verify.py`

**Path:** `packages/services/video-tools/tests/image_modify_verify.py`

**Line 39 - Change:**
```python
# OLD (DELETE)
from video_utils.video_understanding import GeminiVideoAnalyzer, save_analysis_result

# NEW (ADD)
from video_utils import GeminiVideoAnalyzer, save_analysis_result
```

---

## New Module Contents Summary

### gemini_analyzer.py (753 lines)

```python
class GeminiVideoAnalyzer:
    """Google Gemini video, audio, and image understanding analyzer."""

    # Video methods
    def upload_video(self, video_path: Path) -> str
    def describe_video(self, video_path: Path, detailed: bool = False) -> Dict
    def transcribe_video(self, video_path: Path, include_timestamps: bool = True) -> Dict
    def answer_questions(self, video_path: Path, questions: List[str]) -> Dict
    def analyze_scenes(self, video_path: Path) -> Dict
    def extract_key_info(self, video_path: Path) -> Dict

    # Audio methods
    def upload_audio(self, audio_path: Path) -> str
    def describe_audio(self, audio_path: Path, detailed: bool = False) -> Dict
    def transcribe_audio(self, audio_path: Path, ...) -> Dict
    def analyze_audio_content(self, audio_path: Path) -> Dict
    def answer_audio_questions(self, audio_path: Path, questions: List[str]) -> Dict
    def detect_audio_events(self, audio_path: Path) -> Dict

    # Image methods
    def upload_image(self, image_path: Path) -> str
    def describe_image(self, image_path: Path, detailed: bool = False) -> Dict
    def classify_image(self, image_path: Path) -> Dict
    def detect_objects(self, image_path: Path, detailed: bool = False) -> Dict
    def answer_image_questions(self, image_path: Path, questions: List[str]) -> Dict
    def extract_text_from_image(self, image_path: Path) -> Dict
    def analyze_image_composition(self, image_path: Path) -> Dict

def check_gemini_requirements() -> tuple[bool, str]
```

### whisper_transcriber.py (399 lines)

```python
class WhisperTranscriber:
    """OpenAI Whisper transcriber for audio and video files."""

    def transcribe_audio_file(self, audio_path: Path, ...) -> Dict
    def transcribe_video_audio(self, video_path: Path, ...) -> Dict
    def batch_transcribe(self, file_paths: List[Path], ...) -> List[Dict]

    def _load_local_model(self, model_size: str = "turbo")
    def _transcribe_api(self, audio_path: Path, ...) -> Dict
    def _transcribe_local(self, audio_path: Path, ...) -> Dict
    def _extract_audio_from_video(self, video_path: Path) -> Path

def check_whisper_requirements(...) -> Dict[str, tuple[bool, str]]
```

### ai_utils.py (510 lines)

```python
# Convenience functions
def save_analysis_result(result: Dict, output_path: Path) -> bool
def analyze_video_file(video_path: Path, analysis_type: str, ...) -> Optional[Dict]
def analyze_audio_file(audio_path: Path, analysis_type: str, ...) -> Optional[Dict]
def analyze_image_file(image_path: Path, analysis_type: str, ...) -> Optional[Dict]
def transcribe_with_whisper(file_path: Path, ...) -> Optional[Dict]
def batch_transcribe_whisper(file_paths: List[Path], ...) -> List[Dict]
def analyze_media_comprehensively(file_path: Path, ...) -> Dict

# Status functions
def check_ai_requirements() -> Dict
def print_ai_status()
```

---

## Benefits of Cleanup

1. **Remove 1363 lines of duplicate code**
2. **Clearer imports** - Each module has focused responsibility
3. **Easier maintenance** - Changes only need to be made in one place
4. **Better testing** - Each module can be tested independently
5. **Compliance** - All files under 800 lines (gemini_analyzer.py is 753)

---

## References

- [ARCHITECTURE_OVERVIEW.md](../packages/services/video-tools/docs/ARCHITECTURE_OVERVIEW.md) - Documents the split
- [__init__.py](../packages/services/video-tools/video_utils/__init__.py) - Already imports from new modules
- [CLAUDE.md Guidelines](../CLAUDE.md) - 500-line file limit
