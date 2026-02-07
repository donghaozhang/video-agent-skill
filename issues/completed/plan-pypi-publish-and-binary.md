# Plan: Pre-Merge PyPI Publishing + Python Binary

## Problem

Current CI/CD flow is **post-merge**: tag push → GitHub Release → PyPI publish. This means broken packages can land on `main` before anyone validates the published artifact. We want:

1. **PyPI publish gated before merge** — validate the package builds and publishes correctly as a PR requirement
2. **Standalone Python binary** — users can download and run `aicp` without `pip install`

## Current State

| Workflow | Trigger | What it does |
|---|---|---|
| `test.yml` | push to main, PRs to main | Run tests on Python 3.10/3.11/3.12 |
| `release.yml` | tag push `v*.*.*` | Create GitHub Release from tag |
| `publish.yml` | GitHub Release published | Build + publish to PyPI |

**Package**: `video-ai-studio` v1.0.19 on PyPI
**Entry points**: `ai-content-pipeline`, `aicp`, `vimax`, `fal-image-to-video`, `fal-text-to-video`

---

## Proposed CI/CD Pipeline

### New Flow

```
PR opened/updated
  ├── test.yml          → run pytest (existing, unchanged)
  ├── publish-check.yml → build sdist+wheel, publish to TestPyPI ← NEW
  │     └── verify install from TestPyPI works
  └── binary.yml        → build standalone binaries (Linux/macOS/Windows) ← NEW
          └── upload as PR artifacts

All checks pass → merge allowed

Merge to main
  └── (nothing automatic — intentional)

Tag push v*.*.*
  ├── release.yml       → create GitHub Release (existing, unchanged)
  │     └── publish.yml → publish to real PyPI (existing, unchanged)
  └── binary.yml        → build binaries, attach to GitHub Release ← NEW
```

### Why TestPyPI on PR (not real PyPI)

- Publishing to real PyPI on every PR would create version conflicts and spam
- TestPyPI validates the full build→upload→install cycle without polluting the real index
- If TestPyPI succeeds, real PyPI will succeed (same toolchain)

---

## Subtask 1: Pre-Merge Publish Validation (`publish-check.yml`)

### Workflow: `.github/workflows/publish-check.yml`

**Trigger**: PRs to `main`

**Steps**:
1. Checkout code
2. Set up Python 3.12
3. Install build + twine
4. Auto-bump version with `.devN` suffix (so TestPyPI accepts it)
   - e.g., `1.0.19` → `1.0.19.dev{PR_NUMBER}{RUN_NUMBER}`
5. `python -m build` — build sdist and wheel
6. `twine check dist/*` — validate metadata
7. Publish to TestPyPI using `pypa/gh-action-pypi-publish` with `repository-url: https://test.pypi.org/legacy/`
8. Verify install: `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ video-ai-studio=={dev_version}`
9. Smoke test: `aicp --help` returns exit code 0

### Secrets Required

| Secret | Purpose |
|---|---|
| `TEST_PYPI_API_TOKEN` | Upload to TestPyPI |
| `PYPI_API_TOKEN` | Already exists for real PyPI |

### Branch Protection

Add `publish-check` as a required status check on `main` branch so PRs cannot merge until the package builds and publishes successfully.

---

## Subtask 2: Python Binary Build (`binary.yml`)

### Approach: PyInstaller

PyInstaller is the standard tool for creating standalone Python executables. It bundles the Python interpreter + all dependencies into a single file or folder.

**Why PyInstaller over alternatives**:
- **vs Nuitka**: PyInstaller is simpler, better community support, no C compiler needed
- **vs cx_Freeze**: PyInstaller handles complex dependency trees better
- **vs shiv/zipapp**: Those still require Python installed; PyInstaller doesn't

### Workflow: `.github/workflows/binary.yml`

**Triggers**:
- PRs to `main` — build binaries, upload as workflow artifacts (for testing)
- Tag push `v*.*.*` — build binaries, attach to GitHub Release

**Matrix build**:

| OS | Runner | Output |
|---|---|---|
| Linux x86_64 | `ubuntu-latest` | `aicp-linux-x86_64` |
| macOS ARM | `macos-latest` | `aicp-macos-arm64` |
| macOS Intel | `macos-13` | `aicp-macos-x86_64` |
| Windows x64 | `windows-latest` | `aicp-windows-x64.exe` |

### Steps

1. Checkout code
2. Set up Python 3.12
3. `pip install -e . && pip install pyinstaller`
4. Run PyInstaller:
   ```bash
   pyinstaller --onefile \
     --name aicp \
     --hidden-import ai_content_pipeline \
     --hidden-import fal_text_to_video \
     --hidden-import fal_image_to_video \
     --collect-data ai_content_pipeline \
     packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py
   ```
5. Smoke test the binary: `./dist/aicp --help`
6. Upload artifact (PR) or attach to release (tag)

### PyInstaller Spec File: `aicp.spec`

Create a committed spec file for reproducible builds:

```python
# aicp.spec
a = Analysis(
    ['packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py'],
    pathex=['.'],
    hiddenimports=[
        'ai_content_pipeline',
        'ai_content_pipeline.config',
        'ai_content_pipeline.models',
        'ai_content_pipeline.pipeline',
        'ai_content_pipeline.cli',
        'ai_content_pipeline.cli.exit_codes',
        'fal_text_to_video',
        'fal_image_to_video',
        'fal_avatar',
        'fal_video_to_video',
        'fal_image_to_image',
    ],
    datas=[
        ('packages/core/ai_content_pipeline/ai_content_pipeline/config', 'ai_content_pipeline/config'),
    ],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='aicp',
    console=True,
    strip=False,
)
```

### Binary Distribution

On GitHub Release, binaries are attached as assets:

```
v1.0.20
  ├── video_ai_studio-1.0.20.tar.gz      (sdist)
  ├── video_ai_studio-1.0.20-py3-none-any.whl  (wheel)
  ├── aicp-linux-x86_64                   (Linux binary)
  ├── aicp-macos-arm64                    (macOS ARM binary)
  ├── aicp-macos-x86_64                   (macOS Intel binary)
  └── aicp-windows-x64.exe               (Windows binary)
```

Users install with:
```bash
# Option A: pip (existing)
pip install video-ai-studio

# Option B: download binary (new)
curl -L https://github.com/donghaozhang/video-agent-skill/releases/latest/download/aicp-linux-x86_64 -o aicp
chmod +x aicp
./aicp --help
```

---

## Subtask 3: Version Management

### Problem
TestPyPI needs unique versions per upload. Real PyPI needs clean semver.

### Solution: Dev Version Suffix for PRs

In `publish-check.yml`:
```bash
# Compute dev version from PR number + run number
BASE_VERSION=$(python -c "exec(open('setup.py').read()); print(VERSION)")
DEV_VERSION="${BASE_VERSION}.dev${PR_NUMBER}${RUN_NUMBER}"

# Temporarily patch setup.py for TestPyPI build
sed -i "s/VERSION = \"${BASE_VERSION}\"/VERSION = \"${DEV_VERSION}\"/" setup.py
```

Real releases keep the clean version from `setup.py` (no change needed).

---

## Subtask 4: Update Existing Workflows

### `test.yml` — Add pytest runner

Update to also run the full pytest suite (currently only runs `test_core.py` and `test_integration.py`):

```yaml
- name: Run pytest suite
  run: python -m pytest tests/ -v --tb=short
```

### `publish.yml` — No changes

Keep as-is. It already handles real PyPI publishing on release.

### `release.yml` — No changes

Keep as-is. It already creates releases from tags.

---

## Implementation Order

| # | Task | Depends On | Files |
|---|---|---|---|
| 1 | Create `publish-check.yml` | — | `.github/workflows/publish-check.yml` |
| 2 | Set up TestPyPI token | — | GitHub repo Settings → Secrets |
| 3 | Create `aicp.spec` | — | `aicp.spec` |
| 4 | Create `binary.yml` | #3 | `.github/workflows/binary.yml` |
| 5 | Add branch protection rules | #1 | GitHub repo Settings → Branches |
| 6 | Update `test.yml` with pytest | — | `.github/workflows/test.yml` |
| 7 | Test full flow with a real PR | #1, #4 | — |

---

## Files to Create/Modify

### New Files
- `.github/workflows/publish-check.yml` — pre-merge TestPyPI validation
- `.github/workflows/binary.yml` — cross-platform binary builds
- `aicp.spec` — PyInstaller spec for reproducible builds

### Modified Files
- `.github/workflows/test.yml` — add pytest suite

### No Changes
- `.github/workflows/publish.yml` — already correct
- `.github/workflows/release.yml` — already correct
- `setup.py` — already has correct entry_points

---

## Secrets Checklist

| Secret | Status | Where |
|---|---|---|
| `PYPI_API_TOKEN` | Already exists | GitHub repo secrets |
| `TEST_PYPI_API_TOKEN` | **Needs setup** | GitHub repo secrets |
| `GITHUB_TOKEN` | Automatic | Built-in |

---

## Risk & Rollback

| Risk | Mitigation |
|---|---|
| TestPyPI upload fails on version conflict | Dev suffix includes run number for uniqueness |
| PyInstaller misses hidden imports | Spec file explicitly lists all subpackages; smoke test catches failures |
| Binary too large (>100MB) | Use `--onefile` + UPX compression; monitor artifact size |
| macOS binary not signed | Accept Gatekeeper warning for now; code signing is a future enhancement |
| Branch protection blocks emergency fixes | Admin override always available |
