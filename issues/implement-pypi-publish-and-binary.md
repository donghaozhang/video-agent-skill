# Implementation: Pre-Merge PyPI Publishing + Python Binary

> Parent plan: [plan-pypi-publish-and-binary.md](plan-pypi-publish-and-binary.md)

## Overview

Implement a CI/CD pipeline that validates PyPI publishing **before** merging to main, and produces standalone Python binaries for every release. This is a long-term infrastructure investment — all future releases and contributors benefit from gated publishing and zero-install binaries.

**Estimated total time**: ~60 minutes (5 subtasks)

---

## Subtask 1: Create Single Source of Truth for Version (10 min)

### Problem
Version is duplicated across `setup.py` (`VERSION = "1.0.19"`) and `packages/core/ai_content_pipeline/ai_content_pipeline/__init__.py` (`__version__ = "1.0.18"`) — they're already out of sync. CI workflows need to read and patch the version dynamically. A single canonical location prevents drift.

### Implementation

Create `packages/core/ai_content_pipeline/ai_content_pipeline/_version.py` as the single source:

```python
__version__ = "1.0.20"
```

Both `setup.py` and `__init__.py` import from it. CI scripts read/patch this one file.

### Files to Create
| File | Purpose |
|---|---|
| `packages/core/ai_content_pipeline/ai_content_pipeline/_version.py` | Single source of truth for package version |

### Files to Modify
| File | Change |
|---|---|
| `setup.py` (line 13) | Replace hardcoded `VERSION = "1.0.19"` with import from `_version.py` |
| `packages/core/ai_content_pipeline/ai_content_pipeline/__init__.py` (line 15) | Replace hardcoded `__version__ = "1.0.18"` with `from ._version import __version__` |

### Tests
| File | Cases |
|---|---|
| `tests/test_version.py` | 1. `_version.__version__` matches `setup.py` version. 2. `ai_content_pipeline.__version__` matches `_version.__version__`. 3. Version string is valid PEP 440 (regex check). |

### Acceptance Criteria
- `python -c "from ai_content_pipeline._version import __version__; print(__version__)"` works
- `python -c "import ai_content_pipeline; print(ai_content_pipeline.__version__)"` prints same version
- `python setup.py --version` prints same version
- All existing tests pass

---

## Subtask 2: Create Pre-Merge TestPyPI Workflow (15 min)

### Problem
Currently, `publish.yml` only runs **after** a GitHub Release is created (post-merge). Broken builds can land on main. We need a pre-merge gate that proves the package builds, uploads, installs, and runs.

### Implementation

Create `.github/workflows/publish-check.yml` that:
1. Triggers on PRs to `main`
2. Builds sdist + wheel with a `.devN` version suffix
3. Uploads to TestPyPI
4. Installs from TestPyPI into a fresh venv
5. Runs `aicp --help` as a smoke test

The dev version suffix uses `{base}.dev{pr_number}{run_number}` to guarantee uniqueness on TestPyPI without polluting real PyPI.

### Files to Create
| File | Purpose |
|---|---|
| `.github/workflows/publish-check.yml` | Pre-merge TestPyPI validation workflow |

### File Contents (`.github/workflows/publish-check.yml`)

```yaml
name: Publish Check (TestPyPI)

on:
  pull_request:
    branches: [ main ]

permissions:
  contents: read

jobs:
  build-and-test-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build tools
        run: |
          python -m pip install --upgrade pip
          python -m pip install build twine

      - name: Compute dev version
        id: version
        run: |
          BASE=$(python -c "
          import re
          with open('packages/core/ai_content_pipeline/ai_content_pipeline/_version.py') as f:
              match = re.search(r'__version__\s*=\s*[\"'\''](.*?)[\"'\'']', f.read())
              print(match.group(1))
          ")
          DEV="${BASE}.dev${{ github.event.pull_request.number }}${{ github.run_number }}"
          echo "BASE_VERSION=${BASE}" >> $GITHUB_OUTPUT
          echo "DEV_VERSION=${DEV}" >> $GITHUB_OUTPUT
          echo "Publishing as version: ${DEV}"

      - name: Patch version for TestPyPI
        run: |
          sed -i 's/__version__ = .*/__version__ = "${{ steps.version.outputs.DEV_VERSION }}"/' \
            packages/core/ai_content_pipeline/ai_content_pipeline/_version.py

      - name: Build distributions
        run: python -m build

      - name: Check distributions
        run: python -m twine check dist/*

      - name: Upload to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.TEST_PYPI_API_TOKEN }}
          repository-url: https://test.pypi.org/legacy/
          skip-existing: true

      - name: Verify install from TestPyPI
        run: |
          python -m venv /tmp/test-install
          /tmp/test-install/bin/pip install \
            --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            "video-ai-studio==${{ steps.version.outputs.DEV_VERSION }}"
          /tmp/test-install/bin/aicp --help

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist-testpypi
          path: dist/
          retention-days: 5
```

### Files to Modify
None — this is additive.

### Tests
No automated tests — the workflow **is** the test. Verification:
1. Open a test PR to main
2. Confirm `publish-check` job appears in PR checks
3. Confirm it builds, uploads to TestPyPI, and installs successfully

### Acceptance Criteria
- Workflow triggers on every PR to `main`
- Build produces valid sdist + wheel
- TestPyPI upload succeeds
- Install from TestPyPI succeeds
- `aicp --help` returns exit code 0

### Manual Step Required
- **Add `TEST_PYPI_API_TOKEN` secret** in GitHub repo → Settings → Secrets and variables → Actions
- Get token from https://test.pypi.org/manage/account/token/

---

## Subtask 3: Create PyInstaller Spec File (10 min)

### Problem
PyInstaller needs to know about hidden imports (packages not discoverable via static analysis) and data files. A committed `.spec` file makes builds reproducible across all CI runners and developer machines.

### Implementation

Create `aicp.spec` at project root with explicit hidden imports for all provider packages and data file collection for config YAML files.

### Files to Create
| File | Purpose |
|---|---|
| `aicp.spec` | PyInstaller spec for reproducible cross-platform binary builds |

### File Contents (`aicp.spec`)

```python
# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for the aicp (AI Content Pipeline) binary.

Build with: pyinstaller aicp.spec
Output:     dist/aicp (or dist/aicp.exe on Windows)

This spec file ensures all provider packages and config data are bundled,
even when PyInstaller's static analysis can't discover them.
"""

import sys
from pathlib import Path

block_cipher = None

# Project root (where this spec file lives)
PROJECT_ROOT = Path(SPECPATH)

a = Analysis(
    [str(PROJECT_ROOT / 'packages' / 'core' / 'ai_content_pipeline' / 'ai_content_pipeline' / '__main__.py')],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        # Config YAML files needed at runtime
        (str(PROJECT_ROOT / 'packages' / 'core' / 'ai_content_pipeline' / 'ai_content_pipeline' / 'config'), 'ai_content_pipeline/config'),
    ],
    hiddenimports=[
        # Core pipeline
        'ai_content_pipeline',
        'ai_content_pipeline.config',
        'ai_content_pipeline.config.constants',
        'ai_content_pipeline.models',
        'ai_content_pipeline.pipeline',
        'ai_content_pipeline.pipeline.manager',
        'ai_content_pipeline.cli',
        'ai_content_pipeline.cli.exit_codes',
        'ai_content_pipeline.cli.interactive',
        'ai_content_pipeline.cli.output',
        'ai_content_pipeline.cli.paths',
        'ai_content_pipeline.cli.stream',
        'ai_content_pipeline.registry',
        'ai_content_pipeline.registry_data',
        'ai_content_pipeline.video_analysis',
        'ai_content_pipeline.motion_transfer',
        'ai_content_pipeline.speech_to_text',
        'ai_content_pipeline.grid_generator',
        'ai_content_pipeline.project_structure_cli',
        # FAL providers
        'fal_text_to_video',
        'fal_text_to_video.config',
        'fal_text_to_video.models',
        'fal_text_to_video.utils',
        'fal_image_to_video',
        'fal_image_to_video.config',
        'fal_image_to_video.models',
        'fal_image_to_video.utils',
        'fal_image_to_image',
        'fal_image_to_image.config',
        'fal_image_to_image.models',
        'fal_image_to_image.utils',
        'fal_video_to_video',
        'fal_video_to_video.config',
        'fal_video_to_video.models',
        'fal_video_to_video.utils',
        'fal_avatar',
        'fal_avatar.config',
        'fal_avatar.models',
        # Platform
        'ai_content_platform',
        # Third-party hidden imports PyInstaller often misses
        'yaml',
        'dotenv',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy optional deps to keep binary small
        'matplotlib',
        'jupyter',
        'notebook',
        'ipython',
        'scipy',
        'numpy',
        'cv2',
        'moviepy',
        'tkinter',
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='aicp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

### Files to Modify
| File | Change |
|---|---|
| `.gitignore` | Add `build/`, `dist/`, `*.spec.bak` (PyInstaller artifacts) |

### Tests
| File | Cases |
|---|---|
| `tests/test_pyinstaller_spec.py` | 1. `aicp.spec` file exists and is valid Python (compile check). 2. All `hiddenimports` are actually importable in the current environment. 3. Entry point path in spec matches `__main__.py` location. |

### Acceptance Criteria
- `pyinstaller aicp.spec` produces `dist/aicp` binary locally
- `./dist/aicp --help` runs and exits 0
- Binary size is under 100MB

---

## Subtask 4: Create Cross-Platform Binary Build Workflow (15 min)

### Problem
Users shouldn't need Python installed to use `aicp`. We need binaries for Linux, macOS (ARM + Intel), and Windows, built automatically in CI.

### Implementation

Create `.github/workflows/binary.yml` with a matrix strategy for 4 OS targets. On PRs, binaries are uploaded as artifacts for testing. On tag pushes, binaries are attached to the GitHub Release.

### Files to Create
| File | Purpose |
|---|---|
| `.github/workflows/binary.yml` | Cross-platform binary build workflow |

### File Contents (`.github/workflows/binary.yml`)

```yaml
name: Build Binaries

on:
  pull_request:
    branches: [ main ]
  push:
    tags:
      - 'v*.*.*'

permissions:
  contents: write  # Needed to attach assets to releases

jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            artifact_name: aicp-linux-x86_64
            asset_name: aicp-linux-x86_64
          - os: macos-latest
            artifact_name: aicp-macos-arm64
            asset_name: aicp-macos-arm64
          - os: macos-13
            artifact_name: aicp-macos-x86_64
            asset_name: aicp-macos-x86_64
          - os: windows-latest
            artifact_name: aicp-windows-x64.exe
            asset_name: aicp-windows-x64.exe

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install pyinstaller

      - name: Build binary
        run: pyinstaller aicp.spec

      - name: Rename binary (Unix)
        if: runner.os != 'Windows'
        run: mv dist/aicp dist/${{ matrix.artifact_name }}

      - name: Rename binary (Windows)
        if: runner.os == 'Windows'
        run: mv dist/aicp.exe dist/${{ matrix.artifact_name }}

      - name: Smoke test
        run: dist/${{ matrix.artifact_name }} --help

      - name: Upload artifact (PR)
        if: github.event_name == 'pull_request'
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact_name }}
          path: dist/${{ matrix.artifact_name }}
          retention-days: 7

      - name: Attach to release (tag)
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v2
        with:
          files: dist/${{ matrix.artifact_name }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Files to Modify
None — this is additive.

### Tests
No automated tests — the workflow **is** the test. Verification:
1. Open a test PR to main
2. Confirm all 4 matrix jobs run
3. Download artifact and run `./aicp-linux-x86_64 --help`

### Acceptance Criteria
- All 4 matrix builds succeed (Linux, macOS ARM, macOS Intel, Windows)
- Smoke test passes on each platform
- PR artifacts are downloadable
- Tag push attaches binaries to GitHub Release

---

## Subtask 5: Update test.yml + Add Branch Protection (10 min)

### Problem
Current `test.yml` only runs `test_core.py` and `test_integration.py`, missing the full pytest suite (~572 tests). Branch protection doesn't require publish-check or binary builds.

### Implementation

1. Add `python -m pytest tests/ -v --tb=short` step to `test.yml`
2. Document the branch protection rules to add (manual GitHub Settings step)

### Files to Modify
| File | Change |
|---|---|
| `.github/workflows/test.yml` (line 37-41) | Add `python -m pytest tests/ -v --tb=short` step after existing test steps |

### Updated test.yml

Add after line 41 (after "Run integration tests"):
```yaml
      - name: Run full pytest suite
        run: |
          python -m pytest tests/ -v --tb=short
```

### Branch Protection (Manual)

In GitHub repo → Settings → Branches → Branch protection rules for `main`:

| Required status check | Purpose |
|---|---|
| `test` (3.10, 3.11, 3.12) | Already exists |
| `build-and-test-publish` | **Add** — gates on TestPyPI publish |
| `build` (linux, macos-arm, macos-intel, windows) | **Add** — gates on binary builds |

### Tests
| File | Cases |
|---|---|
| `tests/test_workflow_files.py` | 1. All `.yml` files in `.github/workflows/` are valid YAML. 2. `test.yml` contains a pytest step. 3. `publish-check.yml` exists and references `TEST_PYPI_API_TOKEN`. 4. `binary.yml` exists and has 4-item matrix. |

### Acceptance Criteria
- `test.yml` runs the full pytest suite in CI
- All required status checks block merge when failing
- Admin override remains available for emergencies

---

## Summary: All Files

### New Files (6)
| File | Subtask |
|---|---|
| `packages/core/ai_content_pipeline/ai_content_pipeline/_version.py` | 1 |
| `.github/workflows/publish-check.yml` | 2 |
| `aicp.spec` | 3 |
| `.github/workflows/binary.yml` | 4 |
| `tests/test_version.py` | 1 |
| `tests/test_pyinstaller_spec.py` | 3 |
| `tests/test_workflow_files.py` | 5 |

### Modified Files (4)
| File | Subtask | Change |
|---|---|---|
| `setup.py` | 1 | Import version from `_version.py` |
| `packages/core/ai_content_pipeline/ai_content_pipeline/__init__.py` | 1 | Import `__version__` from `_version` |
| `.github/workflows/test.yml` | 5 | Add pytest step |
| `.gitignore` | 3 | Add PyInstaller artifacts |

### Unchanged Files (2)
| File | Reason |
|---|---|
| `.github/workflows/publish.yml` | Already correct for real PyPI |
| `.github/workflows/release.yml` | Already correct for tag-based releases |

### Manual Steps (2)
| Step | Subtask | Where |
|---|---|---|
| Add `TEST_PYPI_API_TOKEN` secret | 2 | GitHub → Settings → Secrets |
| Add branch protection rules | 5 | GitHub → Settings → Branches |

---

## Dependency Graph

```
Subtask 1 (version) ─────┬──→ Subtask 2 (publish-check.yml)
                          │
                          └──→ Subtask 3 (aicp.spec) ──→ Subtask 4 (binary.yml)
                                                                     │
Subtask 5 (test.yml + protection) ◄──────────────────────────────────┘
```

Subtask 1 is the foundation — everything else depends on having a single version source. Subtasks 2-4 can be parallelized after subtask 1. Subtask 5 is last because branch protection should only be enabled after all workflows exist.

---

## Long-Term Benefits

1. **No broken PyPI releases** — every PR proves the package publishes correctly before merge
2. **Zero-install distribution** — users download a single binary, no Python required
3. **Version consistency** — single `_version.py` prevents drift between setup.py and __init__.py
4. **Cross-platform confidence** — binaries built and smoke-tested on 4 OS targets per PR
5. **Contributor-friendly** — new contributors get immediate feedback on packaging issues
6. **Reproducible builds** — committed `.spec` file means anyone can build the binary locally
