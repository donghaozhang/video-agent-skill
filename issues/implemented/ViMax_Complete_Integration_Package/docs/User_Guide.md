# ViMax User Guide

> 🎬 **ViMax** is an AI-driven video generation framework that can automatically convert ideas or scripts into complete videos.

---

## 📋 Table of Contents

1. [Project Introduction](#project-introduction)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [API Configuration](#api-configuration)
5. [Usage Methods](#usage-methods)
6. [FAQ](#faq)

---

## Project Introduction

ViMax provides two main functionalities:

| Feature | Description | Entry File |
|---------|-------------|------------|
| **Idea2Video** | Input idea → Auto-generate script → Generate video | `main_idea2video.py` |
| **Script2Video** | Input script → Directly generate video | `main_script2video.py` |

### Core Capabilities
- 🧬 Intelligent script generation
- 🎥 Multi-shot filming simulation
- 🧸 Automatic reference image selection
- ✅ Consistency checking (characters, scenes)
- ⚡ Parallel generation for high efficiency

---

## System Requirements

- **Operating System**: Windows / Linux
- **Python**: 3.12+
- **Package Manager**: [uv](https://docs.astral.sh/uv/getting-started/installation/)

---

## Installation Steps

### 1. Install uv (if not already installed)

```powershell
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Or use pip
pip install uv
```

### 2. Install Dependencies

```powershell
cd C:\Users\yanie\Desktop\ViMax
uv sync
```

This will automatically create a virtual environment and install all dependencies.

---

## API Configuration

ViMax requires three APIs:

| Service | Purpose | Recommended Options |
|---------|---------|---------------------|
| **Chat Model** | Generate scripts, analyze scenes | OpenRouter / Google AI Studio |
| **Image Generator** | Generate image frames | Google Imagen (AI Studio) |
| **Video Generator** | Generate video segments | Google Veo (AI Studio) |

### Edit Configuration Files

**Idea2Video** → Edit `configs/idea2video.yaml`
**Script2Video** → Edit `configs/script2video.yaml`

```yaml
# Chat model (for script generation)
chat_model:
  init_args:
    model: google/gemini-2.5-flash-lite-preview-09-2025
    model_provider: openai
    api_key: <Your OpenRouter API Key>
    base_url: https://openrouter.ai/api/v1

# Image generator
image_generator:
  class_path: tools.ImageGeneratorNanobananaGoogleAPI
  init_args:
    api_key: <Your Google AI Studio API Key>

# Video generator
video_generator:
  class_path: tools.VideoGeneratorVeoGoogleAPI
  init_args:
    api_key: <Your Google AI Studio API Key>

working_dir: .working_dir/idea2video
```

### Get API Keys

1. **OpenRouter**: https://openrouter.ai/keys
2. **Google AI Studio**: https://aistudio.google.com/apikey

---

## Usage Methods

### Method 1: Idea2Video (Idea to Video)

Edit `main_idea2video.py`:

```python
idea = """
A cat and a dog are best friends. What happens when they meet a new cat?
"""

user_requirement = """
Suitable for children, no more than 3 scenes.
"""

style = "Cartoon"  # Style: Cartoon / Realistic / Anime Style etc.
```

Run:

```powershell
cd C:\Users\yanie\Desktop\ViMax
uv run python main_idea2video.py
```

### Method 2: Script2Video (Script to Video)

Edit `main_script2video.py`:

```python
script = """
EXT. SCHOOL PLAYGROUND - DAY

Xiaoming (10 years old, boy, wearing blue school uniform) is playing soccer.
Xiaohong (10 years old, girl, wearing red dress) is cheering on the side.

XIAOMING: Watch my shot!
XIAOHONG: Go for it! You can do it!

(Xiaoming shoots, the ball goes in)

XIAOHONG: Amazing!
"""

user_requirement = """
Upbeat pace, no more than 10 shots.
"""

style = "Anime Style"
```

Run:

```powershell
cd C:\Users\yanie\Desktop\ViMax
uv run python main_script2video.py
```

---

## Output Results

Videos and intermediate files are saved in the `.working_dir/` directory:

```
.working_dir/
├── idea2video/
│   ├── script.txt        # Generated script
│   ├── storyboard/       # Storyboard images
│   ├── frames/           # Generated image frames
│   └── output.mp4        # Final video
└── script2video/
    └── ...
```

---

## FAQ

### Q: Error `uv: command not found`
Install uv:
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### Q: API call failed
- Check if API Key is correct
- Check network connection
- Google AI Studio's Imagen/Veo may have regional restrictions

### Q: Video generation is very slow
This is normal, AI video generation takes time. You can adjust `max_requests_per_minute` in the configuration file to control the rate.

### Q: Character inconsistency
ViMax has built-in consistency checking, but AI generation may still have deviations. You can try:
- Describe character appearance in detail in the script
- Use more specific style descriptions

---

## 🔗 Related Links

- **GitHub**: https://github.com/HKUDS/ViMax
- **uv Documentation**: https://docs.astral.sh/uv/
- **OpenRouter**: https://openrouter.ai/
- **Google AI Studio**: https://aistudio.google.com/

---

*Last Updated: 2026-02-03*
