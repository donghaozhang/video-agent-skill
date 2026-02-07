# Implementation Plan: Unix/Linux Style Framework Migration

**Status**: COMPLETED (Phase 1 — core modules, tests, and foundational wiring)
**PR**: [#20](https://github.com/donghaozhang/video-agent-skill/pull/20)
**Issue**: [framework-unix-linux-style-migration.md](framework-unix-linux-style-migration.md)
**Branch**: `feat/unix-linux-style-framework-migration`
**Estimated Total Effort**: ~4-5 hours across 6 subtasks
**Approach**: Long-term maintainability over quick wins. Each subtask is a separate PR-ready commit.

---

## Architecture Overview (Current State)

| Component | Framework | Entry Point | Lines |
|-----------|-----------|-------------|-------|
| `ai-content-pipeline` / `aicp` | argparse | `__main__.py:main` | 1010 |
| `fal-text-to-video` | Click | `fal_text_to_video/cli.py` | 195 |
| `fal-image-to-video` | Click | `fal_image_to_video/cli.py` | 198 |
| `vimax` | Click | `vimax/cli/commands.py` | 597 |
| `ai-content-platform` | Click | `cli/main.py` | 286 |

**Key Problems** (verified against codebase 2026-02-07):
1. JSON output only via `--save-json FILENAME` (writes to file, not stdout). Exception: `cli/commands.py:220` has `--format json` for `cost` command only.
2. Exit codes are only `0` and `1` (no semantic differentiation)
3. Error messages go to stdout via `print()` (not stderr) — in `__main__.py`, `executor.py` (~15 print calls), `manager.py:56`, `video_analysis.py:56`
4. `--no-confirm` exists (`__main__.py:635`) but defaults to `True` (skips by default). `setup_env()` at line 122 still uses raw `input()`. `cli/commands.py:97` uses `click.confirm()`.
5. No stdin support for piping
6. No XDG path conventions
7. Mixed argparse/Click across packages
8. `executor.py` has ~15 `print()` statements that would corrupt `--json` stdout output
9. `manager.py:56` prints `"✅ AI Pipeline Manager initialized"` to stdout on every instantiation

---

## Subtask Overview

| # | Subtask | Status | Tests | Notes |
|---|---------|--------|-------|-------|
| 1 | [Exit Codes & Error Model](subtask-1-exit-codes.md) | DONE | 27 | `cli/exit_codes.py` + `__main__.py` + provider CLIs |
| 2 | [JSON Output & --quiet/--debug](subtask-2-json-output.md) | DONE | 17 | `cli/output.py` CLIOutput class; flag wiring is follow-up |
| 3 | [Stdin/Stdout First](subtask-3-stdin-stdout.md) | DONE | 8 | `read_input()` helper; `--input` flag wiring is follow-up |
| 4 | [Non-Interactive Mode](subtask-4-non-interactive.md) | DONE | 14 | `cli/interactive.py`; fixed `--no-confirm` default bug |
| 5 | [XDG Config/Cache/State Paths](subtask-5-xdg-paths.md) | DONE | 16 | `cli/paths.py`; CLI flag wiring is follow-up |
| 6 | [Stream-Friendly Pipeline](subtask-6-streaming.md) | DONE | 9 | `cli/stream.py`; executor integration is follow-up |
| | **Total** | **6/6** | **91** | |

---

## Subtask 1: Exit Codes & Error Model

**Goal**: Replace blanket `sys.exit(1)` with semantic exit codes. Route errors to stderr. Stack traces only in `--debug`.

**Detailed plan**: [subtask-1-exit-codes.md](subtask-1-exit-codes.md)

### Files to Create

| File | Purpose |
|------|---------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/cli/exit_codes.py` | Exit code constants + exception-to-code mapping |
| `packages/core/ai_content_pipeline/ai_content_pipeline/cli/__init__.py` | Package init |
| `tests/test_exit_codes.py` | Unit tests for exit code mapping |

### Files to Modify

| File | Changes |
|------|---------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Use `error_exit()` helper, route errors to stderr (`--debug` already exists at line 598) |
| `packages/providers/fal/text-to-video/fal_text_to_video/cli.py` | Use shared exit codes |
| `packages/providers/fal/image-to-video/fal_image_to_video/cli.py` | Use shared exit codes |

### Design

```python
# exit_codes.py
EXIT_SUCCESS = 0
EXIT_INVALID_ARGS = 2
EXIT_MISSING_CONFIG = 3
EXIT_PROVIDER_ERROR = 4
EXIT_PIPELINE_ERROR = 5

# Maps actual exception classes from ai_content_platform/core/exceptions.py
EXCEPTION_MAP = {
    ValidationError: EXIT_INVALID_ARGS,          # exceptions.py:39
    ConfigurationError: EXIT_MISSING_CONFIG,      # exceptions.py:44
    PipelineConfigurationError: EXIT_MISSING_CONFIG,  # exceptions.py:9
    APIKeyError: EXIT_MISSING_CONFIG,             # exceptions.py:24
    ServiceNotAvailableError: EXIT_PROVIDER_ERROR,    # exceptions.py:19
    StepExecutionError: EXIT_PIPELINE_ERROR,      # exceptions.py:14
    PipelineExecutionError: EXIT_PIPELINE_ERROR,  # exceptions.py:49
}

def error_exit(error, debug=False):
    """Print one-line error to stderr, exit with mapped code."""
    code = EXCEPTION_MAP.get(type(error), 1)
    print(f"error: {error}", file=sys.stderr)
    if debug:
        traceback.print_exc(file=sys.stderr)
    sys.exit(code)
```

### Test Cases
- `test_validation_error_returns_exit_2`
- `test_missing_config_returns_exit_3`
- `test_provider_error_returns_exit_4`
- `test_pipeline_error_returns_exit_5`
- `test_unknown_error_returns_exit_1`
- `test_debug_flag_shows_traceback`
- `test_error_goes_to_stderr`

---

## Subtask 2: JSON Output & --quiet/--debug Flags

**Goal**: Add `--json` flag to all list/generate/status commands that writes structured JSON to stdout (not a file). Add `--quiet` to suppress human-readable output.

**Detailed plan**: [subtask-2-json-output.md](subtask-2-json-output.md)

### Files to Create

| File | Purpose |
|------|---------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/cli/output.py` | Output formatting helpers (JSON vs human) |
| `tests/test_cli_json_output.py` | JSON output validation tests |

### Files to Modify

| File | Changes |
|------|---------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Add `--json`, `--quiet` global flags; modify `print_models()`, `create_video()`, `run_chain()` |
| `packages/providers/fal/text-to-video/fal_text_to_video/cli.py` | Add `--json` to `list-models`, `model-info`, `estimate-cost`, `generate` |
| `packages/providers/fal/image-to-video/fal_image_to_video/cli.py` | Add `--json` to `list-models`, `model-info`, `generate` |

### Design

```python
# output.py
import json
import sys

class CLIOutput:
    """Handles output routing based on --json and --quiet flags."""

    def __init__(self, json_mode=False, quiet=False):
        self.json_mode = json_mode
        self.quiet = quiet

    def result(self, data: dict):
        """Write primary result. JSON to stdout, or human-readable."""
        if self.json_mode:
            json.dump(data, sys.stdout, indent=2, default=str)
            sys.stdout.write("\n")
        elif not self.quiet:
            # Human-readable formatting (existing behavior)
            pass

    def info(self, message: str):
        """Write informational message to stderr (never pollutes stdout)."""
        if not self.quiet:
            print(message, file=sys.stderr)

    def error(self, message: str):
        """Write error to stderr."""
        print(f"error: {message}", file=sys.stderr)
```

### JSON Schema (versioned)

```json
{
  "schema_version": "1",
  "command": "list-models",
  "data": { ... },
  "metadata": {
    "timestamp": "2026-02-07T10:00:00Z",
    "version": "0.1.0"
  }
}
```

### Key Commands to Add --json

| Command | JSON Output Shape |
|---------|-------------------|
| `list-models` | `{"text_to_image": [...], "text_to_video": [...], ...}` |
| `create-video` | `{"success": bool, "output_path": str, "cost": float, "duration": float}` |
| `run-chain` | `{"success": bool, "steps_completed": int, "outputs": {...}, "total_cost": float}` |
| `generate-image` | `{"success": bool, "output_path": str, "model": str}` |
| `list-avatar-models` | `[{"key": str, "name": str, "pricing": ...}]` |
| `analyze-video` | `{"model": str, "analysis_type": str, "result": str}` |

### Test Cases
- `test_list_models_json_is_valid_json`
- `test_list_models_json_has_schema_version`
- `test_quiet_suppresses_human_output`
- `test_json_goes_to_stdout_not_file`
- `test_info_messages_go_to_stderr_in_json_mode`
- `test_error_never_corrupts_json_stdout`

---

## Subtask 3: Stdin/Stdout First

**Goal**: Support `--input -` for reading prompts/configs from stdin. Support `--output -` for writing raw results to stdout.

**Detailed plan**: [subtask-3-stdin-stdout.md](subtask-3-stdin-stdout.md)

### Files to Modify

| File | Changes |
|------|---------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Add stdin reading for `create-video`, `generate-image`, `run-chain` |
| `packages/providers/fal/text-to-video/fal_text_to_video/cli.py` | Add `--input -` for prompt text |
| `packages/providers/fal/image-to-video/fal_image_to_video/cli.py` | Add `--input -` for config |

### Design

```python
# In __main__.py argument parsing
def read_input(args):
    """Read input from --input flag or stdin."""
    if hasattr(args, 'input') and args.input == '-':
        return sys.stdin.read().strip()
    elif hasattr(args, 'input') and args.input:
        return Path(args.input).read_text().strip()
    return getattr(args, 'text', None)
```

### Supported Patterns

```bash
# Read prompt from stdin
echo "cinematic drone shot" | aicp create-video --input -

# Pipe YAML config from stdin
cat pipeline.yaml | aicp run-chain --config -

# Output path only to stdout (for piping)
aicp create-video --text "sunset" --output - 2>/dev/null | xargs open
```

### Test Cases
- `test_create_video_reads_from_stdin`
- `test_run_chain_reads_config_from_stdin`
- `test_generate_image_reads_prompt_from_stdin`
- `test_stdin_dash_flag_triggers_stdin_read`
- `test_stdin_empty_returns_error`

---

## Subtask 4: Non-Interactive Mode

**Goal**: Add `--yes` / `--non-interactive` flags to skip all confirmation prompts. Auto-detect CI environments.

**Detailed plan**: [subtask-4-non-interactive.md](subtask-4-non-interactive.md)

### Files to Modify

| File | Changes |
|------|---------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Add `--yes` global flag, replace `input()` prompts |
| `packages/core/ai_content_platform/cli/commands.py` | Respect `--yes` for cost confirmation |

### Design

```python
def is_non_interactive(args):
    """Check if running non-interactively."""
    if getattr(args, 'yes', False):
        return True
    # Auto-detect CI environments
    ci_vars = ['CI', 'GITHUB_ACTIONS', 'GITLAB_CI', 'JENKINS_URL', 'TF_BUILD']
    return any(os.environ.get(v) for v in ci_vars)

def confirm(message, args):
    """Ask for confirmation, auto-accept in non-interactive mode."""
    if is_non_interactive(args):
        return True
    response = input(f"{message} (y/N): ")
    return response.lower() in ('y', 'yes')
```

### Current Interactive Points (verified)

| File | Line | Current Code | Change |
|------|------|-------------|--------|
| `__main__.py` | 122 | `input(f"⚠️  .env file already exists...")` in `setup_env()` | Use `confirm()` helper |
| `__main__.py` | 278-282 | `input("\nProceed with execution? (y/N): ")` in `run_chain()` — **NOTE: `--no-confirm` defaults to `True` (line 635), so this is already bypassed by default** | Use `confirm()` helper; change `--no-confirm` default to `False` for safety |
| `cli/commands.py` | 96-99 | `click.confirm(f"Proceed with estimated cost...")` | Pass `--yes` via Click context |

### Test Cases
- `test_yes_flag_skips_confirmation`
- `test_ci_env_auto_skips_confirmation`
- `test_non_interactive_flag_works`
- `test_default_prompts_without_yes`

---

## Subtask 5: XDG Config/Cache/State Paths

**Goal**: Follow XDG Base Directory Specification for config, cache, and state directories. Fall back to `~/.config/`, `~/.cache/`, `~/.local/state/` on Linux/Mac. Use `%APPDATA%` on Windows.

**Detailed plan**: [subtask-5-xdg-paths.md](subtask-5-xdg-paths.md)

### Files to Create

| File | Purpose |
|------|---------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/cli/paths.py` | XDG path resolution with env overrides |
| `tests/test_xdg_paths.py` | Path resolution tests across platforms |

### Files to Modify

| File | Changes |
|------|---------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Use XDG paths for default config/cache locations |
| `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/manager.py` | Use XDG cache for temp files |
| `packages/core/ai_content_pipeline/ai_content_pipeline/utils/file_manager.py` | Optional XDG-aware defaults |

### Design

```python
# paths.py
APP_NAME = "video-ai-studio"

def config_dir() -> Path:
    """XDG_CONFIG_HOME/video-ai-studio or platform default."""
    if custom := os.environ.get("XDG_CONFIG_HOME"):
        return Path(custom) / APP_NAME
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", "~")) / APP_NAME
    return Path.home() / ".config" / APP_NAME

def cache_dir() -> Path:
    """XDG_CACHE_HOME/video-ai-studio or platform default."""
    if custom := os.environ.get("XDG_CACHE_HOME"):
        return Path(custom) / APP_NAME
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", "~")) / APP_NAME / "cache"
    return Path.home() / ".cache" / APP_NAME

def state_dir() -> Path:
    """XDG_STATE_HOME/video-ai-studio or platform default."""
    if custom := os.environ.get("XDG_STATE_HOME"):
        return Path(custom) / APP_NAME
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", "~")) / APP_NAME / "state"
    return Path.home() / ".local" / "state" / APP_NAME

def default_config_path() -> Path:
    """Default config file location."""
    return config_dir() / "config.yaml"
```

### CLI Overrides

```bash
# Environment-based
XDG_CONFIG_HOME=/custom/config aicp list-models

# Flag-based (always wins)
aicp run-chain --config /path/to/config.yaml --cache-dir /tmp/cache
```

### Test Cases
- `test_config_dir_uses_xdg_env`
- `test_config_dir_fallback_linux`
- `test_config_dir_fallback_windows`
- `test_cache_dir_uses_xdg_env`
- `test_state_dir_uses_xdg_env`
- `test_cli_override_wins_over_xdg`
- `test_dirs_are_created_on_access`

---

## Subtask 6: Stream-Friendly Pipeline Execution

**Goal**: Add `--stream` mode that emits JSON Lines events to stderr during pipeline execution, with a final result event to stdout.

**Detailed plan**: [subtask-6-streaming.md](subtask-6-streaming.md)

### Files to Create

| File | Purpose |
|------|---------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/cli/stream.py` | JSONL event emitter |
| `tests/test_stream_output.py` | Streaming output validation |

### Files to Modify

| File | Changes |
|------|---------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Add `--stream` flag to `run-chain` |
| `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/executor.py` | Accept optional event callback |

### Design

```python
# stream.py
import json
import sys
import time

class StreamEmitter:
    """Emits JSONL progress events to stderr."""

    def __init__(self, enabled=False):
        self.enabled = enabled
        self.start_time = time.time()

    def emit(self, event_type: str, data: dict):
        if not self.enabled:
            return
        event = {
            "schema_version": "1",
            "event": event_type,
            "timestamp": time.time(),
            "elapsed": time.time() - self.start_time,
            **data,
        }
        print(json.dumps(event), file=sys.stderr)

    def step_start(self, step_index: int, step_type: str, model: str):
        self.emit("step_start", {
            "step": step_index,
            "type": step_type,
            "model": model,
        })

    def step_complete(self, step_index: int, cost: float, output_path: str):
        self.emit("step_complete", {
            "step": step_index,
            "cost": cost,
            "output": output_path,
        })

    def pipeline_complete(self, result: dict):
        """Final result goes to stdout as JSON."""
        print(json.dumps({
            "schema_version": "1",
            "event": "pipeline_complete",
            **result,
        }))
```

### Event Types

| Event | Stream | Description |
|-------|--------|-------------|
| `pipeline_start` | stderr | Pipeline metadata (steps count, config) |
| `step_start` | stderr | Step begins (index, type, model) |
| `step_complete` | stderr | Step done (index, cost, output) |
| `step_error` | stderr | Step failed (index, error) |
| `pipeline_complete` | stdout | Final result (outputs, total_cost, duration) |

### Usage Examples

```bash
# Stream progress to terminal, pipe result to jq
aicp run-chain --config pipeline.yaml --stream 2>/dev/null | jq '.outputs'

# Log progress to file, capture result
aicp run-chain --config pipeline.yaml --stream 2>progress.jsonl | jq -r '.outputs.final.path'

# Watch progress live
aicp run-chain --config pipeline.yaml --stream 2>&1 >/dev/null | jq -r '.event + ": " + (.step|tostring)'
```

### Test Cases
- `test_stream_emits_step_start`
- `test_stream_emits_step_complete`
- `test_stream_final_result_to_stdout`
- `test_stream_progress_to_stderr`
- `test_stream_disabled_by_default`
- `test_stream_events_are_valid_jsonl`

---

## Implementation Order & Dependencies

```
Subtask 1 (Exit Codes) ──────────┐
                                  ├──→ Subtask 2 (JSON Output) ──→ Subtask 3 (Stdin/Stdout)
Subtask 4 (Non-Interactive) ─────┘         │
                                           ├──→ Subtask 6 (Streaming)
Subtask 5 (XDG Paths) ────────────────────┘
```

**Recommended order**: 1 → 4 → 2 → 5 → 3 → 6

- Subtask 1 first: establishes the `cli/` package and error patterns everything else uses
- Subtask 4 next: small, independent, unblocks CI testing
- Subtask 2 next: builds on exit codes, adds output formatting layer
- Subtask 5 next: independent utility, used by output layer for config
- Subtask 3 next: builds on JSON output and exit codes
- Subtask 6 last: builds on everything above

---

## Backward Compatibility Strategy

1. **Default behavior unchanged**: Without new flags, all commands behave exactly as before
2. **Deprecation warnings**: Old `--save-json FILENAME` flag kept temporarily with deprecation notice pointing to `--json`
3. **Schema versioning**: All JSON output includes `"schema_version": "1"` for future evolution
4. **Exit code 1 preserved**: Unknown errors still exit with code 1 (scripts checking `!= 0` still work)
5. **No command renaming**: Existing command names preserved; no breaking surface changes

---

## File Tree (New/Modified)

```
packages/core/ai_content_pipeline/ai_content_pipeline/
├── cli/                          # NEW package
│   ├── __init__.py               # NEW
│   ├── exit_codes.py             # NEW - Exit code constants + mapping
│   ├── output.py                 # NEW - CLIOutput class (json/quiet/human)
│   ├── paths.py                  # NEW - XDG path resolution
│   └── stream.py                 # NEW - JSONL stream emitter
├── __main__.py                   # MODIFIED - Use cli/ helpers
├── pipeline/
│   ├── manager.py                # MODIFIED - XDG-aware defaults
│   └── executor.py               # MODIFIED - Accept stream callback
└── utils/
    └── file_manager.py           # MODIFIED - XDG-aware defaults

packages/providers/fal/
├── text-to-video/fal_text_to_video/cli.py  # MODIFIED - --json, exit codes
└── image-to-video/fal_image_to_video/cli.py # MODIFIED - --json, exit codes

packages/core/ai_content_platform/
└── cli/commands.py               # MODIFIED - --yes flag

tests/
├── test_exit_codes.py            # NEW
├── test_cli_json_output.py       # NEW
├── test_xdg_paths.py             # NEW
└── test_stream_output.py         # NEW
```

---

## Acceptance Criteria

- [ ] Every command supports `--json` for machine-readable output to stdout *(module ready; flag wiring is follow-up)*
- [x] Exit codes are semantic (2/3/4/5) not just 0/1
- [x] Errors go to stderr, results go to stdout
- [x] `--quiet` suppresses all human-readable output *(CLIOutput supports it; flag wiring is follow-up)*
- [x] `--yes` skips interactive prompts; CI auto-detected *(confirm() + is_interactive() implemented)*
- [x] Config/cache/state paths follow XDG on Linux, sensible defaults on Windows
- [x] `--stream` emits JSONL progress events for pipeline execution *(StreamEmitter ready; executor wiring is follow-up)*
- [x] All new features have pytest tests *(91 new tests across 6 files)*
- [x] Existing tests still pass (no breaking changes) *(677 passed, 1 pre-existing failure)*
- [ ] `--save-json` still works but prints deprecation warning *(not yet implemented)*

## Follow-Up Work (Phase 2)

These items require wiring the new CLI modules into existing command handlers:

1. Add `--json`, `--quiet`, `--debug` global flags to `__main__.py` arg parser
2. Route all command output through `CLIOutput` instead of direct `print()`
3. Add `--input` flag to `create-video`, `generate-image`, `run-chain`
4. Add `--config-dir`, `--cache-dir`, `--state-dir` flags
5. Add `--stream` flag to `run-chain` and pass `StreamEmitter` to `executor.execute()`
6. Suppress `executor.py` print pollution when `--json` mode is active
7. Add `--save-json` deprecation warning pointing to `--json`
