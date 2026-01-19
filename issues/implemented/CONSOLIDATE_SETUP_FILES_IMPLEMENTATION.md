# Implementation Plan: Consolidate Setup Files into Single setup.py

**Created:** 2026-01-19
**Status:** Ready for Implementation
**Estimated Time:** ~15 minutes
**Priority:** Medium

---

## Overview

Consolidate 4 separate setup.py files into a single root setup.py to enable single-command installation.

**Goal:** `pip install -e .` installs everything with all CLI commands.

---

## Pre-Implementation Verification (Completed)

| Check | Status | Details |
|-------|--------|---------|
| CLI modules exist | ✅ | `image-to-video/cli.py`, `text-to-video/cli.py` |
| `main()` functions exist | ✅ | Line 140 and 142 respectively |
| Root setup.py structure | ✅ | Uses `find_packages()` correctly |
| Directory structure | ✅ | Hyphenated dirs: `image-to-video`, `text-to-video` |

---

## Subtasks

### Subtask 1: Update Root setup.py Entry Points

**Estimated Time:** 5 minutes
**Risk:** Low

**File to Modify:**
- `setup.py` (root)

**Current Code (lines 151-157):**
```python
entry_points={
    "console_scripts": [
        # AI Content Pipeline
        "ai-content-pipeline=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
        "aicp=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
    ],
},
```

**New Code:**
```python
entry_points={
    "console_scripts": [
        # AI Content Pipeline (main CLI)
        "ai-content-pipeline=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
        "aicp=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
        # FAL Image-to-Video CLI
        "fal-image-to-video=packages.providers.fal.image_to_video.fal_image_to_video.cli:main",
        # FAL Text-to-Video CLI
        "fal-text-to-video=packages.providers.fal.text_to_video.fal_text_to_video.cli:main",
    ],
},
```

**Note:** Directory names use hyphens (`image-to-video`) but Python packages use underscores (`image_to_video`). The entry point paths must use underscores.

---

### Subtask 2: Verify Package Discovery

**Estimated Time:** 2 minutes
**Risk:** Low

**Verification Steps:**
1. Check that `find_packages(include=['packages', 'packages.*'])` discovers the FAL CLI packages
2. Run: `python -c "from setuptools import find_packages; print([p for p in find_packages(include=['packages', 'packages.*']) if 'fal' in p])"`

**Expected Output Should Include:**
- `packages.providers.fal.image_to_video`
- `packages.providers.fal.text_to_video`
- `packages.providers.fal.image_to_video.fal_image_to_video`
- `packages.providers.fal.text_to_video.fal_text_to_video`

---

### Subtask 3: Test Installation

**Estimated Time:** 3 minutes
**Risk:** Low

**Commands:**
```bash
# Uninstall existing packages
pip uninstall video_ai_studio fal-image-to-video fal-text-to-video -y 2>/dev/null

# Reinstall from root
pip install -e .

# Verify installation
pip show video_ai_studio
```

---

### Subtask 4: Test All CLI Commands

**Estimated Time:** 3 minutes
**Risk:** Medium

**Commands to Test:**
```bash
# Main CLI
ai-content-pipeline --help
aicp --help

# FAL CLIs (new)
fal-image-to-video --help
fal-text-to-video --help
```

**Expected:** All commands should display help text without errors.

---

### Subtask 5: Delete Redundant Setup Files

**Estimated Time:** 1 minute
**Risk:** Low

**Files to Delete:**

| File Path | Lines | Reason |
|-----------|-------|--------|
| `packages/providers/fal/avatar-generation/setup.py` | 16 | No CLI, code included via find_packages |
| `packages/providers/fal/image-to-video/setup.py` | 23 | Entry point moved to root setup.py |
| `packages/providers/fal/text-to-video/setup.py` | 23 | Entry point moved to root setup.py |

**Commands:**
```bash
rm packages/providers/fal/avatar-generation/setup.py
rm packages/providers/fal/image-to-video/setup.py
rm packages/providers/fal/text-to-video/setup.py
```

---

### Subtask 6: Update Documentation

**Estimated Time:** 2 minutes
**Risk:** Low

**Files to Update:**
| File | Change |
|------|--------|
| `README.md` | Update installation instructions if needed |
| `CLAUDE.md` | No change needed (already shows `pip install -e .`) |
| `issues/multiple-setup-files-report.md` | Mark as resolved |

---

## Unit Tests

**File:** `tests/unit/test_setup_consolidation.py`

```python
"""Tests to verify setup.py consolidation works correctly."""

import subprocess
import sys


def test_main_cli_available():
    """Test ai-content-pipeline CLI is available."""
    result = subprocess.run(
        [sys.executable, "-m", "packages.core.ai_content_pipeline.ai_content_pipeline", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0 or "usage" in result.stdout.lower()


def test_fal_image_to_video_cli_importable():
    """Test fal-image-to-video CLI module is importable."""
    from packages.providers.fal.image_to_video.fal_image_to_video import cli
    assert hasattr(cli, 'main')


def test_fal_text_to_video_cli_importable():
    """Test fal-text-to-video CLI module is importable."""
    from packages.providers.fal.text_to_video.fal_text_to_video import cli
    assert hasattr(cli, 'main')


def test_entry_points_registered():
    """Test all entry points are registered after installation."""
    import pkg_resources

    # Get entry points for video_ai_studio
    try:
        dist = pkg_resources.get_distribution('video_ai_studio')
        entry_points = dist.get_entry_map().get('console_scripts', {})

        expected = ['ai-content-pipeline', 'aicp', 'fal-image-to-video', 'fal-text-to-video']
        for ep in expected:
            assert ep in entry_points, f"Entry point {ep} not found"
    except pkg_resources.DistributionNotFound:
        # Package not installed in editable mode, skip
        pass
```

---

## Rollback Plan

If issues occur after implementation:

```bash
# Restore deleted files from git
git checkout HEAD -- packages/providers/fal/avatar-generation/setup.py
git checkout HEAD -- packages/providers/fal/image-to-video/setup.py
git checkout HEAD -- packages/providers/fal/text-to-video/setup.py

# Revert setup.py changes
git checkout HEAD -- setup.py

# Reinstall
pip install -e .
pip install -e ./packages/providers/fal/image-to-video/
pip install -e ./packages/providers/fal/text-to-video/
```

---

## Summary

| Subtask | Time | Files |
|---------|------|-------|
| 1. Update entry points | 5 min | `setup.py` |
| 2. Verify package discovery | 2 min | - |
| 3. Test installation | 3 min | - |
| 4. Test CLI commands | 3 min | - |
| 5. Delete redundant setup files | 1 min | 3 files |
| 6. Update documentation | 2 min | `issues/*.md` |
| **Total** | **~15 min** | |

---

## Benefits After Implementation

| Metric | Before | After |
|--------|--------|-------|
| Install commands | 4 | 1 |
| setup.py files | 4 | 1 |
| Maintenance complexity | High | Low |
| Version sources | 4 | 1 |
| CLI entry points | Scattered | Centralized |
