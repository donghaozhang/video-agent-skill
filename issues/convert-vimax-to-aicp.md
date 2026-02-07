# Convert Entire CLI to Click + Integrate ViMax as Subgroup

## Status: Implemented

**Branch:** `feat/unix-linux-style-framework-migration`
**PR:** #22
**Commit:** `fcfc2b1` — feat: Migrate CLI from argparse to Click, integrate vimax as subgroup

## Overview

Migrated the entire `aicp` CLI from argparse to Click and integrated the `vimax` CLI as a native Click subgroup. This gives a unified, composable CLI framework with consistent behavior across all commands.

**Before:**
- `aicp` used **argparse** with 20+ flat subcommands in a single 1057-line `__main__.py`
- `vimax` used **Click** with a nested group (10 commands in `vimax/cli/commands.py`)
- Both were registered as separate console scripts in `setup.py`
- Handler functions took `(args, output)` where `args` was an argparse `Namespace`
- Command dispatch was a 40-line if/elif chain

**After:**
- Single Click-based `aicp` CLI replacing all argparse code
- Commands organized into 6 logical modules under `cli/commands/` (each <500 lines)
- `CLIOutput` threaded via `click.pass_context` / `ctx.obj`
- Vimax integrated as a native Click subgroup: `aicp vimax idea2video`
- Standalone `vimax` console script removed
- `__main__.py` reduced from 1057 lines to 17 lines
- All commands auto-registered at import time in `click_app.py`

## Architecture (Implemented)

```
cli/
  click_app.py          # Root @click.group(), global options, CLIOutput context, import-time registration
  commands/
    __init__.py          # register_all_commands() hub
    pipeline.py          # list-models, setup, generate-image, create-video, run-chain, create-examples
    media.py             # generate-avatar, list-avatar-models, analyze-video, list-video-models
    motion.py            # transfer-motion, list-motion-models
    audio.py             # transcribe, list-speech-models
    imaging.py           # generate-grid, upscale-image
    project.py           # init-project, organize-project, structure-info
```

Vimax stays in its existing location (`ai_content_platform/vimax/cli/commands.py`) and is registered as a subgroup via `cli.add_command(vimax)` in `click_app.py`.

## Subtask Results

### Subtask 1: Create Click root group with global options — DONE

**File created:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/click_app.py`

- Root `@click.group(invoke_without_command=True)` named `cli`
- Global options: `--json`, `--quiet/-q`, `--debug`, `--base-dir`, `--config-dir`, `--cache-dir`, `--state-dir`
- XDG env var overrides applied in group callback
- `CLIOutput` created and stored in `ctx.obj["output"]`
- Shows help and exits 0 when invoked without a subcommand
- All commands and vimax subgroup registered at module import time

---

### Subtask 2: Convert core pipeline commands to Click — DONE

**File created:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/pipeline.py`
**File created:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/__init__.py`

6 commands converted:
- `list-models` — calls `print_models(output)`
- `setup` — calls `setup_env(args, output)` with SimpleNamespace bridge
- `generate-image` — full Click implementation with `--text`, `--model`, `--aspect-ratio`, `--resolution`, `--input`, `--output-dir`, `--save-json`
- `create-video` — full Click implementation with `--text`, `--image-model`, `--video-model`, `--input`, `--output-dir`, `--save-json`
- `run-chain` — full Click implementation with `--config`, `--input-text`, `--prompt-file`, `--input`, `--no-confirm`, `--stream`, `--save-json`
- `create-examples` — calls `create_examples(args, output)`

Includes `_check_save_json_deprecation(save_json, output)` helper for backward compatibility.

---

### Subtask 3: Convert media commands to Click — DONE

**File created:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/media.py`

4 commands converted:
- `generate-avatar` — full Click implementation, `--reference-images` uses `multiple=True`
- `list-avatar-models` — calls `list_avatar_models(args, output)`
- `analyze-video` — uses `SimpleNamespace` bridge to call `analyze_video_command(args)`
- `list-video-models` — calls `list_video_models()`

---

### Subtask 4: Convert motion + audio commands to Click — DONE

**File created:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/motion.py`
**File created:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/audio.py`

4 commands converted:
- `transfer-motion` — uses `SimpleNamespace` bridge, `--orientation` with `click.Choice()`
- `list-motion-models` — calls `list_motion_models()`
- `transcribe` — uses `SimpleNamespace` bridge, `--keyterms` uses `multiple=True`, `--diarize/--no-diarize` boolean flag
- `list-speech-models` — calls `list_speech_models()`

---

### Subtask 5: Convert imaging + project commands to Click — DONE

**File created:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/imaging.py`
**File created:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/project.py`

5 commands converted:
- `generate-grid` — uses `SimpleNamespace` bridge
- `upscale-image` — uses `SimpleNamespace` bridge
- `init-project` — uses `SimpleNamespace` bridge
- `organize-project` — uses `SimpleNamespace` bridge
- `structure-info` — uses `SimpleNamespace` bridge

---

### Subtask 6: Wire everything in `__main__.py` and integrate vimax — DONE

**File rewritten:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` (1057 lines → 17 lines)

Command registration moved to `click_app.py` at module level (not `__main__.py`) so that `from cli.click_app import cli` always returns a fully-populated group. This is critical for test reliability.

---

### Subtask 7: Remove standalone vimax console script — DONE

**File modified:** `setup.py` — removed `vimax=` from `console_scripts`
**File deleted:** `vimax.bat`

---

### Subtask 8: Update vimax CLI help text — DONE

**Files modified:**
- `packages/core/ai_content_platform/vimax/cli/commands.py` — docstrings updated to `aicp vimax <command>`
- `packages/core/ai_content_platform/vimax/__init__.py` — module docstring updated
- `packages/core/ai_content_platform/vimax/cli/__init__.py` — module docstring updated

---

### Subtask 9: Update PyInstaller spec and documentation — DONE

**File modified:** `aicp.spec` — added `click_app`, 6 command modules, vimax platform modules, `click` to hiddenimports
**File renamed:** `docs/vimax-cli.md` → `docs/aicp-vimax-commands.md` — all `vimax` references updated to `aicp vimax`
**File modified:** `CLAUDE.md` — updated 3 references from standalone `vimax` to `aicp vimax` subgroup

---

### Subtask 10: Write and update tests — DONE

**File created:** `tests/test_click_app.py` (43 tests)
- TestRootGroup: help exit code, description, global options, short flag, all commands visible, no-command help
- TestVimaxSubgroup: vimax help, idea2video help, idea2video requires --idea, generate-storyboard help, list-models
- TestCommandHelp: parametrized `--help` for all 19 commands
- TestRequiredOptions: 8 tests validating required option enforcement
- TestSetupPyVimax: vimax not in console_scripts
- TestPyInstallerSpec: spec includes click_app, command modules, vimax modules, click

**File rewritten:** `tests/test_main_cli_flags.py` (33 tests)
- Converted from argparse `_build_parser()` to Click `CliRunner`
- Updated `_check_save_json_deprecation` import from `__main__` to `cli.commands.pipeline`
- TestGlobalFlags, TestDirOverrideWiring, TestCLIOutputCreation, TestOutputRouting, TestInputFlag, TestStreamFlag, TestQuietMode, TestSaveJsonDeprecation

## Test Results

```
tests/test_click_app.py:        43/43 PASSED
tests/test_main_cli_flags.py:   33/33 PASSED
tests/test_pyinstaller_spec.py:  7/7  PASSED
Full suite:                     795/796 PASSED (1 pre-existing Windows cp1252 failure)
```

## Files Summary

| File | Action | Lines |
|------|--------|-------|
| `cli/click_app.py` | **Created** | 78 |
| `cli/commands/__init__.py` | **Created** | 23 |
| `cli/commands/pipeline.py` | **Created** | ~300 |
| `cli/commands/media.py` | **Created** | ~200 |
| `cli/commands/motion.py` | **Created** | ~80 |
| `cli/commands/audio.py` | **Created** | ~120 |
| `cli/commands/imaging.py` | **Created** | ~80 |
| `cli/commands/project.py` | **Created** | ~80 |
| `__main__.py` | **Rewritten** | 17 (was 1057) |
| `setup.py` | Modified | removed vimax console_script |
| `vimax.bat` | **Deleted** | — |
| `vimax/cli/commands.py` | Modified | updated help text |
| `vimax/__init__.py` | Modified | updated docstrings |
| `vimax/cli/__init__.py` | Modified | updated docstrings |
| `docs/aicp-vimax-commands.md` | **Renamed** from `vimax-cli.md` + updated |
| `CLAUDE.md` | Modified | updated vimax references |
| `aicp.spec` | Modified | added hiddenimports |
| `tests/test_click_app.py` | **Created** | 221 (43 tests) |
| `tests/test_main_cli_flags.py` | **Rewritten** | 326 (33 tests) |

**All paths relative to `packages/core/ai_content_pipeline/ai_content_pipeline/` unless noted.**

## Key Design Decisions

1. **Import-time registration** in `click_app.py` (not `__main__.py`) — ensures `from cli.click_app import cli` always returns fully-populated group. Critical for test reliability with Click's `CliRunner`.

2. **`SimpleNamespace` bridge** for external handlers — commands like `analyze-video`, `transfer-motion`, `transcribe` use handler functions that expect `args.foo` attribute access. Rather than refactoring all handlers, Click kwargs are wrapped in `types.SimpleNamespace` for compatibility.

3. **`invoke_without_command=True`** on root group — `aicp` with no args shows help and exits 0 (user-friendly behavior).

4. **Vimax optional dependency** — `cli.add_command(vimax)` wrapped in `try/except ImportError` so the CLI works even if `ai_content_platform` is not installed.
