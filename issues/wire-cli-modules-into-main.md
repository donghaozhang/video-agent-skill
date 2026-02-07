# Wire CLI Modules into __main__.py

**Status**: COMPLETED
**Branch**: `feat/unix-linux-style-framework-migration`
**Parent**: [framework-unix-linux-style-migration.md](framework-unix-linux-style-migration.md)
**Depends on**: Phase 1 CLI modules (all 6 subtasks in `completed/`)
**Estimated Time**: ~90 minutes (7 subtasks)
**Tests**: 35 new tests in `tests/test_main_cli_flags.py`, 754 total passing (0 regressions)

---

## Goal

Connect the CLI infrastructure modules (`CLIOutput`, `StreamEmitter`, `read_input`, XDG paths) built in Phase 1 into the actual `__main__.py` command handlers. After this work, every command supports `--json`, `--quiet`, `--debug`, `--input`, and pipeline commands support `--stream`. The existing `--save-json` flag gets a deprecation path.

---

## Key Files

| File | Role |
|------|------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | CLI entry point — 89 `print()` calls, 19 commands, arg parser |
| `packages/core/ai_content_pipeline/ai_content_pipeline/cli/output.py` | `CLIOutput` + `read_input()` |
| `packages/core/ai_content_pipeline/ai_content_pipeline/cli/stream.py` | `StreamEmitter` + `NullEmitter` |
| `packages/core/ai_content_pipeline/ai_content_pipeline/cli/paths.py` | `config_dir()`, `cache_dir()`, `state_dir()` |
| `packages/core/ai_content_pipeline/ai_content_pipeline/cli/exit_codes.py` | `error_exit()`, exit code constants |
| `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/executor.py` | 16 `print()` calls inside step loop |
| `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/manager.py` | 3 `print()` calls, wraps `executor.execute()` |
| `tests/test_main_cli_flags.py` | New test file for this work |

---

## Subtask 1: Add Global Flags to Arg Parser (~10 min) — COMPLETED

**File**: `__main__.py` (lines 485-566, arg parser setup)

Add global flags to the **main parser** (before subparsers), so they apply to all commands:

```python
# After line 566 (--base-dir), before subparsers
parser.add_argument('--json', action='store_true', default=False,
    help='Emit machine-readable JSON output to stdout')
parser.add_argument('--quiet', '-q', action='store_true', default=False,
    help='Suppress non-essential output (errors still go to stderr)')
parser.add_argument('--config-dir', type=str, default=None,
    help='Override config directory (default: XDG_CONFIG_HOME/video-ai-studio)')
parser.add_argument('--cache-dir', type=str, default=None,
    help='Override cache directory (default: XDG_CACHE_HOME/video-ai-studio)')
parser.add_argument('--state-dir', type=str, default=None,
    help='Override state directory (default: XDG_STATE_HOME/video-ai-studio)')
```

Note: `--debug` already exists at line 565. No change needed.

**Tests** (`tests/test_main_cli_flags.py`):
- `test_json_flag_parsed` — verify `args.json == True`
- `test_quiet_flag_parsed` — verify `args.quiet == True`
- `test_debug_flag_already_exists` — verify `args.debug == True`
- `test_dir_overrides_parsed` — verify all three dir flags parse correctly

---

## Subtask 2: Create CLIOutput in main() and Pass to Handlers (~15 min) — COMPLETED

**File**: `__main__.py` (lines 930-973, main dispatch)

After `args = parser.parse_args()` (line 930), instantiate `CLIOutput`:

```python
from .cli.output import CLIOutput

args = parser.parse_args()
output = CLIOutput(
    json_mode=getattr(args, 'json', False),
    quiet=getattr(args, 'quiet', False),
    debug=getattr(args, 'debug', False),
)
```

Then update the dispatch to pass `output` to every handler:

```python
if args.command == "list-models":
    print_models(output)            # was: print_models()
elif args.command == "setup":
    setup_env(args, output)         # was: setup_env(args)
elif args.command == "generate-image":
    generate_image(args, output)    # was: generate_image(args)
# ... etc for all commands
```

Update every handler function signature to accept `output` as a second parameter. For handlers that delegate to imported functions (`analyze_video_command`, `transfer_motion_command`, etc.), pass `output` through only if those functions accept it — otherwise leave them unchanged (they already handle their own output).

**Inline handlers to update** (defined in `__main__.py`):
- `print_models()` → `print_models(output)`
- `setup_env(args)` → `setup_env(args, output)`
- `generate_image(args)` → `generate_image(args, output)`
- `create_video(args)` → `create_video(args, output)`
- `run_chain(args)` → `run_chain(args, output)`
- `create_examples(args)` → `create_examples(args, output)`
- `generate_avatar(args)` → `generate_avatar(args, output)`
- `list_avatar_models(args)` → `list_avatar_models(args, output)`

**Tests**:
- `test_output_object_created_with_json_mode` — mock `CLIOutput`, verify `json_mode=True` when `--json` passed
- `test_output_object_created_with_quiet_mode` — same for `--quiet`

---

## Subtask 3: Replace print() in Command Handlers with CLIOutput (~20 min) — COMPLETED

**File**: `__main__.py` — all handler functions

Replace every `print()` call in the 8 inline handler functions with the appropriate `CLIOutput` method:

| Old Pattern | New Pattern |
|-------------|-------------|
| `print("✅ ...")` (success info) | `output.info("...")` |
| `print("❌ ...")` (error) | `output.error("...")` |
| `print("📋 ...")` / `print("📝 ...")` (progress) | `output.info("...")` |
| `print(f"💰 ...")` (cost/debug info) | `output.verbose("...")` |
| Final result block (success + outputs) | `output.result({...}, command="cmd-name")` |

**Conversion rules**:
1. **Success results** — replace the multi-line success block with a single `output.result()` call containing structured data
2. **Error messages** — use `output.error()` (always goes to stderr)
3. **Progress info** — use `output.info()` (suppressed in `--json`/`--quiet`)
4. **Debug info** — use `output.verbose()` (only in `--debug`)
5. **List/table output** — use `output.table()` for `print_models()` and `list_avatar_models()`

**Example — `create_video()` conversion** (lines 158-170):

Before:
```python
print(f"\n✅ Video creation successful!")
print(f"📦 Steps completed: {result.steps_completed}/{result.total_steps}")
print(f"💰 Total cost: ${result.total_cost:.3f}")
print(f"⏱️  Total time: {result.total_time:.1f} seconds")
```

After:
```python
output.result({
    "success": True,
    "steps_completed": result.steps_completed,
    "total_steps": result.total_steps,
    "total_cost": result.total_cost,
    "total_time": result.total_time,
    "outputs": result.outputs,
}, command="create-video")
```

**Handlers to convert** (estimated print count):
- `print_models()` — 10 prints → `output.table()` + `output.info()`
- `setup_env()` — 9 prints → `output.info()` + `output.error()`
- `create_video()` — 8 prints → `output.result()` + `output.info()` + `output.error()`
- `run_chain()` — 12 prints → `output.result()` + `output.info()` + `output.verbose()`
- `generate_image()` — 7 prints → `output.result()` + `output.info()` + `output.error()`
- `create_examples()` — 1 print → `output.info()`
- `generate_avatar()` — 12 prints → `output.result()` + `output.info()` + `output.error()`
- `list_avatar_models()` — 10 prints → `output.table()` + `output.info()`

**Tests**:
- `test_list_models_json_output` — verify JSON array output with `--json`
- `test_create_video_json_result` — verify structured JSON result
- `test_quiet_mode_suppresses_info` — verify no stdout info in `--quiet`
- `test_error_always_on_stderr` — verify errors on stderr regardless of mode

---

## Subtask 4: Add --input Flag and Wire read_input() (~10 min) — COMPLETED

**File**: `__main__.py` — subparsers for `create-video`, `generate-image`, `run-chain`

Add `--input` flag to these three commands:

```python
# create-video subparser (after line 590)
create_video_parser.add_argument('--input', type=str, default=None,
    help='Read prompt from file or stdin (use - for stdin)')

# generate-image subparser (after line 579)
generate_image_parser.add_argument('--input', type=str, default=None,
    help='Read prompt from file or stdin (use - for stdin)')

# run-chain subparser (after line 598)
run_chain_parser.add_argument('--input', type=str, default=None,
    help='Read input data from file or stdin (use - for stdin)')
```

In the handlers, use `read_input()` to resolve the input:

```python
from .cli.output import read_input

# In create_video() handler:
text = read_input(args.input, fallback=args.text) if args.input else args.text

# In generate_image() handler:
text = read_input(args.input, fallback=args.text) if args.input else args.text

# In run_chain() handler — replace the complex input_data resolution (lines 196-260):
if args.input:
    input_data = read_input(args.input)
# ... existing fallback logic for --input-text, --prompt-file, config
```

**Tests**:
- `test_input_flag_reads_from_file` — write temp file, verify `--input path` reads it
- `test_input_dash_reads_stdin` — mock stdin, verify `--input -` reads it
- `test_input_flag_overrides_text` — verify `--input` takes precedence over `--text`

---

## Subtask 5: Add --stream Flag and Wire StreamEmitter into Executor (~20 min) — COMPLETED

**Files**: `__main__.py`, `executor.py`, `manager.py`

### 5a: Add `--stream` flag to `run-chain` subparser

```python
# __main__.py, after --no-confirm in run-chain parser (line 603)
run_chain_parser.add_argument('--stream', action='store_true', default=False,
    help='Emit JSONL progress events to stderr during execution')
```

### 5b: Wire StreamEmitter in `run_chain()` handler

```python
from .cli.stream import StreamEmitter, NullEmitter

def run_chain(args, output):
    emitter = StreamEmitter(enabled=args.stream) if args.stream else NullEmitter()
    # ... existing chain loading ...
    emitter.pipeline_start(name=chain.name, total_steps=len(chain.get_enabled_steps()), config=args.config)
    result = manager.execute_chain(chain, input_data, stream_emitter=emitter)
    if args.stream:
        emitter.pipeline_complete({
            "success": result.success,
            "steps_completed": result.steps_completed,
            "total_steps": result.total_steps,
            "total_cost": result.total_cost,
            "total_time": result.total_time,
            "outputs": result.outputs,
            "error": result.error,
        })
    else:
        output.result({...}, command="run-chain")
```

### 5c: Accept `stream_emitter` in `executor.execute()`

**File**: `executor.py`

Add emitter calls inside the step loop (after line 130):

```python
def execute(self, chain, input_data, stream_emitter=None, **kwargs):
    from ..cli.stream import NullEmitter
    emitter = stream_emitter or NullEmitter()
    # ... existing setup ...
    for i, step in enumerate(enabled_steps):
        emitter.step_start(i, step.step_type.value, step.model)
        # ... existing step execution ...
        emitter.step_complete(i, cost=step_result.get('cost', 0), ...)
        # On failure:
        emitter.step_error(i, error_msg, step.step_type.value)
```

### 5d: Pass through from `manager.execute_chain()`

**File**: `manager.py` — the `**kwargs` in `execute_chain()` already passes through to `executor.execute()`, so no change needed.

**Tests**:
- `test_stream_flag_parsed` — verify `args.stream == True`
- `test_executor_accepts_stream_emitter` — verify no crash when emitter passed
- `test_executor_emits_step_events` — mock emitter, verify `step_start`/`step_complete` called
- `test_stream_emitter_not_used_without_flag` — verify `NullEmitter` when `--stream` absent

---

## Subtask 6: Suppress Executor print() in JSON Mode (~10 min) — COMPLETED

**Files**: `executor.py`, `manager.py`

The executor has 16 `print()` calls and manager has 3 — these pollute stdout when `--json` is active. Add a `quiet` parameter:

### 6a: Add `quiet` kwarg to `executor.execute()`

```python
def execute(self, chain, input_data, stream_emitter=None, quiet=False, **kwargs):
    emitter = stream_emitter or NullEmitter()
    # Replace all print() calls:
    if not quiet:
        print(f"Starting chain execution: {len(enabled_steps)} steps")
    # ... same pattern for all 16 prints ...
```

### 6b: Pass `quiet` from `__main__.py`

```python
result = manager.execute_chain(
    chain, input_data,
    stream_emitter=emitter,
    quiet=getattr(args, 'json', False) or getattr(args, 'quiet', False),
)
```

### 6c: Suppress manager prints too

In `manager.execute_chain()`, guard the 3 `print()` calls:

```python
def execute_chain(self, chain, input_data, quiet=False, **kwargs):
    if not quiet:
        print(f"🚀 Executing chain: {chain.name}")
        print(f"📝 Input (...): ...")
    return self.executor.execute(chain, input_data, quiet=quiet, **kwargs)
```

**Tests**:
- `test_executor_quiet_suppresses_prints` — capture stdout, verify empty in quiet mode
- `test_json_mode_suppresses_executor_prints` — end-to-end with `--json`

---

## Subtask 7: Add --save-json Deprecation Warning (~5 min) — COMPLETED

**File**: `__main__.py`

The `--save-json` flag exists on 7 commands. Add a deprecation warning that fires when used, pointing users to `--json`:

```python
import warnings

def _check_save_json_deprecation(args, output):
    """Emit deprecation warning if --save-json is used."""
    if getattr(args, 'save_json', None):
        msg = (
            "--save-json is deprecated and will be removed in a future release. "
            "Use '--json' to emit structured output to stdout, then redirect: "
            "aicp <command> --json > result.json"
        )
        output.warning(msg)
```

Call this at the top of each handler that supports `--save-json`:
- `generate_image()`
- `create_video()`
- `run_chain()`
- `generate_avatar()`

Keep `--save-json` working for now (backward compatibility) — just emit the warning.

**Tests**:
- `test_save_json_deprecation_warning` — verify warning on stderr when `--save-json` used
- `test_save_json_still_works` — verify file still saved (no behavior change yet)

---

## Test Summary

**New test file**: `tests/test_main_cli_flags.py`

| Subtask | Tests | Description |
|---------|-------|-------------|
| 1 | 4 | Global flag parsing |
| 2 | 2 | CLIOutput creation |
| 3 | 4 | Output routing (JSON, quiet, stderr) |
| 4 | 3 | --input flag + read_input() |
| 5 | 4 | --stream flag + executor wiring |
| 6 | 2 | Quiet/JSON suppresses executor prints |
| 7 | 2 | --save-json deprecation |
| **Total** | **21** | |

---

## Implementation Order

```
Subtask 1 (global flags)
    ↓
Subtask 2 (CLIOutput in main)
    ↓
Subtask 3 (replace print calls)  ←  largest subtask
    ↓
Subtask 4 (--input flag)         ←  independent of 3
    ↓
Subtask 5 (--stream wiring)      ←  depends on 2
    ↓
Subtask 6 (suppress prints)      ←  depends on 5
    ↓
Subtask 7 (deprecation warning)  ←  independent
```

Subtasks 4 and 7 can be done in any order. Subtask 6 must follow Subtask 5.

---

## Verification

```bash
# Run new tests
python -m pytest tests/test_main_cli_flags.py -v --override-ini='testpaths=tests'

# Full suite regression check
python -m pytest tests/ -v --override-ini='testpaths=tests'

# Manual smoke tests
echo "cinematic drone shot" | aicp create-video --input - --json
aicp list-models --json | python -c "import sys,json; json.load(sys.stdin)"
aicp run-chain --config input/pipelines/example.yaml --stream 2>/dev/null | jq '.'
```

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking imported command handlers (`analyze_video_command`, etc.) | Don't change their signatures — only update inline handlers |
| Executor `print()` removal breaks debugging | Guard with `if not quiet:`, not removal — prints still work without `--json`/`--quiet` |
| `--save-json` removal breaks existing scripts | Keep working, add warning only — remove in next major version |
| `--json` conflicts with argparse reserved names | argparse allows `--json` as a flag name (verified) |
