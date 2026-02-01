# Output Folder Structure Implementation

**Status**: TODO
**Priority**: Medium
**Created**: 2026-02-01
**Estimated Time**: 25-30 minutes

## Overview

Extend the project structure implementation to organize the `output/` folder with a consistent, categorized structure matching the `input/` pattern. Currently, output files are scattered at the root or in arbitrary pipeline folders.

## Current State

```
output/
├── generated_image_*.png          # Root-level generated images (messy)
├── *.srt, *.json, *.txt          # Root-level transcripts (messy)
├── {pipeline_name}/               # Pipeline-specific folders
├── temp/                          # Temporary files
├── media/                         # Unclear purpose
├── processing/                    # Unclear purpose
└── reports_docs/                  # Documentation outputs
```

## Target Structure

```
output/
├── images/                        # Generated images
│   └── generated_image_*.png
├── videos/                        # Generated videos
│   └── generated_video_*.mp4
├── audio/                         # Generated audio/TTS
│   └── generated_audio_*.mp3
├── transcripts/                   # Transcription outputs
│   ├── *.txt                      # Plain text transcripts
│   ├── *.srt                      # Subtitle files
│   └── *.json                     # Word-level timestamps
├── analysis/                      # Video analysis results
│   ├── *.md                       # Markdown reports
│   └── *.json                     # JSON analysis data
├── pipelines/                     # Pipeline execution outputs
│   └── {pipeline_name}/           # Per-pipeline folders
│       ├── step_*_output.*        # Step outputs
│       └── final_output.*         # Final result
└── temp/                          # Temporary processing files
```

## Implementation Tasks

### Task 1: Update Output Structure Constants
**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/project_structure.py`
**Time**: 5 minutes

- [ ] Add `OUTPUT_STRUCTURE` constant defining output subfolders
- [ ] Add `OUTPUT_FILE_EXTENSIONS` mapping for output organization
- [ ] Update `DEFAULT_STRUCTURE` to include output subfolders

### Task 2: Add Output Organization Functions
**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/project_structure.py`
**Time**: 10 minutes

- [ ] Add `get_output_destination()` - determine output subfolder by file type
- [ ] Add `organize_output()` - move output files to correct subfolders
- [ ] Add `init_output_structure()` - create output subfolders

### Task 3: Update CLI Commands
**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`
**Time**: 5 minutes

- [ ] Add `--include-output` flag to `organize-project` command
- [ ] Update `structure-info` to show output folder details

### Task 4: Update Pipeline Output Paths
**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/manager.py`
**Time**: 5 minutes

- [ ] Update `AIPipelineManager` to use structured output paths
- [ ] Route generated images to `output/images/`
- [ ] Route generated videos to `output/videos/`

### Task 5: Write Tests
**File**: `tests/test_project_structure.py`
**Time**: 5 minutes

- [ ] Add `TestOutputOrganization` class
- [ ] Test `get_output_destination()` for all file types
- [ ] Test `organize_output()` moves files correctly
- [ ] Test dry-run mode

## Output File Mappings

| File Pattern | Destination |
|-------------|-------------|
| generated_image_*.png/jpg | output/images/ |
| generated_video_*.mp4/webm | output/videos/ |
| generated_audio_*.mp3/wav | output/audio/ |
| *_transcript*.txt | output/transcripts/ |
| *.srt, *.vtt | output/transcripts/ |
| *_words.json, *_raw.json | output/transcripts/ |
| *_analysis*.md/json | output/analysis/ |
| step_*_output.* | output/pipelines/{name}/ |

## CLI Usage (After Implementation)

```bash
# Organize output folder
ai-content-pipeline organize-project --include-output

# Preview output organization
ai-content-pipeline organize-project --include-output --dry-run

# Initialize with output structure
ai-content-pipeline init-project  # Already includes output subfolders
```

## Backward Compatibility

- Existing pipelines continue to work (output_dir in YAML still supported)
- New direct generations use structured paths
- `organize-project --include-output` migrates existing files

## Acceptance Criteria

- [ ] Output folder has categorized subfolders (images, videos, audio, transcripts, analysis, pipelines)
- [ ] New generations save to correct subfolders
- [ ] `organize-project --include-output` moves existing files
- [ ] `structure-info` shows output folder breakdown
- [ ] Tests pass for output organization
- [ ] Backward compatible with existing pipeline configs
