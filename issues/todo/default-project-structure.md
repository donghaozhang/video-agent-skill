# Default Project Structure Implementation

**Status**: TODO
**Priority**: Medium
**Created**: 2026-02-01

## Overview

Implement the AI Content Pipeline's standard project structure as the default option for new projects.

## Target Structure

```
{project-root}/
├── input/                        # All input assets and configurations
│   ├── images/                   # Input images for processing
│   ├── videos/                   # Input videos for processing
│   ├── audio/                    # Input audio files
│   ├── pipelines/                # YAML pipeline configurations
│   │   ├── video/                # Video generation pipelines
│   │   ├── image/                # Image generation pipelines
│   │   ├── storyboard/           # Multi-scene storyboard pipelines
│   │   ├── analysis/             # Video analysis pipelines
│   │   └── examples/             # Example/demo pipelines
│   ├── prompts/                  # Text prompts and templates
│   ├── subtitles/                # Subtitle files (.srt, .vtt)
│   ├── text/                     # Text content files
│   └── metadata/                 # Project metadata
├── output/                       # All generated content
│   ├── {pipeline_name}/          # Per-pipeline output folders
│   │   ├── generated_image_*.png # Generated images
│   │   ├── generated_video_*.mp4 # Generated videos
│   │   └── step_*_output.*       # Intermediate step outputs
│   └── generated_*.*             # Direct generation outputs
├── .claude/                      # Claude Code configuration
│   └── skills/                   # Project-specific skills
├── issues/                       # Project planning and tracking
│   ├── todo/                     # Planned features
│   └── implemented/              # Completed features
└── docs/                         # Project documentation
```

## Implementation Tasks

### 1. Input Organization
- [ ] Images (.jpg, .png, .webp, .gif) → `input/images/`
- [ ] Videos (.mp4, .mov, .webm) → `input/videos/`
- [ ] Audio (.mp3, .wav, .aac) → `input/audio/`
- [ ] Pipeline configs (.yaml) → `input/pipelines/{category}/`
- [ ] Prompts (.txt, .md) → `input/prompts/`
- [ ] Subtitles (.srt, .vtt) → `input/subtitles/`

### 2. Output Organization
- [ ] Pipeline outputs → `output/{pipeline_name}/`
- [ ] Direct generations → `output/generated_*.*`
- [ ] Naming pattern: `generated_{type}_{timestamp}.{ext}`

### 3. Pipeline Categories
- [ ] `input/pipelines/video/` - Text/image to video workflows
- [ ] `input/pipelines/image/` - Image generation/editing
- [ ] `input/pipelines/storyboard/` - Multi-scene stories
- [ ] `input/pipelines/analysis/` - Video analysis tasks
- [ ] `input/pipelines/examples/` - Demo configurations

### 4. Skills Organization
- [ ] Skills folder: `.claude/skills/`
- [ ] Each skill: `{skill-name}/Skill.md` entry point
- [ ] Optional: `REFERENCE.md`, `EXAMPLES.md`

## Quick Setup Commands

```bash
# Create default structure
mkdir -p input/{images,videos,audio,pipelines,prompts,subtitles,text,metadata}
mkdir -p input/pipelines/{video,image,storyboard,analysis,examples}
mkdir -p output
mkdir -p issues/{todo,implemented}
mkdir -p docs

# Move input files
mv *.jpg *.png *.gif *.webp input/images/ 2>/dev/null
mv *.mp4 *.mov *.webm input/videos/ 2>/dev/null
mv *.mp3 *.wav *.aac input/audio/ 2>/dev/null
mv *.yaml *.yml input/pipelines/ 2>/dev/null

# Cleanup outputs
rm -rf output/*/step_*  # Remove intermediate files
```

## Pipeline Configuration

Each pipeline YAML specifies its output directory:
```yaml
pipeline_name: my_workflow
output_dir: output/my_workflow

steps:
  - type: text_to_image
    model: flux_dev
    params:
      prompt: "..."
```

## Acceptance Criteria

- [ ] New projects use `input/` and `output/` structure
- [ ] Pipeline outputs organized by `output_dir` in YAML
- [ ] Input assets categorized by type
- [ ] Pipeline configs grouped by category
- [ ] Generated files follow naming convention
- [ ] Organize command restructures existing projects
