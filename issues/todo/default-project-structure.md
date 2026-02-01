# Default Project Structure Implementation

**Status**: TODO
**Priority**: Medium
**Created**: 2026-02-01

## Overview

Implement a simple, consistent media folder structure as the default option for all projects.

## Default Structure (Minimal)

```
{project-root}/
├── media/
│   ├── imported/     # User-imported media (videos, images, audio)
│   ├── generated/    # AI-generated content (from pipelines/skills)
│   └── temp/         # Temporary processing files (auto-cleaned)
└── output/           # Final exported renders
```

This is the **default option** - simple and sufficient for most projects.

## Extended Structure (Full QCut)

For larger projects, expand to the full structure:

```
{project-root}/
├── project.qcut              # Project metadata file
├── media/
│   ├── imported/             # User-imported media
│   ├── generated/            # AI-generated content
│   └── temp/                 # Temporary processing files
├── skills/                   # Project-specific skills
│   ├── ai-content-pipeline/
│   └── ffmpeg-skill/
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
# Create default structure (minimal)
mkdir -p media/{imported,generated,temp} output

# Create extended structure (full)
mkdir -p media/{imported,generated,temp} output cache skills docs

# Move media files to imported
mv *.mp4 *.mov *.webm media/imported/ 2>/dev/null
mv *.jpg *.png *.gif *.webp media/imported/ 2>/dev/null
mv *.mp3 *.wav *.aac media/imported/ 2>/dev/null

# Symlink management
find media/imported -type l              # List symlinks
find media/imported -xtype l             # Find broken symlinks
readlink media/imported/file.mp4         # Show symlink target

# Cleanup temp files
rm -rf media/temp/*
```

## Acceptance Criteria

- [ ] New projects automatically create `media/{imported,generated,temp}` and `output/`
- [ ] AI-generated content saves to `media/generated/`
- [ ] User imports go to `media/imported/`
- [ ] Temp files auto-clean after export
- [ ] Organize command can upgrade to extended structure
- [ ] Symlink import works on Unix/macOS
- [ ] Copy fallback works on Windows
