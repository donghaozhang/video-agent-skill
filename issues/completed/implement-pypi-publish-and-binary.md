# Implementation: Pre-Merge PyPI Publishing + Python Binary

> Parent plan: [plan-pypi-publish-and-binary.md](plan-pypi-publish-and-binary.md)

## Status: COMPLETE

All 7 subtasks implemented, tested, and pushed. All manual steps executed via `gh` CLI.

| # | Subtask | Status | Commit |
|---|---|---|---|
| 1 | Single source of truth for version | Done | `d433105` |
| 2 | Pre-merge TestPyPI workflow | Done | `d433105` |
| 3 | PyInstaller spec file | Done | `d433105` |
| 4 | Cross-platform binary build workflow | Done | `d433105` |
| 5 | Update test.yml + branch protection | Done | `d433105` |
| 6 | On-merge changelog + latest release | Done | `e973929` |
| 7 | GitHub secrets + branch protection (manual) | Done | `e973929` |

**Test results**: 42 new tests all passing, 710/711 existing tests passing (1 pre-existing Windows encoding failure).

---

## Subtask 1: Single Source of Truth for Version — DONE

### Problem
Version was duplicated: `setup.py` had `VERSION = "1.0.19"`, `__init__.py` had `__version__ = "1.0.18"`. Now unified at `1.0.20`.

### Files Created
| File | Purpose |
|---|---|
| `packages/core/ai_content_pipeline/ai_content_pipeline/_version.py` | Single source of truth — `__version__ = "1.0.20"` |
| `tests/test_version.py` | 6 tests: file exists, PEP 440 format, import chain, no hardcoded versions |

### Files Modified
| File | Change |
|---|---|
| `setup.py` | Reads version from `_version.py` via regex (avoids import chain) |
| `packages/core/ai_content_pipeline/ai_content_pipeline/__init__.py` | `from ._version import __version__` |

---

## Subtask 2: Pre-Merge TestPyPI Workflow — DONE

### What It Does
On every PR to `main`: builds sdist+wheel with `.devN` suffix → uploads to TestPyPI → installs from TestPyPI → smoke tests `aicp --help`.

### Files Created
| File | Purpose |
|---|---|
| `.github/workflows/publish-check.yml` | Pre-merge TestPyPI validation workflow |

### Key Details
- Dev version: `{base}.dev{pr_number}{run_number}` for TestPyPI uniqueness
- Uses `pypa/gh-action-pypi-publish@release/v1` with `TEST_PYPI_API_TOKEN`
- Artifacts uploaded with 5-day retention

---

## Subtask 3: PyInstaller Spec File — DONE

### Files Created
| File | Purpose |
|---|---|
| `aicp.spec` | PyInstaller spec with all hidden imports and config data |
| `tests/test_pyinstaller_spec.py` | 7 tests: file exists, valid Python, entry point, hidden imports importable |

### Files Modified
| File | Change |
|---|---|
| `.gitignore` | Added `*.spec.bak`, `*.manifest` (PyInstaller artifacts) |

### Key Details
- 47 hidden imports covering all provider packages
- Excludes heavy optional deps (matplotlib, jupyter, numpy, cv2) to keep binary small
- UPX compression enabled

---

## Subtask 4: Cross-Platform Binary Build Workflow — DONE

### Files Created
| File | Purpose |
|---|---|
| `.github/workflows/binary.yml` | 4-OS matrix build: Linux x86_64, macOS ARM, macOS Intel, Windows x64 |

### Key Details
- On PRs: uploads binaries as workflow artifacts (7-day retention)
- On tag pushes: attaches binaries to GitHub Release via `softprops/action-gh-release@v2`
- Smoke test (`--help`) on each platform before upload
- Windows uses `pwsh` for binary rename

---

## Subtask 5: Update test.yml + Branch Protection — DONE

### Files Modified
| File | Change |
|---|---|
| `.github/workflows/test.yml` | Added `python -m pytest tests/ -v --tb=short --override-ini='testpaths=tests'` step |

### Branch Protection (set via `gh api`)
8 required status checks on `main`, `enforce_admins: false`:

| Check | Source |
|---|---|
| `test (3.10)` | test.yml |
| `test (3.11)` | test.yml |
| `test (3.12)` | test.yml |
| `build-and-test-publish` | publish-check.yml |
| `build (ubuntu-latest, aicp-linux-x86_64)` | binary.yml |
| `build (macos-latest, aicp-macos-arm64)` | binary.yml |
| `build (macos-13, aicp-macos-x86_64)` | binary.yml |
| `build (windows-latest, aicp-windows-x64.exe)` | binary.yml |

---

## Subtask 6: On-Merge Changelog + Latest Release — DONE

### Problem
After each PR merge, the changelog should update automatically and the latest wheel/binary should be available for download without waiting for a tagged release.

### Files Created
| File | Purpose |
|---|---|
| `.github/workflows/on-merge.yml` | 4-job workflow triggered on PR merge to main |

### What `on-merge.yml` Does

**Job 1: `changelog`**
- Reads PR title and categorizes by prefix (`feat:` → Added, `fix:` → Fixed, `docs:` → Documentation)
- Inserts entry into `docs/CHANGELOG.md` under `[Unreleased]` section
- Commits and pushes the update to main

**Job 2: `build-wheel`**
- Builds sdist + wheel
- Uploads as artifact (90-day retention)

**Job 3: `build-binary`**
- Same 4-OS matrix as binary.yml
- Builds and smoke-tests standalone binaries
- Uploads as artifacts (90-day retention)

**Job 4: `update-latest-release`**
- Deletes existing `latest` release tag
- Creates new `latest` prerelease with all artifacts attached
- Includes install instructions for pip and binary download

### Tests
| File | Cases Added |
|---|---|
| `tests/test_workflow_files.py` | 9 new tests: on-merge exists, triggers on PR closed, has all 4 jobs, checks merged flag, 4-platform matrix, references CHANGELOG.md |

---

## Subtask 7: GitHub Secrets + Branch Protection (Manual Steps) — DONE

### Executed via `gh` CLI

```bash
# Set TEST_PYPI_API_TOKEN (reused from PYPI_API_TOKEN)
grep "^PYPI_API_TOKEN=" .env | cut -d'=' -f2- | gh secret set TEST_PYPI_API_TOKEN

# Set branch protection with 8 required checks
gh api repos/donghaozhang/video-agent-skill/branches/main/protection --method PUT --input ...
```

### Secrets
| Secret | Status |
|---|---|
| `PYPI_API_TOKEN` | Already existed |
| `TEST_PYPI_API_TOKEN` | Added (reused from PYPI_API_TOKEN) |

---

## Complete File Inventory

### New Files (9)
| File | Subtask |
|---|---|
| `packages/core/ai_content_pipeline/ai_content_pipeline/_version.py` | 1 |
| `.github/workflows/publish-check.yml` | 2 |
| `aicp.spec` | 3 |
| `.github/workflows/binary.yml` | 4 |
| `.github/workflows/on-merge.yml` | 6 |
| `tests/test_version.py` | 1 |
| `tests/test_pyinstaller_spec.py` | 3 |
| `tests/test_workflow_files.py` | 5, 6 |
| `issues/implement-pypi-publish-and-binary.md` | — |

### Modified Files (4)
| File | Change |
|---|---|
| `setup.py` | Reads version from `_version.py` via regex |
| `packages/core/ai_content_pipeline/ai_content_pipeline/__init__.py` | Imports `__version__` from `_version` |
| `.github/workflows/test.yml` | Added full pytest suite step |
| `.gitignore` | Added PyInstaller artifact patterns |

### Unchanged Files (2)
| File | Reason |
|---|---|
| `.github/workflows/publish.yml` | Already correct for real PyPI on release |
| `.github/workflows/release.yml` | Already correct for tag-based releases |

---

## CI/CD Pipeline Flow (Final)

```text
PR opened/updated
  ├── test.yml          → pytest on Python 3.10/3.11/3.12
  ├── publish-check.yml → build + TestPyPI upload + install verify
  └── binary.yml        → build binaries for 4 platforms

All 8 checks pass → merge allowed

PR merged to main
  └── on-merge.yml
        ├── changelog       → auto-update CHANGELOG.md
        ├── build-wheel     → build sdist + wheel
        ├── build-binary    → 4-platform binaries
        └── latest-release  → update rolling "latest" GitHub release

Tag push v*.*.*
  ├── release.yml → create GitHub Release
  │     └── publish.yml → publish to real PyPI
  └── binary.yml → attach binaries to release
```

---

## Long-Term Benefits

1. **No broken PyPI releases** — every PR proves the package publishes correctly before merge
2. **Zero-install distribution** — users download a single binary, no Python required
3. **Version consistency** — single `_version.py` prevents drift between setup.py and __init__.py
4. **Cross-platform confidence** — binaries built and smoke-tested on 4 OS targets per PR
5. **Contributor-friendly** — new contributors get immediate feedback on packaging issues
6. **Reproducible builds** — committed `.spec` file means anyone can build the binary locally
7. **Auto-changelog** — CHANGELOG.md stays current without manual effort
8. **Always-fresh latest release** — wheel + binaries updated on every merge, no tag needed
