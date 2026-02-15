# Changelog

All notable changes to the AI Content Generation Suite.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.26] - 2026-02-15

### Added
- `set-key`, `get-key`, `check-keys`, `delete-key` CLI commands for credential management
- Persistent credential storage at `~/.config/video-ai-studio/credentials.env` (XDG-compliant)
- Automatic key injection into `os.environ` at CLI startup (`inject_keys()`)
- Security: hidden prompt input, `--stdin` for automation, `0o600` file permissions, masked output

## [1.0.24] - 2026-02-10

### Added
- Native structured output for LLM calls via `chat_with_structured_output` (Pydantic schemas)
- Character portrait registry for cross-scene visual consistency
- Per-chapter output folders with meaningful file names
- `ChapterCompressionResponse` and `ShotResponse` Pydantic schemas for pipeline agents

### Changed
- Documentation overhaul: slimmed README (352→210 lines), updated models reference to 73 models
- CLAUDE.md slimmed (407→259 lines), fixed test count and version references

### Fixed
- CI test failures: added `HAS_VIMAX` skip guard for optional `rich` dependency
- `ShotResponse` missing `characters` field for portrait reference resolution

## [1.0.23] - 2026-02-06

### Added
- Click-based CLI migration: all commands now use Click framework
- ViMax integration as `aicp vimax` subgroup (novel-to-video pipelines)
- Auto-discovery of subpackages in setup.py for correct PyPI distribution

### Fixed
- Package build for ai_content_platform
- Reference image path validation to prevent arbitrary file reads

## [1.0.21] - 2026-01-30

### Added
- Unix-style CLI flags: `--json`, `--quiet`, `--stream`, `--input` for scripting and CI
- CLI exit codes module with stable, documented exit codes
- XDG paths module for cross-platform config/cache/state directories
- CLI output, interactive, and streaming modules
- Cross-platform binary builds via PyInstaller (Linux, macOS ARM64/x86_64, Windows)
- Pre-merge PyPI publishing and on-merge changelog/wheel/binary workflows

### Changed
- Migrated provider CLIs from argparse to Click
- Central model registry now single source of truth for all 73 models

### Fixed
- StreamEmitter default param binding for pytest capture
- PyInstaller entry point and hidden imports
- CI workflow runner (macos-13 retired, switched to macos-15-intel)
- Script injection prevention in on-merge.yml release notes

## [1.0.19] - 2026-01-25

### Added
- ViMax integration package for novel-to-video pipeline
- Kling Video v3 Standard and Pro models (text-to-video)
- Kling O3 (Omni 3) models with element-based character/object consistency
- xAI Grok Imagine Video model (text-to-video and image-to-video with audio)
- xAI Grok Video Edit model for avatar-generation
- Central model registry (`registry.py` + `registry_data.py`) replacing scattered constants
- MODEL_KEY class attributes for auto-discovery across all generators
- Project structure CLI commands (`init-project`, `organize-project`, `structure-info`)
- Output folder organization with categorized subfolders
- Automated release workflow with bump2version

### Changed
- Model registration reduced from 60+ file edits to 2 files
- Expanded Kling v3 duration range to 3-15 seconds

### Fixed
- Various code review findings (docstrings, type hints, error handling)

## [1.0.18] - 2026-01-21

### Added
- Automated PyPI publishing via GitHub Actions
- Comprehensive documentation structure
- Ralph-loop plugin for iterative development

### Changed
- Consolidated setup files for cleaner package structure
- Improved CI/CD workflow with skip-existing option

### Fixed
- Repository URL updates

## [1.0.17] - 2026-01-20

### Added
- PyPI release preparation
- Package metadata updates

### Changed
- Updated repository URLs

## [1.0.16] - 2026-01-19

### Added
- Sora 2 and Sora 2 Pro models
- Kling v2.6 Pro model
- Wan v2.6 model with multi-shot support
- Text-to-video direct generation

### Changed
- Expanded model pricing documentation
