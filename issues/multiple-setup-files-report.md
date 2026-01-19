# Multiple Pip Setup Files Report

**Generated:** 2026-01-19

---

## Summary

**Yes, there are multiple pip setup files in this repository.**

| Count | File Type |
|-------|-----------|
| 4 | `setup.py` |
| 1 | `pyproject.toml` |
| **5** | **Total** |

---

## Setup Files Found

### 1. Root `setup.py` (Main Package)
**Path:** `./setup.py`
**Package Name:** `video_ai_studio`
**Version:** 1.0.15
**Purpose:** Main consolidated package for the entire AI Content Generation Suite

```python
PACKAGE_NAME = "video_ai_studio"
VERSION = "1.0.15"
```

**Entry Points:**
- `ai-content-pipeline` → main CLI command
- `aicp` → shorthand alias

**Optional Dependencies:**
- `pipeline` - YAML configuration support
- `google-cloud` - Google Cloud services
- `video` - Video processing (moviepy, ffmpeg)
- `image` - Image processing (Pillow)
- `dev` - Development tools (pytest, black, flake8)
- `jupyter` - Notebook support
- `mcp` - MCP server support
- `all` - Everything

---

### 2. Root `pyproject.toml` (Build Configuration)
**Path:** `./pyproject.toml`
**Purpose:** Build system configuration and tool settings

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
```

**Tool Configurations:**
- `black` - Code formatting (line-length: 88)
- `isort` - Import sorting
- `pytest` - Test configuration

---

### 3. FAL Avatar Generation `setup.py`
**Path:** `./packages/providers/fal/avatar-generation/setup.py`
**Package Name:** `fal_avatar`
**Version:** 0.1.0
**Purpose:** Standalone FAL avatar generation package

```python
name="fal_avatar"
version="0.1.0"
python_requires=">=3.8"
```

**Dependencies:**
- fal-client
- python-dotenv
- requests

---

### 4. FAL Image-to-Video `setup.py`
**Path:** `./packages/providers/fal/image-to-video/setup.py`
**Package Name:** `fal-image-to-video`
**Version:** 1.0.0
**Purpose:** FAL image-to-video generator (Veo 3.1, Sora 2, Kling, Hailuo)

```python
name="fal-image-to-video"
version="1.0.0"
python_requires=">=3.10"
```

**Entry Points:**
- `fal-image-to-video` → CLI command

---

### 5. FAL Text-to-Video `setup.py`
**Path:** `./packages/providers/fal/text-to-video/setup.py`
**Package Name:** `fal-text-to-video`
**Version:** 1.0.0
**Purpose:** FAL text-to-video generator (Sora 2, Kling, Veo)

```python
name="fal-text-to-video"
version="1.0.0"
python_requires=">=3.10"
```

**Entry Points:**
- `fal-text-to-video` → CLI command

---

## Architecture Analysis

```
veo3-fal-video-ai/
├── setup.py                 # Main package (video_ai_studio v1.0.15)
├── pyproject.toml           # Build config & tool settings
└── packages/
    └── providers/
        └── fal/
            ├── avatar-generation/
            │   └── setup.py     # fal_avatar v0.1.0
            ├── image-to-video/
            │   └── setup.py     # fal-image-to-video v1.0.0
            └── text-to-video/
                └── setup.py     # fal-text-to-video v1.0.0
```

---

## Potential Issues

### 1. Version Inconsistency
- Main package: `1.0.15`
- Sub-packages: `0.1.0` and `1.0.0`

### 2. Python Version Requirements
- Main package: `>=3.10`
- fal_avatar: `>=3.8` (inconsistent)
- Other sub-packages: `>=3.10`

### 3. Duplicate Dependencies
All packages require:
- `fal-client`
- `python-dotenv`
- `requests`

These are already in the main `setup.py`.

---

## Recommendations

1. **Consider consolidating** - The sub-package setup.py files may be redundant since the main setup.py already includes all packages

2. **Synchronize Python version** - Update `fal_avatar` to require `>=3.10` for consistency

3. **Use namespace packages** - If sub-packages need independent installation, consider using namespace packages

4. **Remove if unused** - If these sub-packages are not published separately to PyPI, consider removing their individual setup.py files

---

## Current Installation Methods

```bash
# Install main package (recommended)
pip install -e .

# Install with all optional dependencies
pip install -e ".[all]"

# Install specific sub-package (if needed)
pip install -e ./packages/providers/fal/image-to-video/
```
