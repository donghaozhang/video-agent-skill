# ViMax → video-agent-skill Integration Plan

## Overview

This document details how to integrate ViMax's unique features into the video-agent-skill project, including files to copy, functions to add/modify, and integration steps.

**NEW: CLI-First Approach** - Most ViMax features can now be achieved using the `ai-content-pipeline` CLI without code changes.

---

## 🚀 Quick Start: CLI Commands for ViMax Features

### Installation & Setup

```bash
# Install the package
pip install -e .

# Verify installation
ai-content-pipeline --help

# Setup environment (creates .env template)
ai-content-pipeline setup

# List all available models
ai-content-pipeline list-models
```

### Environment Variables Required

```bash
# Create .env file with:
FAL_KEY=your_fal_api_key           # Required for most features
GEMINI_API_KEY=your_gemini_key     # For video analysis
OPENROUTER_API_KEY=your_key        # For prompt generation
```

---

## 📋 ViMax Feature → CLI Command Mapping

### 1. Character Portraits Generation

**ViMax Feature**: Generate multi-angle character portraits (front/side/back)

**CLI Solution**: Use `generate-image` with specific prompts or `generate-grid` for batch generation

```bash
# Single character portrait
ai-content-pipeline generate-image \
  --text "Portrait of a young samurai warrior, front view, detailed face, cinematic lighting" \
  --model flux_dev

# Generate character sheet (2x2 grid with multiple angles)
ai-content-pipeline generate-grid \
  --prompt-file input/character_sheet.md \
  --grid 2x2 \
  --style "consistent character design, same person"
```

**Example `character_sheet.md`:**
```markdown
# Character: Samurai Warrior

## Style
Anime style, consistent character design, detailed, professional

## Panels
1. Front view portrait, neutral expression
2. Side profile view, looking right
3. Three-quarter view, slight smile
4. Back view, showing hair and costume details
```

---

### 2. Storyboard Generation (Script → Visual Storyboard)

**ViMax Feature**: StoryboardArtist converts scripts to visual storyboards

**CLI Solution**: `generate-grid` command with scene descriptions

```bash
# Generate 3x3 storyboard from scene descriptions
ai-content-pipeline generate-grid \
  --prompt-file input/storyboard.md \
  --grid 3x3 \
  --model nano_banana_pro \
  -o output/storyboard

# Generate 2x2 story panels
ai-content-pipeline generate-grid \
  --prompt-file input/story_panels.md \
  --grid 2x2 \
  --style "comic book style, consistent art"
```

**Example `storyboard.md`:**
```markdown
# Storyboard: Sunrise Battle

## Style
Cinematic, dramatic lighting, film noir aesthetic

## Panels
1. Wide shot: Lone samurai standing at mountain peak, dawn breaking
2. Medium shot: Samurai drawing sword, determined expression
3. Close-up: Sword blade reflecting sunlight
4. Action shot: Samurai leaping into battle
5. Wide shot: Battle clash, dust and debris
6. Close-up: Intense eye contact between fighters
7. Dynamic shot: Sword strike mid-motion
8. Medium shot: Victory pose against sunset
9. Wide shot: Samurai walking away, mountain backdrop
```

---

### 3. Image-to-Video Pipeline (Storyboard → Video)

**ViMax Feature**: CameraImageGenerator creates videos from storyboard frames

**CLI Solution**: YAML pipeline with `run-chain` command

```bash
# Run complete shot workflow (image → split → video → concat)
ai-content-pipeline run-chain --config input/pipelines/shot_workflow.yaml

# Enable parallel processing for faster execution
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain \
  --config input/pipelines/vimax_pipeline.yaml
```

**Create `input/pipelines/vimax_pipeline.yaml`:**
```yaml
# ViMax-style Idea-to-Video Pipeline
pipeline_name: vimax_idea2video
output_dir: output/vimax

steps:
  # Step 1: Generate storyboard grid
  - type: text_to_image
    model: flux_dev
    enabled: true
    params:
      prompt: |
        A 2x2 comic grid showing 4 sequential scenes:
        [Panel 1] Character introduction, establishing shot
        [Panel 2] Rising action, movement begins
        [Panel 3] Climax, dramatic moment
        [Panel 4] Resolution, final pose
        Consistent character design across all panels
      aspect_ratio: "1:1"

  # Step 2: Split into individual frames
  - type: split_image
    model: local
    enabled: true
    params:
      grid_type: "2x2"
      output_prefix: "scene"

  # Step 3: Animate each scene
  - type: image_to_video
    model: kling
    enabled: true
    params:
      prompts:
        - "Character introduction, subtle movement, cinematic"
        - "Character moving, dynamic action, smooth motion"
        - "Dramatic climax moment, intense action"
        - "Resolution scene, gentle movement, peaceful"
      duration: 5
      parallel: true
      max_workers: 2

  # Step 4: Combine into final video
  - type: concat_videos
    model: ffmpeg
    enabled: true
    params:
      output_filename: "final_video.mp4"
```

---

### 4. Character Consistency (Reference-Based Video)

**ViMax Feature**: ReferenceImageSelector maintains character consistency across shots

**CLI Solution**: Avatar generation with reference images

```bash
# Generate video with character reference images
ai-content-pipeline generate-avatar \
  --reference-images character_front.jpg character_side.jpg \
  --prompt "Character walking through a forest, maintaining appearance" \
  --model kling_ref_to_video

# Style transfer with video reference
ai-content-pipeline generate-avatar \
  --reference-images style_ref.jpg \
  --video input_video.mp4 \
  --prompt "Same scene with new visual style" \
  --model kling_v2v_reference
```

---

### 5. Video Analysis & Scene Detection

**ViMax Feature**: Scene Detection Frame Extraction using scenedetect

**CLI Solution**: `analyze-video` command with Gemini

```bash
# Analyze video with timeline breakdown
ai-content-pipeline analyze-video \
  -i input/video.mp4 \
  -t timeline \
  -m gemini-3-pro

# Describe video content
ai-content-pipeline analyze-video \
  -i input/video.mp4 \
  -t describe

# Transcribe video audio
ai-content-pipeline analyze-video \
  -i input/video.mp4 \
  -t transcribe

# List available analysis models
ai-content-pipeline list-video-models
```

---

### 6. Motion Transfer (Character Animation)

**ViMax Feature**: Transfer motion/poses to character images

**CLI Solution**: `transfer-motion` command

```bash
# Transfer dance motion from video to character image
ai-content-pipeline transfer-motion \
  -i character.jpg \
  -v dance_reference.mp4 \
  -o output/animated \
  -p "Character performing the same dance moves"

# With orientation control
ai-content-pipeline transfer-motion \
  -i character.jpg \
  -v motion.mp4 \
  --orientation video \
  -p "Natural motion transfer, maintain character appearance"

# List motion transfer models
ai-content-pipeline list-motion-models
```

---

### 7. Avatar/Talking Head Generation

**ViMax Feature**: Generate animated character videos

**CLI Solution**: `generate-avatar` command

```bash
# Lipsync with audio file
ai-content-pipeline generate-avatar \
  --image-url "https://example.com/character.jpg" \
  --audio-url "https://example.com/speech.mp3" \
  --model omnihuman_v1_5

# Text-to-speech avatar (generates speech + lipsync)
ai-content-pipeline generate-avatar \
  --image-url "https://example.com/character.jpg" \
  --text "Hello, I am your AI assistant. Let me explain the story." \
  --model fabric_1_0_text

# List all avatar models
ai-content-pipeline list-avatar-models
```

---

### 8. Complete Idea-to-Video Workflow

**ViMax Feature**: Full pipeline from idea to final video

**CLI Solution**: Multi-step pipeline with all features combined

```bash
# Step 1: Generate initial storyboard
ai-content-pipeline generate-grid \
  --prompt-file input/story_idea.md \
  --grid 3x3 \
  -o output/storyboard

# Step 2: Upscale storyboard images (optional)
ai-content-pipeline upscale-image \
  -i output/storyboard/grid.png \
  --factor 2

# Step 3: Run video pipeline
ai-content-pipeline run-chain \
  --config input/pipelines/story_to_video.yaml

# Or use the quick create-video for simple cases
ai-content-pipeline create-video \
  --text "A samurai warrior's journey at sunrise"
```

---

## 📁 Example Pipeline Configurations

### Simple Text-to-Video

```yaml
# input/pipelines/simple_video.yaml
pipeline_name: simple_video
output_dir: output/simple

steps:
  - type: text_to_image
    model: flux_dev
    params:
      prompt: "{{input}}"
      aspect_ratio: "16:9"

  - type: image_to_video
    model: kling
    params:
      prompt: "Subtle animation, cinematic movement"
      duration: 5
```

### Multi-Scene Story

```yaml
# input/pipelines/multi_scene.yaml
pipeline_name: multi_scene_story
output_dir: output/story

steps:
  # Scene 1
  - type: text_to_image
    model: flux_dev
    params:
      prompt: "Scene 1: Hero standing at crossroads, dramatic sky"

  - type: image_to_video
    model: kling_2_1
    params:
      prompt: "Hero looking around, wind blowing, contemplative"
      duration: 5

  # Scene 2
  - type: text_to_image
    model: flux_dev
    params:
      prompt: "Scene 2: Hero walking down chosen path, determined"

  - type: image_to_video
    model: kling_2_1
    params:
      prompt: "Hero walking forward, steady pace, leaves falling"
      duration: 5

  # Combine
  - type: concat_videos
    model: ffmpeg
    params:
      output_filename: "hero_journey.mp4"
```

### Character-Consistent Video Series

```yaml
# input/pipelines/character_series.yaml
pipeline_name: character_video_series
output_dir: output/character

steps:
  # Generate character reference
  - type: text_to_image
    model: flux_dev
    params:
      prompt: "Character portrait: young warrior with red hair, detailed face"
      aspect_ratio: "1:1"

  # Generate scenes with reference
  - type: reference_to_video
    model: kling_ref_to_video
    params:
      reference_image: "{{step_1.output}}"
      prompt: "Character walking through forest, maintaining appearance"
      duration: 5
```

---

## 🔧 Available Models Reference

### Text-to-Image Models
| Model | Best For | Cost |
|-------|----------|------|
| `flux_dev` | Quality, artistic content | $0.003 |
| `flux_schnell` | Speed, prototyping | $0.001 |
| `imagen4` | Photorealism, text rendering | $0.004 |
| `nano_banana_pro` | Speed + quality balance | $0.002 |
| `gpt_image_1_5` | Natural language prompts | $0.003 |

### Image-to-Video Models
| Model | Best For | Cost |
|-------|----------|------|
| `veo3` | Google's latest, highest quality | ~$0.50 |
| `veo3_fast` | Faster Veo generation | ~$0.30 |
| `kling` | High quality, reliable | ~$0.15 |
| `kling_2_1` | Improved Kling | ~$0.15 |
| `hailuo` | MiniMax, good quality | ~$0.10 |
| `grok_imagine` | xAI with audio support | $0.05/s |

### Avatar Models
| Model | Best For | Cost |
|-------|----------|------|
| `omnihuman_v1_5` | High-quality talking heads | $0.16/s |
| `fabric_1_0` | Cost-effective lipsync | $0.08/s |
| `fabric_1_0_text` | TTS + lipsync combined | $0.08/s |
| `kling_ref_to_video` | Character consistency | $0.112/s |
| `kling_motion_control` | Motion transfer | $0.06/s |

---

## 1. ViMax Unique Feature Inventory

### 1. Character Consistency System
| Feature | Description | CLI Solution |
|---------|-------------|--------------|
| CharacterExtractor | Auto-extract character info | `analyze-video -t describe` |
| CharacterPortraitsGenerator | Multi-angle portraits | `generate-grid --grid 2x2` |
| ReferenceImageSelector | Select best references | `generate-avatar --reference-images` |

### 2. Camera System
| Feature | Description | CLI Solution |
|---------|-------------|--------------|
| Camera Interface | Camera tree structure | YAML pipeline with steps |
| CameraImageGenerator | Camera transition videos | `run-chain` with image_to_video |
| Scene Detection | Extract keyframes | `analyze-video -t timeline` |

### 3. Multi-Agent Collaboration Pipeline
| Feature | Description | CLI Solution |
|---------|-------------|--------------|
| Screenwriter | Idea → Script | Use LLM externally, feed to CLI |
| StoryboardArtist | Script → Storyboard | `generate-grid` |
| Pipeline Orchestration | YAML pipelines | `run-chain --config` |

### 4. Structured Data Interfaces
| Interface | CLI Equivalent |
|-----------|----------------|
| CharacterInScene | Prompt engineering |
| ShotDescription | YAML step params |
| Camera | Pipeline step configuration |
| ImageOutput | Output directory structure |
| VideoOutput | `concat_videos` step |

---

## 2. Files to Copy (If Custom Development Needed)

### 2.1 Core Agent Files

```
ViMax/agents/
├── character_extractor.py       → video-agent-skill/agents/
├── character_portraits_generator.py → video-agent-skill/agents/
├── reference_image_selector.py  → video-agent-skill/agents/
├── camera_image_generator.py    → video-agent-skill/agents/
├── screenwriter.py              → video-agent-skill/agents/
├── storyboard_artist.py         → video-agent-skill/agents/
└── __init__.py                  → Merge into existing __init__.py
```

### 2.2 Interface Definition Files

```
ViMax/interfaces/
├── character.py                 → video-agent-skill/interfaces/
├── shot_description.py          → video-agent-skill/interfaces/
├── camera.py                    → video-agent-skill/interfaces/
├── image_output.py              → video-agent-skill/interfaces/
└── video_output.py              → video-agent-skill/interfaces/
```

### 2.3 Utility Function Files

```
ViMax/utils/
└── image.py                     → video-agent-skill/utils/
```

### 2.4 Pipeline Files

```
ViMax/pipelines/
├── idea2video_pipeline.py       → video-agent-skill/pipelines/
└── script2video_pipeline.py     → video-agent-skill/pipelines/
```

### 2.5 Configuration Files

```
ViMax/configs/
├── idea2video.yaml              → video-agent-skill/configs/
└── script2video.yaml            → video-agent-skill/configs/
```

### 2.6 Prompt Templates

```
ViMax/prompts/
└── *.txt                        → video-agent-skill/prompts/
```

---

## 3. Directory Structure to Create

Create the following directories in video-agent-skill:

```bash
mkdir -p video-agent-skill/agents
mkdir -p video-agent-skill/interfaces
mkdir -p video-agent-skill/pipelines
mkdir -p video-agent-skill/configs
mkdir -p video-agent-skill/prompts
```

---

## 4. Dependencies to Add

Add to `video-agent-skill/requirements.txt` or `pyproject.toml`:

```
pydantic>=2.0
scenedetect[opencv]>=0.6
opencv-python>=4.8
pillow>=10.0
google-genai>=1.0
litellm>=1.0
pyyaml>=6.0
```

---

## 5. Functions/Code to Modify

### 5.1 Adapt image_generator

ViMax uses Google Imagen, video-agent-skill has multiple image generators. Need to create an adapter layer:

```python
# video-agent-skill/adapters/image_generator_adapter.py

class ImageGeneratorAdapter:
    """Adapt ViMax agents to video-agent-skill's image generators"""

    def __init__(self, generator_type="flux"):
        self.generator = self._init_generator(generator_type)

    async def generate(self, prompt: str, **kwargs) -> str:
        """Return generated image as base64 or path"""
        # Call video-agent-skill's image generation
        pass
```

### 5.2 Adapt video_generator

```python
# video-agent-skill/adapters/video_generator_adapter.py

class VideoGeneratorAdapter:
    """Adapt ViMax agents to video-agent-skill's video generators"""

    def __init__(self, generator_type="kling"):
        self.generator = self._init_generator(generator_type)

    async def generate(self, image: str, prompt: str, **kwargs) -> str:
        """Return generated video path"""
        pass
```

### 5.3 Adapt LLM Calls

ViMax uses `litellm`, need to ensure compatibility with video-agent-skill's LLM calls:

```python
# video-agent-skill/adapters/llm_adapter.py

from litellm import completion

class LLMAdapter:
    """Unified LLM call interface"""

    def __init__(self, model="openrouter/anthropic/claude-3.5-sonnet"):
        self.model = model

    async def chat(self, messages: list, **kwargs):
        response = await completion(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response
```

---

## 6. Integration Steps

### Phase 1: CLI-First Approach (Recommended - Immediate)

1. **Use existing CLI commands** for most ViMax features
2. **Create YAML pipeline configs** for complex workflows
3. **Use prompt engineering** to achieve character consistency

### Phase 2: Infrastructure (1-2 days)

1. **Create directory structure**
   ```bash
   cd video-agent-skill
   mkdir -p agents interfaces pipelines configs prompts adapters
   ```

2. **Copy interface files**
   ```bash
   cp ../interfaces/*.py interfaces/
   ```

3. **Copy utility functions**
   ```bash
   cp ../utils/image.py utils/
   ```

4. **Install dependencies**
   ```bash
   pip install pydantic scenedetect opencv-python pillow google-genai litellm pyyaml
   ```

### Phase 3: Adapter Layer (2-3 days)

1. **Create ImageGeneratorAdapter**
   - Map ViMax's `image_generator` to video-agent-skill's Flux/SDXL

2. **Create VideoGeneratorAdapter**
   - Map ViMax's `video_generator` to video-agent-skill's Kling/Runway

3. **Create LLMAdapter**
   - Unify LLM call interface

### Phase 4: Agent Migration (3-5 days)

1. **Migrate CharacterExtractor**
   - Modify LLM calls to use adapter layer
   - Test character extraction functionality

2. **Migrate CharacterPortraitsGenerator**
   - Modify image generation calls to use adapter layer
   - Test multi-angle portrait generation

3. **Migrate ReferenceImageSelector**
   - Ensure multimodal LLM calls work properly
   - Test reference image selection

4. **Migrate CameraImageGenerator**
   - Ensure scenedetect works properly
   - Test camera video generation

5. **Migrate Screenwriter and StoryboardArtist**
   - Modify prompt paths
   - Test script and storyboard generation

### Phase 5: Pipeline Integration (2-3 days)

1. **Migrate Pipeline Classes**
   - Adapt configuration loading
   - Adapt Agent calls

2. **Create Unified Entry Point**
   ```python
   # video-agent-skill/run_vimax.py
   from pipelines import Idea2VideoPipeline, Script2VideoPipeline
   ```

3. **Test End-to-End Flow**

---

## 7. File Modification Details

### 7.1 character_extractor.py Modifications

```python
# Original (ViMax)
from litellm import completion

# Change to
from adapters.llm_adapter import LLMAdapter

# Original
response = completion(model=self.model, messages=messages)

# Change to
llm = LLMAdapter(model=self.model)
response = await llm.chat(messages)
```

### 7.2 character_portraits_generator.py Modifications

```python
# Original (ViMax)
image_result = self.image_generator.generate(prompt)

# Change to
from adapters.image_generator_adapter import ImageGeneratorAdapter
image_gen = ImageGeneratorAdapter(generator_type="flux")
image_result = await image_gen.generate(prompt)
```

### 7.3 camera_image_generator.py Modifications

```python
# Original (ViMax)
video_result = self.video_generator.generate(image, prompt)

# Change to
from adapters.video_generator_adapter import VideoGeneratorAdapter
video_gen = VideoGeneratorAdapter(generator_type="kling")
video_result = await video_gen.generate(image, prompt)
```

---

## 8. Test Plan

### Unit Tests

```python
# tests/test_character_extractor.py
def test_extract_characters():
    extractor = CharacterExtractor(model="gpt-4")
    script = "Xiaoming and Xiaohong are walking in the park..."
    characters = extractor.extract(script)
    assert len(characters) >= 2

# tests/test_portrait_generator.py
def test_generate_portraits():
    generator = CharacterPortraitsGenerator()
    character = CharacterInScene(name="Xiaoming", description="20-year-old male")
    portraits = generator.generate(character)
    assert "front" in portraits
    assert "side" in portraits
    assert "back" in portraits
```

### Integration Tests

```python
# tests/test_pipeline.py
def test_idea2video_pipeline():
    pipeline = Idea2VideoPipeline(config_path="configs/idea2video.yaml")
    result = pipeline.run(idea="A short film about friendship")
    assert result.video_path.exists()
```

### CLI Tests

```bash
# Test storyboard generation
ai-content-pipeline generate-grid --prompt-file test_storyboard.md --grid 2x2

# Test video pipeline
ai-content-pipeline run-chain --config test_pipeline.yaml

# Test avatar generation
ai-content-pipeline generate-avatar --image-url "..." --text "Test speech"
```

---

## 9. Estimated Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| CLI-First (No Code) | Immediate | Use existing CLI commands |
| Infrastructure | 1-2 days | Create directories, copy files, install dependencies |
| Adapter Layer | 2-3 days | Create three adapters |
| Agent Migration | 3-5 days | Migrate 6 Agents |
| Pipeline Integration | 2-3 days | Migrate Pipelines, create entry point |
| Testing & Debugging | 2-3 days | Unit tests, integration tests |
| **Total** | **10-16 days** | |

---

## 10. Risks and Considerations

### 10.1 API Compatibility
- ViMax uses Google Imagen/Veo, video-agent-skill uses other models
- Need to ensure prompt format compatibility

### 10.2 Async/Sync
- ViMax has some synchronous code
- video-agent-skill may require async
- Need unified handling

### 10.3 Dependency Conflicts
- Check pydantic version compatibility
- Check opencv and scenedetect versions

### 10.4 File Paths
- ViMax uses relative paths
- Need to adapt to video-agent-skill's path structure

---

## 11. Quick Start Commands

### CLI-Only Approach (Recommended)

```bash
# 1. Install and verify
pip install -e .
ai-content-pipeline --help

# 2. Generate character portraits
ai-content-pipeline generate-grid \
  --prompt-file input/character.md \
  --grid 2x2

# 3. Create storyboard
ai-content-pipeline generate-grid \
  --prompt-file input/storyboard.md \
  --grid 3x3

# 4. Run video pipeline
ai-content-pipeline run-chain \
  --config input/pipelines/shot_workflow.yaml

# 5. Analyze results
ai-content-pipeline analyze-video \
  -i output/final_video.mp4 \
  -t timeline
```

### Full Code Integration

```bash
# 1. Enter video-agent-skill directory
cd C:\Users\yanie\Desktop\ViMax\video-agent-skill

# 2. Create directories
mkdir agents interfaces pipelines configs prompts adapters

# 3. Copy files
copy ..\interfaces\*.py interfaces\
copy ..\utils\image.py utils\
copy ..\agents\*.py agents\
copy ..\pipelines\*.py pipelines\
copy ..\configs\*.yaml configs\
xcopy ..\prompts\* prompts\ /E

# 4. Install dependencies
pip install pydantic scenedetect opencv-python pillow google-genai litellm pyyaml

# 5. Create adapter layer (manual coding)
# adapters/image_generator_adapter.py
# adapters/video_generator_adapter.py
# adapters/llm_adapter.py
```

---

## Appendix: File Copy Checklist

### Must Copy
- [x] `interfaces/character.py`
- [x] `interfaces/shot_description.py`
- [x] `interfaces/camera.py`
- [x] `interfaces/image_output.py`
- [x] `interfaces/video_output.py`
- [x] `utils/image.py`
- [x] `agents/character_extractor.py`
- [x] `agents/character_portraits_generator.py`
- [x] `agents/reference_image_selector.py`
- [x] `agents/camera_image_generator.py`

### Optional Copy
- [ ] `agents/screenwriter.py` (if full pipeline needed)
- [ ] `agents/storyboard_artist.py` (if full pipeline needed)
- [ ] `pipelines/*.py` (if pipeline orchestration needed)
- [ ] `configs/*.yaml` (if configuration management needed)
- [ ] `prompts/*.txt` (if prompt templates needed)

---

*Document Version: 2.0*
*Created: 2026-02-03*
*Updated: 2026-02-03 - Added CLI-first approach*
*Author: AI Assistant*
