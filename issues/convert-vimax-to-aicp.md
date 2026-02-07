# Convert Entire CLI to Click + Integrate ViMax as Subgroup

## Status: Pending

## Overview

Migrate the entire `aicp` CLI from argparse to Click, then integrate the `vimax` CLI as a native Click subgroup. This gives a unified, composable CLI framework with consistent behavior across all commands.

**Current state:**
- `aicp` uses **argparse** with 20+ flat subcommands in a single 1057-line `__main__.py`
- `vimax` uses **Click** with a nested group (10 commands in `vimax/cli/commands.py`)
- Both are registered as separate console scripts in `setup.py`
- Handler functions take `(args, output)` where `args` is an argparse `Namespace`
- Command dispatch is a 40-line if/elif chain (lines 1013-1053)

**Target state:**
- Single Click-based `aicp` CLI replacing all argparse code
- Commands organized into logical modules under `cli/commands/` (each <500 lines)
- `CLIOutput` threaded via `click.pass_obj` context
- Vimax integrated as a native Click subgroup: `aicp vimax idea2video`
- Standalone `vimax` console script removed
- `aicp_entry.py` PyInstaller wrapper preserved
- All existing global flags preserved: `--json`, `--quiet`, `--debug`, `--config-dir`, `--cache-dir`, `--state-dir`

**Why all-Click (not hybrid bridge):**
- Click already a dependency (`click>=8.0.0` in `setup.py` line 58)
- Click's `CliRunner` makes testing 10x easier than subprocess-based argparse tests
- Native subgroup nesting (vimax) without fragile argparse `REMAINDER` delegation
- Built-in type validation, help formatting, and shell completion
- Consistent developer experience across all commands
- No hybrid bridge maintenance burden long-term

## Architecture

```
cli/
  click_app.py          # Root @click.group(), global options, CLIOutput context
  commands/
    __init__.py          # Register all command groups
    pipeline.py          # list-models, setup, generate-image, create-video, run-chain, create-examples
    media.py             # generate-avatar, list-avatar-models, analyze-video, list-video-models
    motion.py            # transfer-motion, list-motion-models
    audio.py             # transcribe, list-speech-models
    imaging.py           # generate-grid, upscale-image
    project.py           # init-project, organize-project, structure-info
```

Vimax stays in its existing location (`ai_content_platform/vimax/cli/commands.py`) and is added as a subgroup via `cli.add_command(vimax)`.

## Subtasks

### Subtask 1: Create Click root group with global options and CLIOutput context (~15 min)

**Problem:** The current CLI uses argparse for parsing and manually constructs `CLIOutput` after parsing. We need a Click group that handles global options and provides `CLIOutput` through Click's context system.

**Files to create:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/click_app.py`

**Implementation:**
1. Create root `@click.group()` named `cli` with epilog examples
2. Add global options as group-level Click options:
   - `--debug` (flag)
   - `--json` (flag)
   - `--quiet / -q` (flag)
   - `--base-dir` (string, default ".")
   - `--config-dir` (string)
   - `--cache-dir` (string)
   - `--state-dir` (string)
3. In the group callback, apply XDG env var overrides (`os.environ["XDG_CONFIG_HOME"]`, etc.)
4. Create `CLIOutput` instance and store in `ctx.obj`
5. Export `cli` for use by `__main__.py`

**Key pattern — passing CLIOutput to commands:**
```python
@click.group()
@click.option("--json", "json_mode", is_flag=True, help="Emit machine-readable JSON to stdout")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.option("--base-dir", default=".", help="Base directory for operations")
@click.option("--config-dir", default=None, help="Override config directory")
@click.option("--cache-dir", default=None, help="Override cache directory")
@click.option("--state-dir", default=None, help="Override state directory")
@click.pass_context
def cli(ctx, json_mode, quiet, debug, base_dir, config_dir, cache_dir, state_dir):
    ctx.ensure_object(dict)
    # Apply XDG overrides
    if config_dir:
        os.environ["XDG_CONFIG_HOME"] = config_dir
    if cache_dir:
        os.environ["XDG_CACHE_HOME"] = cache_dir
    if state_dir:
        os.environ["XDG_STATE_HOME"] = state_dir
    # Store shared state
    ctx.obj["output"] = CLIOutput(json_mode=json_mode, quiet=quiet, debug=debug)
    ctx.obj["base_dir"] = base_dir
    ctx.obj["json_mode"] = json_mode
    ctx.obj["quiet"] = quiet
    ctx.obj["debug"] = debug
```

**Test file:** `tests/test_click_app.py`
- Test `aicp --help` shows global options
- Test `CLIOutput` is created with correct flags
- Test XDG env vars are set when --config-dir/--cache-dir/--state-dir provided

---

### Subtask 2: Convert core pipeline commands to Click (~30 min)

**Problem:** 6 core commands (list-models, setup, generate-image, create-video, run-chain, create-examples) need to move from argparse handlers to Click commands.

**Files to create:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/__init__.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/pipeline.py`

**Commands to convert:**

| Command | Current handler | Key options |
|---------|----------------|-------------|
| `list-models` | `print_models(output)` | (none) |
| `setup` | `setup_env(args, output)` | `--output-dir` |
| `generate-image` | `generate_image(args, output)` | `--text`, `--model`, `--aspect-ratio`, `--resolution`, `--input`, `--output-dir`, `--save-json` |
| `create-video` | `create_video(args, output)` | `--text`, `--image-model`, `--video-model`, `--input`, `--output-dir`, `--save-json` |
| `run-chain` | `run_chain(args, output)` | `--config`, `--input-text`, `--prompt-file`, `--input`, `--no-confirm`, `--stream`, `--save-json` |
| `create-examples` | `create_examples(args, output)` | `--output-dir` |

**Implementation pattern — each command uses `@click.pass_context`:**
```python
@click.command("list-models")
@click.pass_context
def list_models_cmd(ctx):
    """List all available models."""
    output = ctx.obj["output"]
    print_models(output)
```

**Notes:**
- Keep the existing handler function bodies (`print_models`, `create_video`, etc.) — only change how args are received
- The `--save-json` flag emits a deprecation warning via `_check_save_json_deprecation()` — preserve this
- The `--input` option uses `read_input()` from `cli/output.py` — preserve this
- `run-chain` uses `StreamEmitter` from `cli/stream.py` — preserve this
- Register all commands in `__init__.py` via a `register_pipeline_commands(cli)` function

**Test file:** `tests/test_click_pipeline_commands.py`
- Test each command's `--help` output
- Test `list-models` runs without error
- Test `generate-image` requires `--text`
- Test `create-video` requires `--text`
- Test `run-chain` requires `--config`

---

### Subtask 3: Convert media commands to Click (~25 min)

**Problem:** 4 media commands need to move from argparse to Click.

**Files to create:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/media.py`

**Commands to convert:**

| Command | Current handler | Key options |
|---------|----------------|-------------|
| `generate-avatar` | `generate_avatar(args, output)` | `--image-url`, `--audio-url`, `--text`, `--video-url`, `--reference-images`, `--prompt`, `--model`, `--duration`, `--aspect-ratio`, `--save-json` |
| `list-avatar-models` | `list_avatar_models(args, output)` | (none) |
| `analyze-video` | `analyze_video_command(args)` | `-i/--input`, `-o/--output`, `-m/--model`, `-t/--type`, `-f/--format` |
| `list-video-models` | `list_video_models()` | (none) |

**Notes:**
- `analyze-video` and `list-video-models` currently don't use `CLIOutput` (they use their own print logic from `video_analysis.py`). Keep as-is for now; they can be migrated to `CLIOutput` in a future cleanup.
- `generate-avatar` checks `FAL_AVATAR_AVAILABLE` at runtime — preserve this guard.
- `--reference-images` uses `nargs="+"` in argparse; in Click use `multiple=True`.
- Register via `register_media_commands(cli)`.

**Test file:** `tests/test_click_media_commands.py`
- Test `generate-avatar --help` shows all options
- Test `list-avatar-models` help
- Test `analyze-video` requires `-i/--input`

---

### Subtask 4: Convert motion + audio commands to Click (~20 min)

**Problem:** 4 commands (transfer-motion, list-motion-models, transcribe, list-speech-models) need conversion.

**Files to create:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/motion.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/audio.py`

**Commands to convert:**

| Command | Current handler | Key options |
|---------|----------------|-------------|
| `transfer-motion` | `transfer_motion_command(args)` | `-i/--image`, `-v/--video`, `-o/--output`, `--orientation`, `--no-sound`, `-p/--prompt`, `--save-json` |
| `list-motion-models` | `list_motion_models()` | (none) |
| `transcribe` | `transcribe_command(args)` | `-i/--input`, `-o/--output`, `--language`, `--diarize/--no-diarize`, `--tag-events/--no-tag-events`, `--keyterms`, `--save-json`, `--raw-json`, `--srt`, `--srt-max-words`, `--srt-max-duration` |
| `list-speech-models` | `list_speech_models()` | (none) |

**Notes:**
- `transfer-motion` and `transcribe` currently don't use `CLIOutput` (they have their own print logic). Keep their handler functions unchanged; Click only changes how args are received.
- `--diarize/--no-diarize` maps naturally to Click's boolean flag pairs.
- `--keyterms` uses `nargs="+"` in argparse; in Click use `multiple=True`.
- `--orientation` has `choices` — use `click.Choice()`.
- Register via `register_motion_commands(cli)` and `register_audio_commands(cli)`.

**Test file:** `tests/test_click_motion_audio_commands.py`
- Test `transfer-motion` requires `-i` and `-v`
- Test `transcribe` requires `-i/--input`
- Test `--orientation` validates choices

---

### Subtask 5: Convert imaging + project commands to Click (~15 min)

**Problem:** 5 utility commands need conversion.

**Files to create:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/imaging.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/project.py`

**Commands to convert:**

| Command | Current handler | Key options |
|---------|----------------|-------------|
| `generate-grid` | `generate_grid_command(args)` | `--prompt-file/-f`, `--grid/-g`, `--style/-s`, `--model/-m`, `--upscale`, `-o/--output`, `--save-json` |
| `upscale-image` | `upscale_image_command(args)` | `-i/--input`, `--factor`, `--target`, `--format`, `-o/--output`, `--save-json` |
| `init-project` | `init_project_command(args)` | `-d/--directory`, `--dry-run` |
| `organize-project` | `organize_project_command(args)` | `-d/--directory`, `-s/--source`, `--dry-run`, `-r/--recursive`, `--include-output` |
| `structure-info` | `structure_info_command(args)` | `-d/--directory` |

**Notes:**
- These handlers currently take raw `args` Namespace and do their own output. Minimal changes needed — just wrap with Click decorators.
- `--grid` has `choices` from `GRID_CONFIGS.keys()` — use `click.Choice()`.
- `--target` has `choices` from `UPSCALE_TARGETS` — use `click.Choice()`.
- `--format` has `choices` — use `click.Choice()`.
- Register via `register_imaging_commands(cli)` and `register_project_commands(cli)`.

**Test file:** `tests/test_click_utility_commands.py`
- Test `generate-grid` requires `--prompt-file/-f`
- Test `upscale-image` requires `-i/--input`
- Test `init-project` default directory is "."

---

### Subtask 6: Wire everything in `__main__.py` and integrate vimax subgroup (~15 min)

**Problem:** Replace the 1057-line argparse `__main__.py` with a thin wrapper that imports the Click CLI and registers all command groups including vimax.

**Files to modify:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` (rewrite)

**Implementation:**
1. Remove all argparse code (parser setup, subparsers, if/elif dispatch)
2. Keep existing handler functions (`print_models`, `setup_env`, `create_video`, `run_chain`, `generate_image`, `create_examples`, `generate_avatar`, `list_avatar_models`) — move them to the respective `cli/commands/*.py` files or import them there
3. Import `cli` from `cli/click_app.py`
4. Import command registration functions from `cli/commands/`
5. Import and register vimax Click group:
   ```python
   from ai_content_platform.vimax.cli.commands import vimax
   cli.add_command(vimax)
   ```
6. Define `main()` as:
   ```python
   def main():
       from .cli.click_app import cli
       cli()
   ```
7. Keep `if __name__ == "__main__": main()` for `python -m` invocation

**New `__main__.py` structure (~30 lines):**
```python
"""AI Content Pipeline CLI Interface."""
from .cli.click_app import cli
from .cli.commands import register_all_commands

# Register all command groups
register_all_commands(cli)

# Register vimax as subgroup
try:
    from ai_content_platform.vimax.cli.commands import vimax
    cli.add_command(vimax)
except ImportError:
    pass  # vimax not installed

def main():
    cli()

if __name__ == "__main__":
    main()
```

**Notes:**
- `aicp_entry.py` continues to call `from ai_content_pipeline.__main__ import main; main()` — no changes needed
- The vimax import is wrapped in try/except so the CLI works even if `ai_content_platform` is not installed
- Handler function bodies (the actual logic) move into `cli/commands/*.py` files, not left in `__main__.py`

**Test file:** `tests/test_click_app.py` (extend)
- Test `aicp --help` shows all command groups
- Test `aicp vimax --help` shows vimax subcommands
- Test `aicp vimax idea2video --help` shows idea2video options

---

### Subtask 7: Remove standalone vimax console script (~5 min)

**Problem:** After integration, the standalone `vimax` entry point is redundant.

**Files to modify:**
- `setup.py` (line 229) — remove `"vimax=packages.core.ai_content_platform.vimax.cli.commands:main"`
- `vimax.bat` — delete this file

**Implementation:**
1. Remove the `vimax` entry from `console_scripts` in `setup.py`
2. Delete `vimax.bat` at project root
3. Keep the `vimax` Click group and `register_commands()` function in `commands.py` — still used by Click subgroup registration

**Test file:** `tests/test_click_app.py`
- Test that `vimax` is NOT in console_scripts (parse setup.py)

---

### Subtask 8: Update vimax CLI help text and internal references (~10 min)

**Problem:** Vimax command help strings and docstrings reference `vimax <command>` — they should say `aicp vimax <command>`.

**Files to modify:**
- `packages/core/ai_content_platform/vimax/cli/commands.py` (lines 18-634)
- `packages/core/ai_content_platform/vimax/__init__.py`
- `packages/core/ai_content_platform/vimax/cli/__init__.py`
- `packages/core/ai_content_platform/vimax/README.md`

**Implementation:**
1. Update the vimax Click group docstring from standalone to subcommand context
2. Update all command docstrings: `vimax idea2video` -> `aicp vimax idea2video`
3. Update the `list-models` command output header
4. Update module docstrings in `__init__.py` files
5. Update README.md examples

**Test file:** `tests/unit/vimax/test_cli.py` (update)
- Update help text assertions to expect `aicp vimax`

---

### Subtask 9: Update PyInstaller spec and documentation (~15 min)

**Problem:** `aicp.spec` needs vimax modules and `click` in hiddenimports. Documentation references standalone `vimax` and argparse-style usage.

**Files to modify:**
- `aicp.spec` (hiddenimports list)
- `docs/vimax-cli.md` -> rename to `docs/aicp-vimax-commands.md`
- `CLAUDE.md`
- `README.md`

**Implementation (PyInstaller):**
1. Add vimax-related hidden imports:
   ```
   'ai_content_platform.vimax',
   'ai_content_platform.vimax.cli',
   'ai_content_platform.vimax.cli.commands',
   'ai_content_platform.vimax.agents',
   'ai_content_platform.vimax.adapters',
   'ai_content_platform.vimax.interfaces',
   'ai_content_platform.vimax.pipelines',
   ```
2. Add `click` to third-party hidden imports
3. Add new CLI modules:
   ```
   'ai_content_pipeline.cli.click_app',
   'ai_content_pipeline.cli.commands',
   'ai_content_pipeline.cli.commands.pipeline',
   'ai_content_pipeline.cli.commands.media',
   'ai_content_pipeline.cli.commands.motion',
   'ai_content_pipeline.cli.commands.audio',
   'ai_content_pipeline.cli.commands.imaging',
   'ai_content_pipeline.cli.commands.project',
   ```

**Implementation (Documentation):**
1. Rename `docs/vimax-cli.md` -> `docs/aicp-vimax-commands.md`, update all examples
2. Update CLAUDE.md: remove `vimax` from standalone console commands, add `aicp vimax` subcommand group
3. Update README.md vimax references

**Test file:** `tests/test_pyinstaller_spec.py` (update)
- Check for vimax modules in hiddenimports
- Check for `click` in hiddenimports
- Check for new CLI command modules

---

### Subtask 10: Write and update tests (~20 min)

**Problem:** Existing tests use argparse-style invocation or mock vimax groups. Need to update for Click.

**Files to create/modify:**
- `tests/test_click_app.py` (new) — Root CLI tests
- `tests/test_click_pipeline_commands.py` (new) — Pipeline command tests
- `tests/test_click_media_commands.py` (new) — Media command tests
- `tests/test_click_motion_audio_commands.py` (new) — Motion + audio command tests
- `tests/test_click_utility_commands.py` (new) — Imaging + project command tests
- `tests/unit/vimax/test_cli.py` (update) — Update vimax CLI tests
- `tests/test_main_cli_flags.py` (update) — Update to use Click CliRunner

**Implementation:**
1. All new tests use `click.testing.CliRunner` for invocation
2. Test pattern:
   ```python
   from click.testing import CliRunner
   from ai_content_pipeline.cli.click_app import cli

   def test_help():
       runner = CliRunner()
       result = runner.invoke(cli, ["--help"])
       assert result.exit_code == 0
       assert "list-models" in result.output
   ```
3. Update `test_main_cli_flags.py` to invoke via Click instead of argparse
4. Update vimax test assertions for `aicp vimax` help text
5. Test global options propagation: `--json`, `--quiet`, `--debug` affect CLIOutput

---

## Dependency Order

```
Subtask 1 (Click root group)
    |
Subtask 2 (pipeline commands) ----+
Subtask 3 (media commands)    ----+-- can run in parallel
Subtask 4 (motion + audio)   ----+
Subtask 5 (imaging + project) ---+
    |
Subtask 6 (wire __main__.py + vimax subgroup) <- depends on 1-5
    |
Subtask 7 (remove standalone vimax) <- depends on 6
Subtask 8 (update vimax help text)  <- depends on 6
    |
Subtask 9 (PyInstaller + docs) <- after all code changes
Subtask 10 (tests) <- after all code changes
```

## Files Summary

| File | Action |
|------|--------|
| `cli/click_app.py` | **New** — Root Click group with global options |
| `cli/commands/__init__.py` | **New** — Command registration hub |
| `cli/commands/pipeline.py` | **New** — list-models, setup, generate-image, create-video, run-chain, create-examples |
| `cli/commands/media.py` | **New** — generate-avatar, list-avatar-models, analyze-video, list-video-models |
| `cli/commands/motion.py` | **New** — transfer-motion, list-motion-models |
| `cli/commands/audio.py` | **New** — transcribe, list-speech-models |
| `cli/commands/imaging.py` | **New** — generate-grid, upscale-image |
| `cli/commands/project.py` | **New** — init-project, organize-project, structure-info |
| `__main__.py` | **Rewrite** — Thin wrapper importing Click CLI |
| `setup.py` | Remove vimax console_script |
| `vimax.bat` | **Delete** |
| `vimax/cli/commands.py` | Update help text to `aicp vimax` |
| `vimax/__init__.py` | Update docstrings |
| `vimax/cli/__init__.py` | Update docstrings |
| `vimax/README.md` | Update examples |
| `docs/vimax-cli.md` | **Rename** to `docs/aicp-vimax-commands.md` + update |
| `CLAUDE.md` | Update vimax + CLI references |
| `README.md` | Update vimax references |
| `aicp.spec` | Add vimax + click + new CLI modules to hiddenimports |
| `tests/test_click_app.py` | **New** — Root CLI tests |
| `tests/test_click_pipeline_commands.py` | **New** — Pipeline command tests |
| `tests/test_click_media_commands.py` | **New** — Media command tests |
| `tests/test_click_motion_audio_commands.py` | **New** — Motion + audio tests |
| `tests/test_click_utility_commands.py` | **New** — Imaging + project tests |
| `tests/unit/vimax/test_cli.py` | Update assertions |
| `tests/test_main_cli_flags.py` | Update to Click CliRunner |
| `tests/test_pyinstaller_spec.py` | Update hidden import checks |

**All paths are relative to `packages/core/ai_content_pipeline/ai_content_pipeline/` unless noted otherwise.**

## Estimated Total Time: ~170 minutes

## Risks

- **Handler function migration**: The 6 handler functions in `__main__.py` (`print_models`, `setup_env`, `generate_image`, `create_video`, `run_chain`, `create_examples`, `generate_avatar`, `list_avatar_models`) need to be moved to `cli/commands/*.py` files. These functions reference `CLIOutput`, `read_input()`, `_check_save_json_deprecation()`, `confirm()`, `error_exit()`, and `StreamEmitter`. All of these are already in the `cli/` package, so imports are straightforward.
- **Commands that bypass CLIOutput**: `analyze_video_command`, `transfer_motion_command`, `transcribe_command`, `generate_grid_command`, `upscale_image_command`, `init_project_command`, `organize_project_command`, `structure_info_command` all do their own printing. These are wrapped with Click decorators but their internals stay unchanged — they receive a Click-compatible args object.
- **Args namespace compatibility**: Some handler functions access `args.foo` directly. In Click, params are passed as function kwargs. For handlers that haven't been refactored to take explicit kwargs, we may need a thin adapter. The cleanest approach is to refactor each handler to take explicit params.
- **Binary size**: Adding vimax modules to the PyInstaller bundle increases binary size. Acceptable since vimax is a core feature.
- **Async commands**: vimax uses `asyncio.run()`. This works fine from Click since Click doesn't interfere with event loops.
- **Existing test breakage**: `test_main_cli_flags.py` tests argparse behavior. These need to be updated to use Click CliRunner. The tests for `--json`, `--quiet`, `--debug`, `--config-dir`, `--cache-dir`, `--state-dir` should all still pass with Click — just the invocation method changes.
