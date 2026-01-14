# FAL OpenRouter Video API Integration

## Overview

This document outlines how to use FAL's OpenRouter Video Enterprise API as an alternative to the Google Gemini API for video analysis tasks.

## Why Consider FAL OpenRouter?

| Feature | Google Gemini | FAL OpenRouter |
|---------|---------------|----------------|
| Authentication | `GEMINI_API_KEY` | `FAL_KEY` |
| Model Lock-in | Gemini models only | Multiple VLMs (Gemini, Claude, GPT-4o, etc.) |
| Pricing | Per-request | Pay-per-token |
| Video Support | Direct upload | URL-based |
| File Upload | Required for local files | URL only (need hosting) |

## API Details

- **Endpoint ID**: `openrouter/router/video/enterprise`
- **Base URL**: `https://fal.run/openrouter/router/video/enterprise`
- **Category**: Video-to-Text analysis

## Available Models via OpenRouter

| Model | Provider | Model ID | Best For |
|-------|----------|----------|----------|
| **Gemini 3** | Google | `google/gemini-3` | Latest flagship model |
| **Gemini 3 Flash** | Google | `google/gemini-3-flash` | Fast, cost-effective |
| Gemini 2.5 Pro | Google | `google/gemini-2.5-pro` | High-quality detailed analysis |
| Gemini 2.5 Flash | Google | `google/gemini-2.5-flash` | Balanced speed/quality |
| Claude 3.5 Sonnet | Anthropic | `anthropic/claude-3.5-sonnet` | Nuanced understanding |
| GPT-4o | OpenAI | `openai/gpt-4o` | General-purpose analysis |

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_url` | string | Yes | Video URL (mp4, mpeg, mov, webm, YouTube) |
| `prompt` | string | Yes | Processing instructions for the video |
| `model` | string | Yes | VLM to use (e.g., `google/gemini-3-flash`) |
| `system_prompt` | string | No | Context/instructions to guide model behavior |
| `temperature` | float | No | Response diversity (0-2, default: 1) |
| `max_tokens` | int | No | Maximum tokens in response |
| `reasoning` | bool | No | Include reasoning in response |

## Output Format

```json
{
  "output": "Generated text analysis of video content",
  "usage": {
    "prompt_tokens": 1234,
    "completion_tokens": 567,
    "total_tokens": 1801,
    "cost": 0.0045
  }
}
```

---

## Code Replacement Guide

### Files That Need Modification

```
packages/services/video-tools/video_utils/
├── gemini_analyzer.py          # REPLACE: Main analyzer class
├── ai_utils.py                 # UPDATE: Import and instantiation
├── command_utils.py            # NO CHANGE (uses ai_utils)
└── ai_commands/
    ├── image_commands.py       # UPDATE: Import statements
    ├── video_commands.py       # UPDATE: Import statements
    └── audio_commands.py       # UPDATE: Import statements
```

---

### 1. Replace `gemini_analyzer.py` (Primary Change)

**Current File**: `packages/services/video-tools/video_utils/gemini_analyzer.py`

**Current Code (lines 19-44)**:
```python
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiVideoAnalyzer:
    """Google Gemini video, audio, and image understanding analyzer."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key."""
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "Google GenerativeAI not installed. Run: pip install google-generativeai"
            )

        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY environment variable or pass api_key parameter"
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
```

**Replace With** - Create new file `fal_video_analyzer.py`:
```python
"""
FAL OpenRouter Video Analyzer - Alternative to GeminiVideoAnalyzer.

Uses FAL's OpenRouter API to access multiple VLMs including Gemini 3, Claude, GPT-4o.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False


class FalVideoAnalyzer:
    """FAL OpenRouter video, audio, and image understanding analyzer."""

    SUPPORTED_MODELS = [
        "google/gemini-3",           # Latest Gemini flagship
        "google/gemini-3-flash",     # Fast Gemini 3
        "google/gemini-2.5-pro",
        "google/gemini-2.5-flash",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
    ]

    def __init__(self, api_key: Optional[str] = None, model: str = "google/gemini-3-flash"):
        """Initialize with FAL API key and model selection."""
        if not FAL_AVAILABLE:
            raise ImportError(
                "FAL client not installed. Run: pip install fal-client"
            )

        self.api_key = api_key or os.getenv('FAL_KEY')
        if not self.api_key:
            raise ValueError(
                "FAL API key required. Set FAL_KEY environment variable or pass api_key parameter"
            )

        os.environ['FAL_KEY'] = self.api_key
        self.model = model

    def _analyze(self, video_url: str, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Core analysis method using FAL OpenRouter."""
        input_params = {
            "video_url": video_url,
            "prompt": prompt,
            "model": self.model,
        }

        if system_prompt:
            input_params["system_prompt"] = system_prompt

        result = fal_client.subscribe(
            "openrouter/router/video/enterprise",
            arguments=input_params
        )

        return {
            "output": result.get("output", ""),
            "usage": result.get("usage", {}),
            "model": self.model
        }

    def describe_video(self, video_url: str, detailed: bool = False) -> Dict[str, Any]:
        """Generate video description and summary."""
        if detailed:
            prompt = """Analyze this video in detail and provide:
1. Overall summary and main topic
2. Key scenes and their timestamps
3. Visual elements (objects, people, settings, actions)
4. Audio content (speech, music, sounds)
5. Mood and tone
6. Technical observations (quality, style, etc.)

Provide structured analysis with clear sections."""
        else:
            prompt = """Provide a concise description of this video including:
- Main content and topic
- Key visual elements
- Brief summary of what happens
- Duration and pacing"""

        print("🤖 Generating video description via FAL...")
        result = self._analyze(video_url, prompt)

        return {
            'description': result['output'],
            'detailed': detailed,
            'analysis_type': 'description',
            'usage': result['usage']
        }

    def transcribe_video(self, video_url: str, include_timestamps: bool = True) -> Dict[str, Any]:
        """Transcribe audio content from video."""
        if include_timestamps:
            prompt = """Transcribe all spoken content in this video. Include:
1. Complete transcription of all speech
2. Speaker identification if multiple speakers
3. Approximate timestamps for each segment
4. Note any non-speech audio (music, sound effects, silence)

Format as a clean, readable transcript with timestamps."""
        else:
            prompt = """Provide a complete transcription of all spoken content in this video.
Focus on accuracy and readability. Include speaker changes if multiple people speak."""

        print("🎤 Transcribing video audio via FAL...")
        result = self._analyze(video_url, prompt)

        return {
            'transcription': result['output'],
            'include_timestamps': include_timestamps,
            'analysis_type': 'transcription',
            'usage': result['usage']
        }

    def analyze_scenes(self, video_url: str) -> Dict[str, Any]:
        """Analyze video scenes and create timeline breakdown."""
        prompt = """Analyze this video and break it down into distinct scenes or segments. For each scene, provide:
1. Start and end timestamps (approximate)
2. Scene description and main content
3. Key visual elements and actions
4. Audio content (speech, music, effects)
5. Scene transitions and cuts

Create a detailed timeline of the video content."""

        print("🎬 Analyzing video scenes via FAL...")
        result = self._analyze(video_url, prompt)

        return {
            'scene_analysis': result['output'],
            'analysis_type': 'scenes',
            'usage': result['usage']
        }

    def answer_questions(self, video_url: str, questions: List[str]) -> Dict[str, Any]:
        """Answer specific questions about the video."""
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
        prompt = f"""Analyze this video and answer the following questions:

{questions_text}

Provide detailed, accurate answers based on what you observe in the video. If a question cannot be answered from the video content, please state that clearly."""

        print("❓ Answering questions about video via FAL...")
        result = self._analyze(video_url, prompt)

        return {
            'questions': questions,
            'answers': result['output'],
            'analysis_type': 'qa',
            'usage': result['usage']
        }

    def extract_key_info(self, video_url: str) -> Dict[str, Any]:
        """Extract key information and insights from video."""
        prompt = """Extract key information from this video including:
1. Main topics and themes
2. Important facts or data mentioned
3. Key people, places, or objects
4. Notable quotes or statements
5. Action items or conclusions
6. Technical specifications if relevant
7. Timestamps for important moments

Provide structured, actionable information."""

        print("🔍 Extracting key information via FAL...")
        result = self._analyze(video_url, prompt)

        return {
            'key_info': result['output'],
            'analysis_type': 'extraction',
            'usage': result['usage']
        }


def check_fal_requirements() -> tuple[bool, str]:
    """Check if FAL requirements are met."""
    if not FAL_AVAILABLE:
        return False, "FAL client library not installed. Run: pip install fal-client"

    api_key = os.getenv('FAL_KEY')
    if not api_key:
        return False, "FAL_KEY environment variable not set"

    return True, "FAL API ready"
```

---

### 2. Update `ai_utils.py`

**File**: `packages/services/video-tools/video_utils/ai_utils.py`

**Current Import (line 12)**:
```python
from .gemini_analyzer import GeminiVideoAnalyzer, check_gemini_requirements
```

**Add FAL Import**:
```python
from .gemini_analyzer import GeminiVideoAnalyzer, check_gemini_requirements
# Optional: FAL alternative
try:
    from .fal_video_analyzer import FalVideoAnalyzer, check_fal_requirements
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False
```

**Update `analyze_video_file` function (lines 87-119)**:
```python
def analyze_video_file(video_path: Path, analysis_type: str = "description",
                      questions: Optional[List[str]] = None, detailed: bool = False,
                      use_fal: bool = False, video_url: Optional[str] = None,
                      model: str = "google/gemini-3-flash") -> Optional[Dict[str, Any]]:
    """Convenience function to analyze video using Gemini or FAL.

    Args:
        video_path: Path to video file (for Gemini)
        analysis_type: Type of analysis
        questions: List of questions for Q&A analysis
        detailed: Whether to perform detailed analysis
        use_fal: If True, use FAL OpenRouter instead of Gemini
        video_url: Video URL (required for FAL)
        model: Model to use with FAL (default: google/gemini-3-flash)

    Returns:
        Analysis result dictionary or None if failed
    """
    try:
        if use_fal:
            if not video_url:
                print("❌ video_url required for FAL analysis")
                return None
            analyzer = FalVideoAnalyzer(model=model)

            if analysis_type == "description":
                return analyzer.describe_video(video_url, detailed=detailed)
            elif analysis_type == "transcription":
                return analyzer.transcribe_video(video_url, include_timestamps=True)
            elif analysis_type == "scenes":
                return analyzer.analyze_scenes(video_url)
            elif analysis_type == "extraction":
                return analyzer.extract_key_info(video_url)
            elif analysis_type == "qa" and questions:
                return analyzer.answer_questions(video_url, questions)
        else:
            # Original Gemini implementation
            analyzer = GeminiVideoAnalyzer()
            # ... existing code ...
```

---

### 3. Update `ai_commands/image_commands.py`

**File**: `packages/services/video-tools/video_utils/ai_commands/image_commands.py`

**Current Import (lines 153-155 in `cmd_describe_images`)**:
```python
from ..gemini_analyzer import GeminiVideoAnalyzer
gemini_analyzer = GeminiVideoAnalyzer()
```

**To Support FAL** - add optional parameter:
```python
def cmd_describe_images(use_fal: bool = False, model: str = "google/gemini-3-flash") -> None:
    """Quick description of images using Gemini or FAL."""
    if use_fal:
        from ..fal_video_analyzer import FalVideoAnalyzer
        analyzer = FalVideoAnalyzer(model=model)
        # Note: FAL requires URLs, not local files
    else:
        from ..gemini_analyzer import GeminiVideoAnalyzer
        analyzer = GeminiVideoAnalyzer()
```

---

### 4. Update `ai_commands/video_commands.py`

Same pattern as image_commands.py - add `use_fal` parameter to video analysis functions.

---

### 5. Update `ai_commands/audio_commands.py`

Same pattern - add `use_fal` parameter to audio analysis functions.

---

## Environment Setup

Add to your `.env` file:

```bash
# Google Gemini (existing)
GEMINI_API_KEY=your_gemini_api_key

# FAL AI (new - for OpenRouter Video API)
FAL_KEY=your_fal_api_key
```

## Installation

```bash
# Install FAL client
pip install fal-client

# Or add to requirements.txt
echo "fal-client>=0.4.0" >> requirements.txt
pip install -r requirements.txt
```

## Migration Checklist

- [ ] Install FAL client: `pip install fal-client`
- [ ] Add `FAL_KEY` to environment variables
- [ ] Create `fal_video_analyzer.py` in `video_utils/`
- [ ] Update `ai_utils.py` imports and functions
- [ ] Update CLI commands to accept `--use-fal` flag
- [ ] Add model selection option (`--model google/gemini-3-flash`)
- [ ] Update tests for FAL integration
- [ ] Update documentation

## Key Differences: Gemini vs FAL

| Aspect | Gemini Direct | FAL OpenRouter |
|--------|---------------|----------------|
| **Local Files** | `genai.upload_file(path)` | Must host file, use URL |
| **Model Selection** | Hardcoded in code | Runtime parameter |
| **Authentication** | `GEMINI_API_KEY` | `FAL_KEY` |
| **Cost Tracking** | Manual | Built-in `usage` in response |
| **Multi-model** | Gemini only | Gemini, Claude, GPT-4o |

## Limitations

1. **URL-based only**: Videos must be accessible via URL (no direct file upload like Gemini)
   - Workaround: Use cloud storage (S3, GCS, Azure Blob) or FAL's file upload API
2. **Dependency on OpenRouter**: Adds another layer between you and the model provider
3. **Cost tracking**: Need to monitor usage tokens for billing

## Code Examples

### Python - Quick Start

```python
from video_utils.fal_video_analyzer import FalVideoAnalyzer

# Use Gemini 3 Flash (fast)
analyzer = FalVideoAnalyzer(model="google/gemini-3-flash")

# Or use Gemini 3 (highest quality)
analyzer = FalVideoAnalyzer(model="google/gemini-3")

# Analyze video
result = analyzer.describe_video(
    video_url="https://example.com/video.mp4",
    detailed=True
)

print(result['description'])
print(f"Tokens used: {result['usage']['total_tokens']}")
print(f"Cost: ${result['usage']['cost']}")
```

### JavaScript

```javascript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("openrouter/router/video/enterprise", {
  input: {
    video_url: "https://example.com/video.mp4",
    prompt: "Describe the video content in detail",
    model: "google/gemini-3-flash"  // or "google/gemini-3"
  },
  logs: true
});

console.log(result.data.output);
console.log(`Cost: $${result.data.usage.cost}`);
```

## References

- [FAL OpenRouter Video API](https://fal.ai/models/openrouter/router/video/enterprise/api)
- [FAL Python Client](https://github.com/fal-ai/fal)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter Model List](https://openrouter.ai/models)
