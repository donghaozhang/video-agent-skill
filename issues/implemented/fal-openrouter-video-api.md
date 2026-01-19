# FAL OpenRouter Video API Integration

**Status: IMPLEMENTED**

This document describes the multi-provider media analyzer architecture that supports both Google Gemini and FAL OpenRouter APIs.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Command Layer                               │
│  (video_commands.py, audio_commands.py, image_commands.py)      │
│                           │                                      │
│                     Uses ai_utils.py                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Abstraction Layer                             │
│                                                                  │
│  ┌──────────────────┐    ┌─────────────────────────────────┐   │
│  │  AnalyzerFactory │───▶│  MediaAnalyzerProtocol (ABC)    │   │
│  │  get_analyzer()  │    └─────────────────────────────────┘   │
│  └──────────────────┘                    ▲                      │
│                              ┌───────────┴───────────┐          │
│                              ▼                       ▼          │
│              ┌─────────────────────────┐  ┌─────────────────┐  │
│              │   GeminiVideoAnalyzer   │  │ FalVideoAnalyzer│  │
│              │   (local files)         │  │ (URL-based)     │  │
│              └─────────────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implemented Files

| File | Description |
|------|-------------|
| `analyzer_protocol.py` | Abstract base class defining the interface |
| `fal_video_analyzer.py` | FAL OpenRouter implementation |
| `analyzer_factory.py` | Factory for creating analyzers |
| `ai_utils.py` | Updated with `provider` parameter support |
| `__init__.py` | Exports new classes |

---

## Available Models (via FAL OpenRouter)

| Model | Provider | Model ID | Best For |
|-------|----------|----------|----------|
| **Gemini 3 Flash Preview** | Google | `google/gemini-3-flash-preview` | Latest fast model |
| **Gemini 3 Pro Preview** | Google | `google/gemini-3-pro-preview` | Latest flagship model |
| Gemini 2.5 Pro | Google | `google/gemini-2.5-pro` | High-quality detailed analysis |
| Gemini 2.5 Flash | Google | `google/gemini-2.5-flash` | Balanced speed/quality |
| Gemini 2.5 Flash Lite | Google | `google/gemini-2.5-flash-lite` | Fastest, cost-effective |
| Gemini 2.0 Flash | Google | `google/gemini-2.0-flash-001` | Previous generation fast |

> **Note:** Model availability may change. Check [FAL OpenRouter API](https://fal.ai/models/openrouter/router/video/enterprise/api) for current models.

---

## Usage Examples

### 1. Using Default Provider (Backward Compatible)

```python
# Existing code works unchanged - uses Gemini by default
from video_utils import analyze_video_file

result = analyze_video_file(Path("video.mp4"), "description")
```

### 2. Specify Provider Explicitly

```python
from video_utils import analyze_video_file

# Use Gemini (default)
result = analyze_video_file(Path("video.mp4"), "description", provider='gemini')

# Use FAL with Gemini 2.5 Flash (requires URL)
result = analyze_video_file(
    "https://example.com/video.mp4",
    "description",
    provider='fal',
    model='google/gemini-2.5-flash'
)
```

### 3. Using Factory Directly

```python
from video_utils import get_analyzer

# Get default analyzer (controlled by env var)
analyzer = get_analyzer()

# Get specific provider
gemini = get_analyzer(provider='gemini')
fal = get_analyzer(provider='fal', model='google/gemini-2.5-flash')

# Analyze video
result = fal.describe_video("https://example.com/video.mp4", detailed=True)
print(result['description'])
print(f"Tokens: {result['usage']['total_tokens']}")
```

### 4. Switch Provider via Environment Variable

```bash
# Switch entire application to FAL
export MEDIA_ANALYZER_PROVIDER=fal
export FAL_DEFAULT_MODEL=google/gemini-2.5-flash

# Run application - all analysis uses FAL now
python your_script.py
```

### 5. Check Provider Status

```python
from video_utils import print_provider_status

print_provider_status()
# Output:
# 🔌 Media Analyzer Providers
# ========================================
# 📌 Default provider: gemini
#
# ✅ GEMINI: Gemini API ready
# ❌ FAL: FAL_KEY environment variable not set
#
# 💡 Switch provider with: export MEDIA_ANALYZER_PROVIDER=fal
```

---

## Environment Configuration

```bash
# .env file

# Default provider selection (optional, defaults to 'gemini')
MEDIA_ANALYZER_PROVIDER=gemini  # or 'fal'

# Gemini configuration
GEMINI_API_KEY=your_gemini_api_key

# FAL configuration (only needed if using FAL)
FAL_KEY=your_fal_api_key
FAL_DEFAULT_MODEL=google/gemini-2.5-flash
```

---

## Key Differences: Gemini vs FAL

| Aspect | Gemini Direct | FAL OpenRouter |
|--------|---------------|----------------|
| **Input** | Local files | URLs only |
| **File Upload** | `genai.upload_file()` | Must host externally |
| **Model Selection** | Hardcoded | Runtime parameter |
| **Authentication** | `GEMINI_API_KEY` | `FAL_KEY` |
| **Cost Tracking** | Manual | Built-in `usage` in response |
| **Multi-model** | Gemini only | Gemini 2.5/3 variants |

---

## Installation

```bash
# FAL client is optional - only install if using FAL provider
pip install fal-client

# Or add to requirements.txt
echo "fal-client>=0.4.0" >> requirements.txt
```

---

## API Reference

### `get_analyzer(provider=None, model=None, **kwargs)`

Get an analyzer instance.

**Parameters:**
- `provider`: `'gemini'` or `'fal'` (default: `MEDIA_ANALYZER_PROVIDER` env var or `'gemini'`)
- `model`: Model ID for FAL (default: `FAL_DEFAULT_MODEL` env var or `'google/gemini-2.5-flash'`)
- `**kwargs`: Additional arguments passed to provider constructor

**Returns:** `MediaAnalyzerProtocol` implementation

### `AnalyzerFactory.list_providers()`

List available providers.

**Returns:** `['gemini']` or `['gemini', 'fal']` if fal-client is installed

### `AnalyzerFactory.get_provider_requirements(provider)`

Check if a provider is properly configured.

**Returns:** `{'available': bool, 'message': str}`

---

## Extending with New Providers

To add a new provider:

1. Create a new class implementing `MediaAnalyzerProtocol`
2. Add it to `analyzer_factory.py`
3. Export from `__init__.py`

Example:

```python
# my_provider_analyzer.py
from .analyzer_protocol import MediaAnalyzerProtocol

class MyProviderAnalyzer(MediaAnalyzerProtocol):
    @property
    def provider_name(self) -> str:
        return "my_provider"

    @property
    def supported_input_types(self) -> List[str]:
        return ["file", "url"]

    def describe_video(self, source, detailed=False):
        # Implementation
        pass

    # ... implement other abstract methods
```

---

## References

- [FAL OpenRouter Video API](https://fal.ai/models/openrouter/router/video/enterprise/api)
- [FAL Python Client](https://github.com/fal-ai/fal)
- [OpenRouter Model List](https://openrouter.ai/models)
