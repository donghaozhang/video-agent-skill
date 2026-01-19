# Plan: Consolidate Setup Files into Single setup.py

**Created:** 2026-01-19
**Implemented:** 2026-01-19
**Status:** ✅ Completed
**Priority:** Medium

---

## Problem

Currently there are **4 separate setup.py files** requiring multiple install commands:

```bash
pip install -e .
pip install -e ./packages/providers/fal/avatar-generation/
pip install -e ./packages/providers/fal/image-to-video/
pip install -e ./packages/providers/fal/text-to-video/
```

This is complicated and error-prone.

---

## Goal

**Single command installation:**
```bash
pip install -e .
```

This should install everything including all CLI commands.

---

## Files to Modify

### Keep (modify):
| File | Action |
|------|--------|
| `./setup.py` | Add missing entry points |
| `./pyproject.toml` | Keep as-is (build config only) |

### Delete after consolidation:
| File | Reason |
|------|--------|
| `packages/providers/fal/avatar-generation/setup.py` | Merge into root setup.py |
| `packages/providers/fal/image-to-video/setup.py` | Merge into root setup.py |
| `packages/providers/fal/text-to-video/setup.py` | Merge into root setup.py |

---

## Changes Required

### 1. Update Root `setup.py` Entry Points

**Current:**
```python
entry_points={
    "console_scripts": [
        "ai-content-pipeline=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
        "aicp=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
    ],
},
```

**New:**
```python
entry_points={
    "console_scripts": [
        # Main CLI
        "ai-content-pipeline=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
        "aicp=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
        # FAL Image-to-Video CLI
        "fal-image-to-video=packages.providers.fal.image_to_video.fal_image_to_video.cli:main",
        # FAL Text-to-Video CLI
        "fal-text-to-video=packages.providers.fal.text_to_video.fal_text_to_video.cli:main",
    ],
},
```

### 2. Verify CLI Module Paths Exist

Before adding entry points, confirm these paths are correct:
- `packages/providers/fal/image-to-video/fal_image_to_video/cli.py` → `main()`
- `packages/providers/fal/text-to-video/fal_text_to_video/cli.py` → `main()`

### 3. Update Python Version Requirement

**Current in fal_avatar:** `python_requires=">=3.8"`
**Should be:** `python_requires=">=3.10"` (consistent with main package)

Already handled by root setup.py.

### 4. Delete Redundant Setup Files

After verification:
```bash
rm packages/providers/fal/avatar-generation/setup.py
rm packages/providers/fal/image-to-video/setup.py
rm packages/providers/fal/text-to-video/setup.py
```

---

## Implementation Steps

| Step | Task | Risk |
|------|------|------|
| 1 | Verify CLI module paths exist and have `main()` function | Low |
| 2 | Add new entry points to root `setup.py` | Low |
| 3 | Test installation: `pip install -e .` | Low |
| 4 | Test all CLI commands work | Medium |
| 5 | Delete redundant setup.py files | Low |
| 6 | Update documentation | Low |

---

## Testing Checklist

After consolidation, verify these commands work:

```bash
# Uninstall and reinstall
pip uninstall video_ai_studio fal_avatar fal-image-to-video fal-text-to-video -y
pip install -e .

# Test all CLI commands
ai-content-pipeline --help
aicp --help
fal-image-to-video --help
fal-text-to-video --help
```

---

## Rollback Plan

If issues occur:
1. Restore deleted setup.py files from git
2. Revert changes to root setup.py
3. Re-install using multiple commands

---

## Benefits After Consolidation

| Before | After |
|--------|-------|
| 4 install commands | 1 install command |
| 4 setup.py files | 1 setup.py file |
| Version inconsistency | Single version source |
| Duplicate dependencies | Centralized dependencies |
| Complex maintenance | Simple maintenance |

---

## Final Structure

```
veo3-fal-video-ai/
├── setup.py              # Single consolidated setup (all entry points)
├── pyproject.toml        # Build config & tool settings
└── packages/
    └── providers/
        └── fal/
            ├── avatar-generation/
            │   └── (no setup.py)
            ├── image-to-video/
            │   └── (no setup.py)
            └── text-to-video/
                └── (no setup.py)
```

---

## Notes

- The `fal_avatar` package has no CLI entry point, so nothing to add for it
- All package code is already included via `find_packages(include=['packages', 'packages.*'])`
- Only entry points (CLI commands) were missing from root setup.py
