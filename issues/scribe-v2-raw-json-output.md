# Scribe v2 Raw JSON + SRT Output Implementation

**Feature:** Add `--raw-json` and `--srt` flags for word-level timestamps and subtitle generation
**Created:** 2026-01-22
**Updated:** 2026-01-23
**Status:** ✅ COMPLETE
**Priority:** Medium
**Branch:** shot

---

## Overview

Extended the `transcribe` command with:
1. **`--raw-json`** - Complete FAL API response with word-level timestamps ✅ DONE
2. **`--srt`** - Generate SRT subtitle file from word timestamps ✅ DONE

Both outputs can be generated from a single API call - no extra cost.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      transcribe command                          │
├─────────────────────────────────────────────────────────────────┤
│  Input: audio/video file                                         │
│                                                                  │
│  ┌──────────────┐    ┌──────────────────────────────────────┐   │
│  │ Scribe v2    │───▶│ raw_response (word-level timestamps) │   │
│  │ API Call     │    └──────────────────────────────────────┘   │
│  └──────────────┘                     │                          │
│                                       ▼                          │
│         ┌─────────────────────────────────────────────┐         │
│         │           SubtitleConverter                  │         │
│         │  (reusable module for future formats)        │         │
│         ├─────────────────────────────────────────────┤         │
│         │  • words_to_srt(words, config) → .srt ✅    │         │
│         │  • words_to_vtt(words, config) → .vtt (future) │      │
│         │  • words_to_ass(words, config) → .ass (future) │      │
│         └─────────────────────────────────────────────┘         │
│                                                                  │
│  Outputs (all optional, combinable):                             │
│  ├── transcript.txt     (--save-txt, default)                   │
│  ├── metadata.json      (--save-json)                           │
│  ├── raw_words.json     (--raw-json) ✅                         │
│  └── subtitles.srt      (--srt) ✅                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Raw JSON Output ✅ COMPLETE

**Files modified:**
- `packages/providers/fal/speech-to-text/fal_speech_to_text/models/base.py`
- `packages/providers/fal/speech-to-text/fal_speech_to_text/models/scribe_v2.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/speech_to_text.py`

---

## Phase 2: SRT Subtitle Generation ✅ COMPLETE

### Subtask 2.1: Create SubtitleConverter Module ✅

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/subtitle_converter.py`

Created standalone, reusable module for converting word-level timestamps to subtitle formats.

Features:
- `SubtitleConfig` dataclass for configuration
- `words_to_srt()` function for SRT generation
- Segmentation based on: word count, character count, duration, silence gaps
- Skips spacing and audio_event elements
- Extensible for future VTT/ASS support

---

### Subtask 2.2: Add CLI Arguments ✅

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

Added arguments:
- `--srt FILENAME` - Generate SRT subtitle file
- `--srt-max-words N` - Max words per subtitle line (default: 8)
- `--srt-max-duration N` - Max seconds per subtitle (default: 4.0)

---

### Subtask 2.3: Integrate SRT Output ✅

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/speech_to_text.py`

- Added import for `words_to_srt`, `SubtitleConfig`
- Added SRT generation block in `transcribe_command()`
- Proper error handling for missing word timestamps

---

### Subtask 2.4: Unit Tests ✅

**File:** `tests/test_subtitle_converter.py`

15 tests covering:
- Timecode formatting (zero, seconds, minutes, hours, None)
- SRT generation (empty, basic, spacing, max_words, gaps, duration)
- Config defaults and custom values
- Segmentation logic (single word, audio events)

**Test results:** 15 passed

---

## CLI Usage Examples

```bash
# Just raw JSON (word timestamps)
aicp transcribe -i audio.mp3 --raw-json words.json

# Just SRT subtitles
aicp transcribe -i audio.mp3 --srt subtitles.srt

# Both outputs from single API call (recommended)
aicp transcribe -i audio.mp3 --raw-json words.json --srt subtitles.srt

# Customize subtitle generation
aicp transcribe -i audio.mp3 --srt subs.srt --srt-max-words 6 --srt-max-duration 3.0

# Full output suite
aicp transcribe -i audio.mp3 \
    --save-json metadata.json \
    --raw-json words.json \
    --srt subtitles.srt
```

---

## File Summary

| File | Phase | Action | Status |
|------|-------|--------|--------|
| `fal_speech_to_text/models/base.py` | 1 | Modify | ✅ |
| `fal_speech_to_text/models/scribe_v2.py` | 1 | Modify | ✅ |
| `ai_content_pipeline/__main__.py` | 1+2 | Modify | ✅ |
| `ai_content_pipeline/speech_to_text.py` | 1+2 | Modify | ✅ |
| `ai_content_pipeline/subtitle_converter.py` | 2 | **Create** | ✅ |
| `tests/test_subtitle_converter.py` | 2 | **Create** | ✅ |

---

## Benefits

1. **Single API Call**: Both --raw-json and --srt use same transcription result
2. **Extensible**: SubtitleConverter module ready for VTT/ASS formats
3. **Configurable**: Users control subtitle timing/length
4. **No LLM Required**: Deterministic, fast, free conversion
5. **Backward Compatible**: All existing flags unchanged
6. **Well Tested**: 15 unit tests cover core functionality

---

## Future Enhancements (Out of Scope)

- `--vtt` - WebVTT format for web video players
- `--ass` - Advanced SubStation Alpha for styled subtitles
- `--speaker-labels` - Prefix subtitles with speaker IDs
- `--word-highlight` - JSON format for karaoke-style word highlighting

---

## Cost Impact

None - same single API call, just additional local processing.
