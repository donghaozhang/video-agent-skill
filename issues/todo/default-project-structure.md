# Default Project Structure Implementation

**Status**: TODO
**Priority**: Medium
**Created**: 2026-02-01

## Overview

Implement QCut's standard project structure as the default option for new projects and workspace organization.

## Target Structure

```
Documents/QCut/Projects/{project-name}/
├── project.qcut              # Project metadata file
├── media/                    # All media files
│   ├── imported/             # User-imported media (videos, images, audio)
│   ├── generated/            # AI-generated content (from skills)
│   └── temp/                 # Temporary processing files
├── skills/                   # Project-specific skills
│   ├── ai-content-pipeline/  # AI content generation skill
│   │   ├── Skill.md
│   │   ├── REFERENCE.md
│   │   └── EXAMPLES.md
│   └── ffmpeg-skill/         # FFmpeg processing skill
│       ├── Skill.md
│       └── REFERENCE.md
├── output/                   # Exported videos and renders
├── cache/                    # FFmpeg and processing cache
└── docs/                     # Project documentation (optional)
```

## Implementation Tasks

### 1. Media Organization
- [ ] Videos (.mp4, .mov, .webm, .avi) → `media/imported/` or `media/generated/`
- [ ] Images (.jpg, .png, .webp, .gif) → `media/imported/` or `media/generated/`
- [ ] Audio (.mp3, .wav, .aac, .m4a) → `media/imported/` or `media/generated/`
- [ ] AI-generated content → `media/generated/`
- [ ] User-imported content → `media/imported/`

### 2. Hybrid Symlink Import System
- [ ] Implement symlink-preferred imports (saves disk space)
- [ ] Add copy fallback for Windows without admin/network drives
- [ ] Track metadata: `importMethod`, `originalPath`, `fileSize`

### 3. Skills Organization
- [ ] Each skill as folder with `Skill.md` entry point
- [ ] Support reference files: `REFERENCE.md`, `EXAMPLES.md`, `CONCEPTS.md`
- [ ] Support `scripts/` subfolder for helper scripts

### 4. Output Naming Convention
- [ ] Final renders → `output/`
- [ ] Naming pattern: `{project-name}_{date}_{resolution}.mp4`

### 5. Temporary File Management
- [ ] Processing intermediates → `media/temp/`
- [ ] Cache files → `cache/`
- [ ] Auto-cleanup after export

### 6. Virtual Folder System
- [ ] Metadata-only virtual folders
- [ ] Items can belong to multiple folders (tags)
- [ ] Special "Skills" folder for project skills
- [ ] Max folder depth: 3 levels
- [ ] Folder naming: max 50 characters

## Quick Setup Commands

```bash
# Create standard structure
mkdir -p media/{imported,generated,temp} output cache skills docs

# Move media files
mv *.mp4 *.mov *.webm media/imported/ 2>/dev/null
mv *.jpg *.png *.gif *.webp media/imported/ 2>/dev/null
mv *.mp3 *.wav *.aac media/imported/ 2>/dev/null

# Symlink management
find media/imported -type l              # List symlinks
find media/imported -xtype l             # Find broken symlinks
readlink media/imported/file.mp4         # Show symlink target

# Cleanup
rm -rf media/temp/* cache/*
```

## Acceptance Criteria

- [ ] New projects automatically use this structure
- [ ] Organize command restructures existing projects
- [ ] Symlink import works on Unix/macOS
- [ ] Copy fallback works on Windows
- [ ] Virtual folders display correctly in UI
- [ ] Output naming follows convention
- [ ] Temp files cleaned after export
