# ViMax → video-agent-skill Integration Plan

## Overview

This document details how to integrate ViMax's unique features into the video-agent-skill project, including files to copy, functions to add/modify, and integration steps.

---

## 1. ViMax Unique Feature Inventory

### 1. Character Consistency System
| Feature | Description | video-agent-skill Status |
|---------|-------------|-------------------------|
| CharacterExtractor | Automatically extract character info from scripts | ❌ None |
| CharacterPortraitsGenerator | Generate multi-angle character portraits (front/side/back) | ❌ None |
| ReferenceImageSelector | Intelligently select best reference images | ❌ None |

### 2. Camera System
| Feature | Description | video-agent-skill Status |
|---------|-------------|-------------------------|
| Camera Interface | Hierarchical camera tree structure | ❌ None |
| CameraImageGenerator | Generate camera transition videos | ❌ None |
| Scene Detection Frame Extraction | Extract keyframes using scenedetect | ❌ None |

### 3. Multi-Agent Collaboration Pipeline
| Feature | Description | video-agent-skill Status |
|---------|-------------|-------------------------|
| Screenwriter | Idea → Script generation | ⚠️ Has basic text generation |
| StoryboardArtist | Script → Storyboard | ❌ None |
| Pipeline Orchestration | YAML-configured Agent pipelines | ❌ None |

### 4. Structured Data Interfaces
| Interface | Purpose |
|-----------|---------|
| CharacterInScene | Character information in scene |
| CharacterInEvent | Character information in event |
| CharacterInNovel | Character information in novel |
| ShotDescription | Complete shot description |
| ShotBriefDescription | Simplified shot description |
| Camera | Camera configuration and hierarchy |
| ImageOutput | Image output wrapper |
| VideoOutput | Video output wrapper |

---

## 2. Files to Copy

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

### Phase 1: Infrastructure (1-2 days)

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

### Phase 2: Adapter Layer (2-3 days)

1. **Create ImageGeneratorAdapter**
   - Map ViMax's `image_generator` to video-agent-skill's Flux/SDXL

2. **Create VideoGeneratorAdapter**
   - Map ViMax's `video_generator` to video-agent-skill's Kling/Runway

3. **Create LLMAdapter**
   - Unify LLM call interface

### Phase 3: Agent Migration (3-5 days)

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

### Phase 4: Pipeline Integration (2-3 days)

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

---

## 9. Estimated Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
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

*Document Version: 1.0*
*Created: 2026-02-03*
*Author: AI Assistant*
