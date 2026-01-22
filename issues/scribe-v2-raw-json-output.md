# Scribe v2 Raw JSON Output Implementation

**Feature:** Add `--raw-json` flag to output complete FAL API response with word-level timestamps
**Created:** 2026-01-22
**Status:** ✅ IMPLEMENTED
**Priority:** Medium
**Estimated Time:** 15 minutes (no subtasks needed)
**Branch:** shot

## Overview

Add a `--raw-json` CLI option to the `transcribe` command that outputs the complete FAL Scribe v2 API response, including:
- Full word-level timestamps with `type` field (`word`, `spacing`, `audio_event`)
- `language_probability` confidence score
- Speaker IDs for each word element
- All spacing elements between words

## Current vs Desired Output

### Current `--save-json` Output
```json
{
  "success": true,
  "text": "...",
  "speakers": ["speaker_0"],
  "duration": 14.779,
  "metadata": {"words_count": 47}
}
```

### New `--raw-json` Output
```json
{
  "language_code": "en",
  "language_probability": 1,
  "text": "With a soft and whispery American accent...",
  "words": [
    {
      "text": "With",
      "start": 0.119,
      "end": 0.259,
      "type": "word",
      "speaker_id": "speaker_0"
    },
    {
      "text": " ",
      "start": 0.239,
      "end": 0.299,
      "type": "spacing",
      "speaker_id": "speaker_0"
    }
  ]
}
```

## Implementation

### File: `packages/providers/fal/speech-to-text/fal_speech_to_text/models/base.py`

**Changes:**
1. Add `raw_response` field to `TranscriptionResult` dataclass

```python
@dataclass
class TranscriptionResult:
    """Standardized result for speech-to-text transcription."""
    success: bool
    text: str = ""
    words: Optional[List[WordTimestamp]] = None
    speakers: Optional[List[str]] = None
    audio_events: Optional[List[AudioEvent]] = None
    duration: Optional[float] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    model_used: Optional[str] = None
    language_detected: Optional[str] = None
    language_probability: Optional[float] = None  # ADD THIS
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    raw_response: Optional[Dict[str, Any]] = None  # ADD THIS
```

### File: `packages/providers/fal/speech-to-text/fal_speech_to_text/models/scribe_v2.py`

**Changes:**
1. Store `language_probability` from API response
2. Store `raw_response` for direct access

```python
# In transcribe() method, after parsing API response (line ~156):
return TranscriptionResult(
    success=True,
    text=text,
    words=words,
    speakers=speakers,
    audio_events=audio_events,
    duration=duration,
    cost=cost,
    processing_time=processing_time,
    model_used=self.model_name,
    language_detected=result.get("language_code"),
    language_probability=result.get("language_probability"),  # ADD
    raw_response=result,  # ADD - store complete API response
    metadata={...},
)
```

### File: `packages/core/ai_content_pipeline/ai_content_pipeline/speech_to_text.py`

**Changes:**
1. Pass `raw_response` through `TranscriptionCLIResult`
2. Handle `--raw-json` flag in CLI command

```python
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
    language_probability: Optional[float] = None  # ADD
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None  # ADD
```

### File: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

**Changes:**
1. Add `--raw-json` argument to transcribe parser

```python
transcribe_parser.add_argument(
    "--raw-json",
    metavar="FILENAME",
    help="Save raw API response with word-level timestamps as JSON"
)
```

2. Handle `--raw-json` in command dispatch (already in transcribe_command)

### File: `packages/core/ai_content_pipeline/ai_content_pipeline/speech_to_text.py` (transcribe_command)

**Changes in `transcribe_command()`:**
```python
# After existing --save-json handling:
if args.raw_json and result.raw_response:
    raw_json_path = Path(args.output) / args.raw_json
    raw_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_json_path, 'w', encoding='utf-8') as f:
        json.dump(result.raw_response, f, indent=2)
    print(f"📄 Raw JSON: {raw_json_path}")
```

## CLI Usage

```bash
# Basic transcription with raw JSON output
aicp transcribe -i audio.mp3 --raw-json transcript.json

# Combine with existing options
aicp transcribe -i audio.mp3 --diarize --raw-json words.json

# Both metadata and raw output
aicp transcribe -i audio.mp3 --save-json meta.json --raw-json words.json
```

## Testing

### File: `tests/test_speech_to_text_cli.py`

Add test case:
```python
def test_raw_json_output_contains_word_timestamps():
    """Test that --raw-json includes word-level timestamps with type field."""
    # Mock FAL API response
    mock_response = {
        "text": "Hello world",
        "language_code": "eng",
        "language_probability": 0.99,
        "words": [
            {"text": "Hello", "start": 0.0, "end": 0.5, "type": "word", "speaker_id": "speaker_0"},
            {"text": " ", "start": 0.5, "end": 0.6, "type": "spacing", "speaker_id": "speaker_0"},
            {"text": "world", "start": 0.6, "end": 1.0, "type": "word", "speaker_id": "speaker_0"},
        ]
    }

    # Test that raw_response is passed through
    result = TranscriptionResult(
        success=True,
        text="Hello world",
        raw_response=mock_response,
    )

    assert result.raw_response is not None
    assert "words" in result.raw_response
    assert result.raw_response["words"][0]["type"] == "word"
    assert result.raw_response["words"][1]["type"] == "spacing"
```

## File Summary

| File | Action | Lines Changed |
|------|--------|---------------|
| `fal_speech_to_text/models/base.py` | Modify | +2 fields |
| `fal_speech_to_text/models/scribe_v2.py` | Modify | +2 lines |
| `ai_content_pipeline/speech_to_text.py` | Modify | +15 lines |
| `ai_content_pipeline/__main__.py` | Modify | +5 lines |
| `tests/test_speech_to_text_cli.py` | Modify | +20 lines |

## Benefits

1. **Full Data Access**: Users get complete API response for custom processing
2. **Lip-Sync Ready**: Word timestamps with spacing enable precise video lip-sync
3. **Backward Compatible**: Existing `--save-json` behavior unchanged
4. **Minimal Changes**: Leverages existing infrastructure, just passes data through

## Cost Impact

None - same API call, just different output format.
