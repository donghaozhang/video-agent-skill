# Subtask 2: JSON Output & --quiet/--debug Flags

**Status**: COMPLETED (core module + tests; wiring into all commands is follow-up work)
**PR**: [#20](https://github.com/donghaozhang/video-agent-skill/pull/20)
**Parent**: [plan-unix-style-migration.md](plan-unix-style-migration.md)
**Depends on**: Subtask 1 (exit codes)
**Estimated Time**: 60 minutes

### Implementation Summary
- Created `cli/output.py` with `CLIOutput` class (json_mode, quiet, debug) and `SCHEMA_VERSION = "1"`
- Methods: `info()`, `error()`, `warning()`, `verbose()`, `result()`, `table()`
- JSON mode: structured envelope with `schema_version` and `command` fields to stdout
- Quiet mode: suppresses all non-error output; errors always go to stderr
- 17 tests in `tests/test_cli_output.py` — all passing
- **Remaining work**: Wire `--json`/`--quiet` flags into `__main__.py` arg parser and all command handlers

---

## Objective

Add `--json` flag to all list/generate/status commands that writes structured JSON to stdout. Add `--quiet` to suppress human-readable output. Informational messages go to stderr so stdout stays clean for piping.

## Critical Issue: Print Pollution in Core Modules

The following modules print directly to stdout and **will corrupt JSON output** unless addressed:

| File | Line(s) | Print Statement |
|------|---------|-----------------|
| `pipeline/executor.py` | 94, 96, 98 | `"Parallel execution extension loaded..."` |
| `pipeline/executor.py` | 127 | `f"Starting chain execution: {len(enabled_steps)} steps"` |
| `pipeline/executor.py` | 131 | `f"Step {i+1}/{len(enabled_steps)}: ..."` |
| `pipeline/executor.py` | 179 | `f"Step completed in {step_result.get('processing_time', 0):.1f}s"` |
| `pipeline/executor.py` | 253 | `"Stored generated prompt, keeping image data..."` |
| `pipeline/executor.py` | 377, 419-421, 435, 458 | Success/failure/report messages |
| `pipeline/manager.py` | 56 | `f"✅ AI Pipeline Manager initialized (base: ...)"` |
| `pipeline/manager.py` | 153-154 | `f"🚀 Executing chain: ..."`, `f"📝 Input ..."` |
| `pipeline/manager.py` | 333 | `f"📄 Example configurations created in: ..."` |

**Strategy**: Route all core module print statements through the `CLIOutput` instance or replace with `logging` calls. For the initial implementation, redirect these to `sys.stderr` when `--json` mode is active.

The `cli/commands.py:220-239` already has a `--format json` option for the `cost` command — this is a precedent we can follow.

---

## Step-by-Step Implementation

### Step 1: Create `cli/output.py`

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/cli/output.py`

```python
"""
Output formatting for CLI commands.

Supports three modes:
- Default: Human-readable output to stdout (existing behavior)
- --json: Structured JSON to stdout, info to stderr
- --quiet: Suppress all non-essential output
"""

import json
import sys
import time
from typing import Any, Dict, Optional


SCHEMA_VERSION = "1"


class CLIOutput:
    """Routes output based on --json and --quiet flags."""

    def __init__(self, json_mode: bool = False, quiet: bool = False):
        self.json_mode = json_mode
        self.quiet = quiet

    def result(self, data: Dict[str, Any], command: Optional[str] = None):
        """Write primary result to stdout.

        In JSON mode, wraps data in versioned envelope.
        In human mode, caller is responsible for formatting.
        """
        if self.json_mode:
            envelope = {
                "schema_version": SCHEMA_VERSION,
                "data": data,
            }
            if command:
                envelope["command"] = command
            json.dump(envelope, sys.stdout, indent=2, default=str)
            sys.stdout.write("\n")
            sys.stdout.flush()

    def info(self, message: str):
        """Write informational message to stderr.

        Suppressed in --quiet mode. Never touches stdout.
        """
        if not self.quiet:
            print(message, file=sys.stderr)

    def error(self, message: str):
        """Write error to stderr. Never suppressed."""
        print(f"error: {message}", file=sys.stderr)

    def human(self, text: str):
        """Write human-readable text to stdout.

        Suppressed in --json mode (use result() for data) and --quiet mode.
        """
        if not self.json_mode and not self.quiet:
            print(text)

    @property
    def is_json(self) -> bool:
        return self.json_mode

    @property
    def is_quiet(self) -> bool:
        return self.quiet
```

### Step 2: Add global flags to `__main__.py`

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

In the `main()` function at lines 597-599 (after `--debug` and `--base-dir`), add:

```python
parser.add_argument('--json', action='store_true', default=False,
                    help='Output results as JSON to stdout')
parser.add_argument('--quiet', '-q', action='store_true', default=False,
                    help='Suppress informational output')
```

After `args = parser.parse_args()` at line 963, create output helper:

```python
from .cli.output import CLIOutput
output = CLIOutput(json_mode=args.json, quiet=args.quiet)
```

Then pass `output` to all handler functions. The command routing at lines 966-1006 needs updating:
```python
# Before:
if args.command == "list-models":
    print_models()
elif args.command == "create-video":
    create_video(args)
# After:
if args.command == "list-models":
    print_models(output)
elif args.command == "create-video":
    create_video(args, output)
```

**NOTE**: Functions that are imported from other modules (`analyze_video_command`, `list_video_models`, `transfer_motion_command`, etc.) will need their signatures updated too, but this can be done incrementally. Start with the 4 high-usage commands: `list-models`, `create-video`, `run-chain`, `generate-image`.

### Step 3: Modify `print_models()` for JSON support

**Current** (lines 64-89):
```python
def print_models():
    """Print information about all supported models."""
    print("\n🎨 AI Content Pipeline Supported Models")
    print("=" * 50)
    manager = AIPipelineManager()  # NOTE: This prints "✅ AI Pipeline Manager initialized" to stdout!
    available_models = manager.get_available_models()
    # ... loops through step_type/models with print() ...
```

**New** — accept `output` parameter, use registry directly to avoid manager init print:
```python
def print_models(output: CLIOutput):
    if output.is_json:
        from .registry import ModelRegistry
        data = {}
        for category, keys in ModelRegistry.get_supported_models().items():
            models = ModelRegistry.list_by_category(category)
            data[category] = [
                {
                    "key": m.key,
                    "name": m.name,
                    "provider": m.provider,
                    "description": m.description,
                    "pricing": m.pricing,
                }
                for m in models
            ]
        output.result(data, command="list-models")
        return

    # Existing human-readable output (unchanged)
    output.human("\n🎨 AI Content Pipeline Supported Models")
    output.human("=" * 50)
    manager = AIPipelineManager()  # OK for human mode
    available_models = manager.get_available_models()
    # ... rest of existing code ...
```

**Key insight**: For `--json` mode, use `ModelRegistry` directly (already populated via `registry_data.py` import) to avoid the `AIPipelineManager()` constructor which prints to stdout at line 56.

### Step 4: Modify `create_video()` for JSON support

**Current** (lines 142-194). Signature is `def create_video(args):` — takes only `args`.
Uses `manager.quick_create_video()` which returns a `ChainResult` with fields:
`success`, `steps_completed`, `total_steps`, `total_cost`, `total_time`, `outputs`, `error`.

**New** — add `output` parameter:
```python
def create_video(args, output: CLIOutput):
    manager = AIPipelineManager(args.base_dir)
    result = manager.quick_create_video(
        text=args.text,
        image_model=args.image_model,
        video_model=args.video_model,
        output_dir=args.output_dir
    )
    if result.success:
        result_data = {
            "success": True,
            "steps_completed": result.steps_completed,
            "total_cost": result.total_cost,
            "total_time": result.total_time,
            "outputs": result.outputs,
        }
        output.result(result_data, command="create-video")
        output.human(f"\n✅ Video creation successful!")
        output.human(f"📦 Steps completed: {result.steps_completed}/{result.total_steps}")
        output.human(f"💰 Total cost: ${result.total_cost:.3f}")
    else:
        # Error result also goes via JSON if --json is active
        output.result({"success": False, "error": result.error}, command="create-video")
        output.human(f"\n❌ Video creation failed!")
        output.human(f"Error: {result.error}")
```

**NOTE**: The `--save-json` pattern at lines 172-187 writes to a file. Keep it with deprecation warning.

### Step 5: Modify `run_chain()` for JSON support

**Current** (lines 197-320). Signature is `def run_chain(args):` — takes only `args`.
Creates `AIPipelineManager(args.base_dir)` at line 200, loads chain from `args.config` at line 203.
Has extensive input handling (lines 207-264), validation (lines 267-272), cost estimate (lines 275-276),
confirmation prompt (lines 278-282), execution (line 285), and result display (lines 288-313).
`--save-json` writes result dict to a file at lines 298-313.

**New** — add `output` parameter:
```python
def run_chain(args, output: CLIOutput):
    manager = AIPipelineManager(args.base_dir)
    chain = manager.create_chain_from_config(args.config)
    # ... existing input handling (route info to output.info) ...

    result = manager.execute_chain(chain, input_data)

    result_data = {
        "success": result.success,
        "steps_completed": result.steps_completed,
        "total_steps": result.total_steps,
        "total_cost": result.total_cost,
        "total_time": result.total_time,
        "outputs": result.outputs,
        "error": result.error,
    }

    output.result(result_data, command="run-chain")

    # Keep --save-json for backward compatibility with deprecation warning
    if getattr(args, 'save_json', None):
        output.info("warning: --save-json is deprecated, use --json instead")
        json_path = manager.output_dir / args.save_json
        with open(json_path, 'w') as f:
            json.dump(result_data, f, indent=2, default=str)
        output.info(f"Results saved to: {json_path}")

    # Human-readable summary
    if result.success:
        output.human(f"\n✅ Chain execution successful!")
        output.human(f"📦 Steps completed: {result.steps_completed}/{result.total_steps}")
        output.human(f"💰 Total cost: ${result.total_cost:.3f}")
        output.human(f"⏱️  Total time: {result.total_time:.1f} seconds")
    else:
        output.human(f"\n❌ Chain execution failed!")
        output.human(f"Error: {result.error}")
```

**NOTE**: The intermediate print statements at lines 205, 217, 231, 239, 247, 256, 264, 269-271, 276
should be routed through `output.info()` (goes to stderr, suppressed by `--quiet`).

### Step 6: Update provider CLIs

**File**: `packages/providers/fal/text-to-video/fal_text_to_video/cli.py`

Add `import json` at top (not currently imported). Add `--json` per-command (Click doesn't have global options on groups as easily as argparse).

**`list-models` (line 101)** — currently uses `generator.compare_models()` which returns a dict:
```python
@cli.command("list-models")
@click.option('--json', 'json_mode', is_flag=True, help='Output as JSON')
def list_models(json_mode):
    generator = FALTextToVideoGenerator()
    comparison = generator.compare_models()
    if json_mode:
        import json
        click.echo(json.dumps({"schema_version": "1", "command": "list-models", "data": comparison}, indent=2, default=str))
        return
    # ... existing human output (lines 106-115) unchanged ...
```

**`model-info` (line 118)** — currently calls `generator.get_model_info(model)`:
```python
@cli.command("model-info")
@click.argument("model", type=click.Choice(T2V_MODELS, case_sensitive=True))
@click.option('--json', 'json_mode', is_flag=True, help='Output as JSON')
def model_info(model, json_mode):
    generator = FALTextToVideoGenerator()
    info = generator.get_model_info(model)
    if json_mode:
        import json
        click.echo(json.dumps({"schema_version": "1", "command": "model-info", "data": info}, indent=2, default=str))
        return
    # ... existing human output unchanged ...
```

**`estimate-cost` (line 151)** and **`generate` (line 32)** — same pattern.

**File**: `packages/providers/fal/image-to-video/fal_image_to_video/cli.py` — same pattern for `list-models` (line 125), `model-info` (line 151), `generate` (line 32).

### Step 7: Write tests

**File**: `tests/test_cli_json_output.py`

```python
"""Tests for --json CLI output across commands."""

import json
import subprocess
import pytest


class TestListModelsJSON:
    def test_json_is_valid(self):
        result = subprocess.run(
            ['ai-content-pipeline', 'list-models', '--json'],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "schema_version" in data
        assert data["schema_version"] == "1"
        assert "data" in data

    def test_json_has_categories(self):
        result = subprocess.run(
            ['ai-content-pipeline', 'list-models', '--json'],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        categories = data["data"]
        assert "text_to_video" in categories
        assert "text_to_image" in categories

    def test_json_models_have_key_and_name(self):
        result = subprocess.run(
            ['ai-content-pipeline', 'list-models', '--json'],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        for category, models in data["data"].items():
            for model in models:
                assert "key" in model
                assert "name" in model

    def test_quiet_suppresses_human_output(self):
        result = subprocess.run(
            ['ai-content-pipeline', 'list-models', '--quiet'],
            capture_output=True, text=True, timeout=30
        )
        assert result.stdout.strip() == ""

    def test_info_messages_go_to_stderr_in_json_mode(self):
        result = subprocess.run(
            ['ai-content-pipeline', 'list-models', '--json'],
            capture_output=True, text=True, timeout=30
        )
        # stdout should be pure JSON (parseable)
        json.loads(result.stdout)
        # stderr may have info messages but doesn't corrupt stdout


class TestJSONSchema:
    def test_schema_version_is_string(self):
        result = subprocess.run(
            ['ai-content-pipeline', 'list-models', '--json'],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        assert isinstance(data["schema_version"], str)
```

---

## Verification

```bash
# Test JSON output
ai-content-pipeline list-models --json | python -m json.tool
ai-content-pipeline list-models --json | jq '.data.text_to_video[].key'

# Test quiet mode
ai-content-pipeline list-models --quiet  # No output

# Test backward compatibility
ai-content-pipeline list-models  # Same as before (human-readable)

# Run tests
python -m pytest tests/test_cli_json_output.py -v
```

---

## Notes

- `--json` and `--quiet` are mutually compatible: `--json --quiet` outputs JSON with no stderr info
- `--save-json FILENAME` is preserved for backward compatibility but emits a deprecation warning to stderr
- Provider CLIs (`fal-text-to-video`, `fal-image-to-video`) get their own `--json` flag per-command
