# Video Analysis Guide

Analyze videos with AI to extract timelines, descriptions, and transcriptions using Gemini models.

## Overview

The AI Content Pipeline includes powerful video analysis capabilities powered by Google's Gemini models through FAL AI. Extract detailed information from any video including:

- **Timeline analysis** - Scene-by-scene breakdown with timestamps
- **Video descriptions** - Comprehensive descriptions of content
- **Transcriptions** - Extract spoken words and dialogue

## Quick Start

### Basic Analysis

```bash
# Analyze a video with default settings
ai-content-pipeline analyze-video -i video.mp4

# Analyze with specific model
ai-content-pipeline analyze-video -i video.mp4 -m gemini-3-pro
```

### Analysis Types

```bash
# Timeline analysis (scene-by-scene breakdown)
ai-content-pipeline analyze-video -i video.mp4 -t timeline

# Full description
ai-content-pipeline analyze-video -i video.mp4 -t describe

# Transcription (extract speech)
ai-content-pipeline analyze-video -i video.mp4 -t transcribe
```

---

## Available Models

### List Video Analysis Models

```bash
ai-content-pipeline list-video-models
```

### Model Comparison

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `gemini-3-pro` | ★★★ | ★★★★★ | Highest quality analysis |
| `gemini-2.5-pro` | ★★★★ | ★★★★ | Balanced performance |
| `gemini-2.5-flash` | ★★★★★ | ★★★ | Fast analysis |
| `gemini-direct` | ★★★★ | ★★★★ | Direct API access |

### Model Selection

```bash
# Premium quality (detailed analysis)
ai-content-pipeline analyze-video -i video.mp4 -m gemini-3-pro

# Fast analysis (quick results)
ai-content-pipeline analyze-video -i video.mp4 -m gemini-2.5-flash

# Balanced (good quality, reasonable speed)
ai-content-pipeline analyze-video -i video.mp4 -m gemini-2.5-pro
```

---

## Analysis Types

### Timeline Analysis

Extract a scene-by-scene breakdown with timestamps.

```bash
ai-content-pipeline analyze-video -i video.mp4 -t timeline
```

**Output example:**
```
Timeline Analysis for: video.mp4

00:00 - 00:05: Opening shot of city skyline at sunset
00:05 - 00:12: Camera pans down to street level
00:12 - 00:20: Person walking through busy intersection
00:20 - 00:30: Close-up of street vendors
00:30 - 00:45: Wide shot of park with children playing
```

**Use cases:**
- Video editing (find specific scenes)
- Content cataloging
- Accessibility descriptions
- Social media clip identification

### Description Analysis

Get a comprehensive description of video content.

```bash
ai-content-pipeline analyze-video -i video.mp4 -t describe
```

**Output example:**
```
Video Description:

This video captures a vibrant urban sunset scene. The footage begins with
a wide establishing shot of a modern city skyline, with warm orange and
purple hues painting the sky. The camera work is smooth and cinematic,
gradually descending to street level where pedestrians navigate a busy
intersection. Notable elements include...
```

**Use cases:**
- SEO metadata generation
- Accessibility descriptions
- Content summaries
- Archive documentation

### Transcription

Extract spoken words and dialogue from videos.

```bash
ai-content-pipeline analyze-video -i video.mp4 -t transcribe
```

**Output example:**
```
Transcription:

[00:00] Speaker 1: Welcome to today's presentation.
[00:03] Speaker 1: We'll be discussing the future of AI.
[00:08] Speaker 2: Thank you for having me.
[00:10] Speaker 2: I'm excited to share our latest research.
```

**Use cases:**
- Subtitles/captions generation
- Meeting notes
- Podcast transcription
- Content searchability

---

## Python API

### Basic Usage

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Analyze video
result = manager.analyze_video(
    input_path="video.mp4",
    model="gemini-3-pro",
    analysis_type="timeline"
)

print(result.analysis)
print(f"Duration: {result.video_duration}s")
```

### Analysis Types

```python
# Timeline analysis
timeline = manager.analyze_video(
    input_path="video.mp4",
    analysis_type="timeline"
)

# Full description
description = manager.analyze_video(
    input_path="video.mp4",
    analysis_type="describe"
)

# Transcription
transcript = manager.analyze_video(
    input_path="video.mp4",
    analysis_type="transcribe"
)
```

### Custom Prompts

```python
# Custom analysis with specific prompt
result = manager.analyze_video(
    input_path="video.mp4",
    model="gemini-3-pro",
    custom_prompt="Identify all products shown in this video and describe their features"
)
```

---

## YAML Pipeline Integration

### Video Analysis Step

```yaml
name: "Analyze and Process"
steps:
  # Analyze existing video
  - name: "analysis"
    type: "video_analysis"
    params:
      input: "input/video.mp4"
      model: "gemini-3-pro"
      analysis_type: "timeline"
```

### Generate Then Analyze

```yaml
name: "Generate and Analyze"
steps:
  # Generate video
  - name: "video"
    type: "text_to_video"
    model: "hailuo_pro"
    params:
      prompt: "Ocean waves at sunset"

  # Analyze the generated video
  - name: "analysis"
    type: "video_analysis"
    input_from: "video"
    params:
      model: "gemini-2.5-flash"
      analysis_type: "describe"
```

### Batch Analysis

```yaml
name: "Batch Video Analysis"
settings:
  parallel: true
steps:
  - type: "parallel_group"
    steps:
      - type: "video_analysis"
        params:
          input: "videos/video1.mp4"
          analysis_type: "timeline"
      - type: "video_analysis"
        params:
          input: "videos/video2.mp4"
          analysis_type: "timeline"
      - type: "video_analysis"
        params:
          input: "videos/video3.mp4"
          analysis_type: "timeline"
```

---

## Best Practices

### Choosing Analysis Type

| Goal | Analysis Type | Model |
|------|---------------|-------|
| Find specific scenes | `timeline` | gemini-2.5-flash |
| Create descriptions | `describe` | gemini-3-pro |
| Generate captions | `transcribe` | gemini-2.5-pro |
| Quick overview | `describe` | gemini-2.5-flash |

### Video Preparation

**For best results:**
- Use clear, high-quality video
- Keep videos under 10 minutes for faster processing
- Ensure good audio quality for transcription
- Avoid heavily compressed videos

**Supported formats:**
- MP4 (recommended)
- WebM
- MOV
- AVI

### Performance Tips

```bash
# For large videos, use faster models
ai-content-pipeline analyze-video -i large_video.mp4 -m gemini-2.5-flash

# For detailed analysis, use premium models
ai-content-pipeline analyze-video -i important_video.mp4 -m gemini-3-pro
```

---

## Common Use Cases

### Content Cataloging

```python
import os
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Analyze all videos in a directory
video_dir = "videos/"
catalog = []

for filename in os.listdir(video_dir):
    if filename.endswith(('.mp4', '.webm', '.mov')):
        result = manager.analyze_video(
            input_path=os.path.join(video_dir, filename),
            analysis_type="describe",
            model="gemini-2.5-flash"
        )
        catalog.append({
            'filename': filename,
            'description': result.analysis
        })

# Save catalog
import json
with open('video_catalog.json', 'w') as f:
    json.dump(catalog, f, indent=2)
```

### Automated Captioning

```python
# Generate captions for a video
result = manager.analyze_video(
    input_path="presentation.mp4",
    analysis_type="transcribe",
    model="gemini-2.5-pro"
)

# Save as SRT format
def to_srt(transcript):
    # Parse and convert to SRT format
    lines = transcript.split('\n')
    srt_content = ""
    for i, line in enumerate(lines, 1):
        # Parse timestamp and text
        # Format: [00:00] Text
        if line.strip():
            srt_content += f"{i}\n"
            srt_content += f"00:00:00,000 --> 00:00:05,000\n"  # Adjust timing
            srt_content += f"{line}\n\n"
    return srt_content

with open('captions.srt', 'w') as f:
    f.write(to_srt(result.analysis))
```

### Video Search Index

```python
# Create searchable index of video content
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

def index_video(video_path):
    """Create searchable index for a video."""
    # Get timeline
    timeline = manager.analyze_video(
        input_path=video_path,
        analysis_type="timeline"
    )

    # Get full description
    description = manager.analyze_video(
        input_path=video_path,
        analysis_type="describe"
    )

    return {
        'path': video_path,
        'timeline': timeline.analysis,
        'description': description.analysis,
        'keywords': extract_keywords(description.analysis)
    }

def extract_keywords(text):
    """Extract key terms from description."""
    # Simple keyword extraction
    words = text.lower().split()
    # Filter common words and return unique terms
    return list(set(w for w in words if len(w) > 4))[:20]
```

---

## Troubleshooting

### Common Issues

**Issue:** Analysis taking too long
```bash
# Use faster model
ai-content-pipeline analyze-video -i video.mp4 -m gemini-2.5-flash
```

**Issue:** Poor transcription quality
- Check audio quality in source video
- Use `gemini-3-pro` for better accuracy
- Ensure speakers are clear and not overlapping

**Issue:** Missing timeline details
- Use `gemini-3-pro` for more detailed analysis
- Try shorter video segments
- Ensure video has distinct scenes

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Video too long" | Exceeds model limit | Split into segments |
| "Unsupported format" | Invalid video format | Convert to MP4 |
| "Analysis failed" | API or network issue | Retry with different model |

---

## Cost Considerations

| Model | Approximate Cost | Notes |
|-------|------------------|-------|
| gemini-2.5-flash | $0.01-0.05/video | Budget option |
| gemini-2.5-pro | $0.05-0.15/video | Balanced |
| gemini-3-pro | $0.10-0.30/video | Premium quality |

*Costs vary based on video length and complexity.*

```bash
# Estimate cost before analysis
ai-content-pipeline estimate-cost --type video_analysis --input video.mp4
```

---

[Back to Documentation Index](../index.md)
