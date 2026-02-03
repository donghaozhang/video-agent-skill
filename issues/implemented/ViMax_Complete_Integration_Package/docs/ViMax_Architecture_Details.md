# ViMax Architecture Details

> This document provides a detailed introduction to ViMax's code architecture, module functions, and call flows.

---

## 📁 Project Structure

```
ViMax/
├── main_idea2video.py      # Entry: Idea → Video
├── main_script2video.py    # Entry: Script → Video
├── configs/                # Configuration files
│   ├── idea2video.yaml
│   └── script2video.yaml
├── pipelines/              # Main workflow pipelines
│   ├── idea2video_pipeline.py
│   └── script2video_pipeline.py
├── agents/                 # AI Agents (Core Logic)
│   ├── screenwriter.py           # Screenwriter
│   ├── character_extractor.py    # Character Extractor
│   ├── character_portraits_generator.py  # Character Portraits Generator
│   ├── storyboard_artist.py      # Storyboard Artist
│   ├── camera_image_generator.py # Camera Image Generator
│   └── reference_image_selector.py # Reference Image Selector
├── tools/                  # External tool wrappers
│   ├── image_generator_*.py      # Image generators
│   └── video_generator_*.py      # Video generators
├── interfaces/             # Data structure definitions
│   ├── character.py
│   ├── scene.py
│   ├── shot_description.py
│   └── camera.py
└── utils/                  # Utility functions
    ├── rate_limiter.py
    ├── retry.py
    └── video.py
```

---

## 🏗️ Overall Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Input Layer                                │
│  ┌─────────────────────┐              ┌─────────────────────┐               │
│  │   main_idea2video   │              │  main_script2video  │               │
│  │ (Idea + Requirements│              │ (Script + Requirements              │
│  │     + Style)        │              │      + Style)       │               │
│  └──────────┬──────────┘              └──────────┬──────────┘               │
└─────────────┼───────────────────────────────────┼───────────────────────────┘
              │                                   │
              ▼                                   │
┌─────────────────────────────────────────────────┼───────────────────────────┐
│                         Pipeline Layer                                       │
│  ┌─────────────────────────────────────────┐    │                           │
│  │       Idea2VideoPipeline                │    │                           │
│  │  ┌─────────────────────────────────┐    │    │                           │
│  │  │ 1. develop_story()              │    │    │                           │
│  │  │    Calls Screenwriter           │    │    │                           │
│  │  └─────────────┬───────────────────┘    │    │                           │
│  │                ▼                        │    │                           │
│  │  ┌─────────────────────────────────┐    │    │                           │
│  │  │ 2. extract_characters()         │    │    │                           │
│  │  │    Calls CharacterExtractor     │    │    │                           │
│  │  └─────────────┬───────────────────┘    │    │                           │
│  │                ▼                        │    │                           │
│  │  ┌─────────────────────────────────┐    │    │                           │
│  │  │ 3. generate_character_portraits │    │    │                           │
│  │  │    Calls CharacterPortraitsGen  │    │    │                           │
│  │  └─────────────┬───────────────────┘    │    │                           │
│  │                ▼                        │    │                           │
│  │  ┌─────────────────────────────────┐    │    │                           │
│  │  │ 4. write_script_based_on_story  │    │    │                           │
│  │  │    Calls Screenwriter           │    │    │                           │
│  │  └─────────────┬───────────────────┘    │    │                           │
│  │                ▼                        │    │                           │
│  │  ┌─────────────────────────────────┐    │    │                           │
│  │  │ 5. Loop through each scene      │◄───┼────┘                           │
│  │  │    Calls Script2VideoPipeline   │    │                                │
│  │  └─────────────────────────────────┘    │                                │
│  └─────────────────────────────────────────┘                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Script2VideoPipeline                              │    │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐    │    │
│  │  │ 1.Extract     │→ │ 2.Generate    │→ │ 3.Design Storyboard   │    │    │
│  │  │   Characters  │  │   Portraits   │  │                       │    │    │
│  │  └───────────────┘  └───────────────┘  └───────────┬───────────┘    │    │
│  │                                                    ▼                 │    │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐    │    │
│  │  │ 6.Merge Videos│← │ 5.Generate    │← │ 4.Decompose Visual    │    │    │
│  │  │               │  │   Shot Videos │  │   Descriptions        │    │    │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Agents Layer                                      │
│  ┌────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐     │
│  │    Screenwriter    │  │  CharacterExtractor │  │  StoryboardArtist │     │
│  │                    │  │                     │  │                   │     │
│  │  • develop_story() │  │  • extract_chars()  │  │  • design_story   │     │
│  │  • write_script()  │  │                     │  │    board()        │     │
│  └────────────────────┘  └─────────────────────┘  │  • decompose_     │     │
│                                                   │    visual_desc()  │     │
│  ┌────────────────────┐  ┌─────────────────────┐  └───────────────────┘     │
│  │ CharacterPortraits │  │ ReferenceImage      │  ┌───────────────────┐     │
│  │ Generator          │  │ Selector            │  │ CameraImage       │     │
│  │                    │  │                     │  │ Generator         │     │
│  │  • gen_front()     │  │  • select_refs()    │  │                   │     │
│  │  • gen_side()      │  │                     │  │  • construct_     │     │
│  │  • gen_back()      │  │                     │  │    camera_tree()  │     │
│  └────────────────────┘  └─────────────────────┘  └───────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Tools Layer                                       │
│  ┌───────────────────────────────┐  ┌───────────────────────────────┐       │
│  │       Image Generator         │  │       Video Generator         │       │
│  │  • Google Imagen API          │  │  • Google Veo API             │       │
│  │  • Doubao Seedream            │  │  • Doubao Seedance            │       │
│  │                               │  │                               │       │
│  │  generate_single_image()      │  │  generate_single_video()      │       │
│  └───────────────────────────────┘  └───────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           External API Services                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  OpenRouter │  │ Google AI   │  │ Google Veo  │  │   Others... │         │
│  │  (Chat LLM) │  │ (Imagen)    │  │ (Video)     │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Idea2Video Complete Flow

```
Input: idea + user_requirement + style
                    │
                    ▼
    ┌───────────────────────────────┐
    │  Step 1: develop_story()      │
    │  ────────────────────────     │
    │  Screenwriter generates       │
    │  complete story from idea     │
    │  Output: story.txt            │
    └───────────────┬───────────────┘
                    ▼
    ┌───────────────────────────────┐
    │  Step 2: extract_characters() │
    │  ────────────────────────     │
    │  CharacterExtractor extracts  │
    │  all characters and traits    │
    │  from the story               │
    │  Output: characters.json      │
    └───────────────┬───────────────┘
                    ▼
    ┌───────────────────────────────┐
    │  Step 3: generate_portraits() │
    │  ────────────────────────     │
    │  Generate 3 reference images  │
    │  for each character:          │
    │  • Front view (front.png)     │
    │  • Side view (side.png)       │
    │  • Back view (back.png)       │
    │  Output: character_portraits/ │
    └───────────────┬───────────────┘
                    ▼
    ┌───────────────────────────────┐
    │  Step 4: write_script()       │
    │  ────────────────────────     │
    │  Screenwriter adapts story    │
    │  into scene-based script      │
    │  Output: script.json          │
    └───────────────┬───────────────┘
                    ▼
    ┌───────────────────────────────┐
    │  Step 5: Loop through scenes  │
    │  ────────────────────────     │
    │  For each scene, call         │
    │  Script2VideoPipeline to      │
    │  generate video segment       │
    └───────────────┬───────────────┘
                    ▼
    ┌───────────────────────────────┐
    │  Step 6: Merge all videos     │
    │  ────────────────────────     │
    │  Use moviepy to concatenate   │
    │  all scene videos into        │
    │  final video                  │
    │  Output: final_video.mp4      │
    └───────────────────────────────┘
```

---

## 🔄 Script2Video Complete Flow

```
Input: script + user_requirement + style
                    │
                    ▼
    ┌────────────────────────────────────┐
    │  Step 1: extract_characters()      │
    │  Extract character info from script│
    └───────────────┬────────────────────┘
                    ▼
    ┌────────────────────────────────────┐
    │  Step 2: generate_character_       │
    │          portraits()               │
    │  Generate front/side/back          │
    │  portraits for each character      │
    └───────────────┬────────────────────┘
                    ▼
    ┌────────────────────────────────────┐
    │  Step 3: design_storyboard()       │
    │  ─────────────────────────────     │
    │  StoryboardArtist designs shots:   │
    │  • Shot number (shot_idx)          │
    │  • Camera number (cam_idx)         │
    │  • Visual description (visual_desc)│
    │  • Audio description (audio_desc)  │
    │  Output: storyboard.json           │
    └───────────────┬────────────────────┘
                    ▼
    ┌────────────────────────────────────┐
    │  Step 4: decompose_visual_         │
    │          descriptions()            │
    │  ─────────────────────────────     │
    │  Decompose each shot's visual      │
    │  description into:                 │
    │  • First frame desc (ff_desc)      │
    │  • Last frame desc (lf_desc)       │
    │  • Motion desc (motion_desc)       │
    │  • Change type (small/medium/large)│
    │  Output: shots/N/shot_description  │
    └───────────────┬────────────────────┘
                    ▼
    ┌────────────────────────────────────┐
    │  Step 5: construct_camera_tree()   │
    │  ─────────────────────────────     │
    │  Build camera dependency tree:     │
    │  Determine which shots share the   │
    │  same camera position, which       │
    │  shots need transitions            │
    │  Output: camera_tree.json          │
    └───────────────┬────────────────────┘
                    ▼
    ┌────────────────────────────────────┐
    │  Step 6: generate_frames()         │
    │  ─────────────────────────────     │
    │  Generate keyframes for each shot  │
    │  in parallel:                      │
    │  • First frame (first_frame.png)   │
    │  • Last frame (last_frame.png)     │
    │    [if needed]                     │
    │                                    │
    │  Flow:                             │
    │  1. ReferenceImageSelector selects │
    │     best reference image           │
    │  2. ImageGenerator creates image   │
    │  Output: shots/N/first_frame.png   │
    └───────────────┬────────────────────┘
                    ▼
    ┌────────────────────────────────────┐
    │  Step 7: generate_videos()         │
    │  ─────────────────────────────     │
    │  Generate video segments for each  │
    │  shot in parallel:                 │
    │  • Input: first frame + last frame │
    │    (optional) + description        │
    │  • VideoGenerator creates video    │
    │  Output: shots/N/video.mp4         │
    └───────────────┬────────────────────┘
                    ▼
    ┌────────────────────────────────────┐
    │  Step 8: concatenate_videos()      │
    │  ─────────────────────────────     │
    │  Merge all video segments in       │
    │  shot order                        │
    │  Output: final_video.mp4           │
    └────────────────────────────────────┘
```

---

## 🤖 Agents Detailed Description

### 1. Screenwriter

**File**: `agents/screenwriter.py`

**Function**:
- Expand simple ideas into complete stories
- Adapt stories into scene-based scripts

**Methods**:

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `develop_story()` | idea, user_requirement | str (story text) | Generate complete story from idea |
| `write_script_based_on_story()` | story, user_requirement | List[str] (scene script list) | Adapt story into script |

---

### 2. CharacterExtractor

**File**: `agents/character_extractor.py`

**Function**: Identify and extract character information from scripts/stories

**Methods**:

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `extract_characters()` | script/story | List[CharacterInScene] | Extract character names, traits, descriptions |

**Output Data Structure** `CharacterInScene`:
```python
{
    "idx": 0,                           # Character index
    "identifier_in_scene": "Alice",     # Character name
    "static_features": "short hair, green dress",  # Static features (appearance/clothing)
    "dynamic_features": "lively, loves to smile"   # Dynamic features (personality/habits)
}
```

---

### 3. CharacterPortraitsGenerator

**File**: `agents/character_portraits_generator.py`

**Function**: Generate consistent reference images for each character

**Methods**:

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `generate_front_portrait()` | character, style | ImageOutput | Generate front portrait |
| `generate_side_portrait()` | character, front_path | ImageOutput | Generate side view based on front |
| `generate_back_portrait()` | character, front_path | ImageOutput | Generate back view based on front |

---

### 4. StoryboardArtist

**File**: `agents/storyboard_artist.py`

**Function**:
- Convert scripts into professional storyboards
- Decompose visual descriptions into executable frame descriptions

**Methods**:

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `design_storyboard()` | script, characters, requirement | List[ShotBriefDescription] | Design complete storyboard |
| `decompose_visual_description()` | shot_brief_desc, characters | ShotDescription | Decompose into first/last frame and motion descriptions |

**Output Data Structure** `ShotDescription`:
```python
{
    "idx": 0,                    # Shot index
    "cam_idx": 0,                # Camera index (same camera can shoot multiple shots)
    "visual_desc": "...",        # Complete visual description
    "ff_desc": "...",            # First frame description
    "ff_vis_char_idxs": [0, 1],  # Character indices visible in first frame
    "lf_desc": "...",            # Last frame description
    "lf_vis_char_idxs": [0],     # Character indices visible in last frame
    "motion_desc": "...",        # Motion description (camera movement + character actions)
    "audio_desc": "...",         # Audio description (dialogue/sound effects)
    "variation_type": "small"    # Change magnitude: small/medium/large
}
```

---

### 5. CameraImageGenerator

**File**: `agents/camera_image_generator.py`

**Function**:
- Build camera dependency tree
- Generate camera transition videos

**Methods**:

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `construct_camera_tree()` | cameras, shot_descs | List[Camera] | Build camera dependency relationships |
| `generate_transition_video()` | shot1_desc, shot2_desc, shot1_ff | VideoOutput | Generate transition video |

---

### 6. ReferenceImageSelector

**File**: `agents/reference_image_selector.py`

**Function**: Intelligently select the most suitable reference images for generating new frames

**Methods**:

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `select_reference_images_and_generate_prompt()` | available_pairs, frame_desc | dict | Select reference images + generate prompts |

---

## 🔧 Tools Description

### Image Generator

| Class Name | API | Description |
|------------|-----|-------------|
| `ImageGeneratorNanobananaGoogleAPI` | Google AI Studio | Generate images using Imagen |
| `ImageGeneratorDoubaoSeedreamYunwuAPI` | ByteDance Yunwu | Generate images using Doubao |

**Common Method**:
```python
async def generate_single_image(
    prompt: str,                    # Generation prompt
    reference_image_paths: List[str],  # Reference image paths
    size: str = "1600x900"          # Output size
) -> ImageOutput
```

### Video Generator

| Class Name | API | Description |
|------------|-----|-------------|
| `VideoGeneratorVeoGoogleAPI` | Google Veo | Generate videos using Veo |
| `VideoGeneratorDoubaoSeedanceYunwuAPI` | ByteDance Yunwu | Generate videos using Doubao |

**Common Method**:
```python
async def generate_single_video(
    prompt: str,                    # Generation prompt (action + audio description)
    reference_image_paths: List[str]   # Reference frame paths (first/last frame)
) -> VideoOutput
```

---

## 📂 Output Directory Structure

```
.working_dir/
├── idea2video/                    # Idea2Video output
│   ├── story.txt                  # Generated story
│   ├── characters.json            # Extracted characters
│   ├── character_portraits/       # Character portraits
│   │   ├── 0_Alice/
│   │   │   ├── front.png
│   │   │   ├── side.png
│   │   │   └── back.png
│   │   └── 1_Bob/
│   │       └── ...
│   ├── character_portraits_registry.json
│   ├── script.json                # Scene-based script
│   ├── scene_0/                   # First scene
│   │   ├── storyboard.json        # Storyboard
│   │   ├── camera_tree.json       # Camera tree
│   │   ├── shots/
│   │   │   ├── 0/
│   │   │   │   ├── shot_description.json
│   │   │   │   ├── first_frame.png
│   │   │   │   ├── last_frame.png (if needed)
│   │   │   │   └── video.mp4
│   │   │   ├── 1/
│   │   │   └── ...
│   │   └── final_video.mp4        # Scene video
│   ├── scene_1/
│   └── final_video.mp4            # Final complete video
│
└── script2video/                  # Script2Video output
    └── (same structure as above)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd C:\Users\yanie\Desktop\ViMax
uv sync
```

### 2. Configure API Keys

Edit `configs/idea2video.yaml`:

```yaml
chat_model:
  init_args:
    model: google/gemini-2.5-flash-lite-preview-09-2025
    api_key: <Your OpenRouter API Key>
    base_url: https://openrouter.ai/api/v1

image_generator:
  class_path: tools.ImageGeneratorNanobananaGoogleAPI
  init_args:
    api_key: <Your Google AI Studio API Key>

video_generator:
  class_path: tools.VideoGeneratorVeoGoogleAPI
  init_args:
    api_key: <Your Google AI Studio API Key>
```

### 3. Run

```bash
# Idea to Video
uv run python main_idea2video.py

# Script to Video
uv run python main_script2video.py
```

---

## 📝 Key Concepts

### Camera vs Shot

- **Camera (cam_idx)**: A fixed shooting position/angle
- **Shot (shot_idx)**: A continuous video segment

One camera can shoot multiple shots (without moving the camera).

### Variation Type

| Type | Description | Needs Last Frame? |
|------|-------------|-------------------|
| `small` | Minor changes (expressions, small movements) | ❌ |
| `medium` | Medium changes (new character appears, turning) | ✅ |
| `large` | Large changes (major camera movement, scene switch) | ✅ |

### Asynchronous Parallel Processing

ViMax uses `asyncio` for parallel processing:
- Multiple character portraits can be generated in parallel
- Multiple shot first frames can be generated in parallel
- Video generation starts after corresponding frames are completed

---

*Last Updated: 2026-02-03*
