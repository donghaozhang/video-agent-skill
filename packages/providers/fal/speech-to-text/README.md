# FAL Speech-to-Text

Speech-to-text transcription using FAL AI models.

## Installation

```bash
pip install -e packages/providers/fal/speech-to-text
```

## Quick Start

```python
from fal_speech_to_text import FALSpeechToTextGenerator

generator = FALSpeechToTextGenerator()

# Basic transcription
result = generator.transcribe(
    audio_url="https://example.com/audio.mp3"
)
print(result.text)

# With speaker diarization
result = generator.transcribe_with_diarization(
    audio_url="https://example.com/meeting.mp3"
)
for speaker in result.speakers:
    print(f"Speaker: {speaker}")
print(result.text)
```

## Available Models

| Model | Description | Cost |
|-------|-------------|------|
| `scribe_v2` | ElevenLabs Scribe v2 | $0.008/min |

## Features

- **99 Languages**: Auto-detect or specify language
- **Word Timestamps**: Precise timing for each word
- **Speaker Diarization**: Identify who said what
- **Audio Events**: Tag laughter, applause, music, etc.
- **Keyterms**: Bias transcription toward specific terms

## API Reference

### FALSpeechToTextGenerator

```python
generator.transcribe(audio_url, model="scribe_v2", **kwargs)
generator.transcribe_with_diarization(audio_url, model="scribe_v2", **kwargs)
generator.list_models()
generator.get_model_info(model)
generator.estimate_cost(model, duration_minutes, **kwargs)
```

### TranscriptionResult

```python
result.success      # bool
result.text         # str - Full transcription
result.words        # List[WordTimestamp] - Word-level timestamps
result.speakers     # List[str] - Unique speaker IDs
result.audio_events # List[AudioEvent] - Detected audio events
result.duration     # float - Audio duration in seconds
result.cost         # float - Estimated cost in USD
```

## Environment Variables

```
FAL_KEY=your_fal_api_key
```
