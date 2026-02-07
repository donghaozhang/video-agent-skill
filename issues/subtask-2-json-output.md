# Subtask 2: JSON Output & --quiet/--debug Flags

**Parent**: [plan-unix-style-migration.md](plan-unix-style-migration.md)
**Depends on**: Subtask 1 (exit codes)
**Estimated Time**: 60 minutes

---

## Objective

Add `--json` flag to all list/generate/status commands that writes structured JSON to stdout. Add `--quiet` to suppress human-readable output. Informational messages go to stderr so stdout stays clean for piping.

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

In the `main()` function, add to the global argument parser:

```python
parser.add_argument('--json', action='store_true', default=False,
                    help='Output results as JSON to stdout')
parser.add_argument('--quiet', '-q', action='store_true', default=False,
                    help='Suppress informational output')
```

After parsing args, create output helper:

```python
from .cli.output import CLIOutput
output = CLIOutput(json_mode=args.json, quiet=args.quiet)
```

### Step 3: Modify `print_models()` for JSON support

**Current** (~line 64):
```python
def print_models():
    print("\n🎨 AI Content Pipeline Supported Models")
    # ... human-readable table
```

**New**:
```python
def print_models(output: CLIOutput):
    if output.is_json:
        from .registry import ModelRegistry
        data = {}
        for category in ModelRegistry.get_supported_models():
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
    # ...
```

### Step 4: Modify `create_video()` for JSON support

**Current** (~line 130):
```python
def create_video(args, manager):
    # ... execution logic ...
    print(f"\n✅ Video created successfully!")
    print(f"📁 Output: {result.output_path}")
    print(f"💰 Cost: ${result.cost:.4f}")
```

**New**:
```python
def create_video(args, manager, output: CLIOutput):
    # ... execution logic ...
    result_data = {
        "success": True,
        "output_path": str(result.output_path),
        "cost": result.cost,
        "model": args.model,
        "duration": result.processing_time,
    }
    output.result(result_data, command="create-video")
    output.human(f"\n✅ Video created successfully!")
    output.human(f"📁 Output: {result.output_path}")
    output.human(f"💰 Cost: ${result.cost:.4f}")
```

### Step 5: Modify `run_chain()` for JSON support

**Current** (~line 165):
```python
def run_chain(args, manager):
    # ... saves JSON to file with --save-json ...
```

**New**:
```python
def run_chain(args, manager, output: CLIOutput):
    # ... execution logic ...
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
    if hasattr(args, 'save_json') and args.save_json:
        output.info("warning: --save-json is deprecated, use --json instead")
        json_path = manager.output_dir / args.save_json
        with open(json_path, 'w') as f:
            json.dump(result_data, f, indent=2)
        output.info(f"Results saved to: {json_path}")

    # Human-readable summary
    if result.success:
        output.human(f"\n✅ Pipeline completed!")
    else:
        output.human(f"\n❌ Pipeline failed: {result.error}")
```

### Step 6: Update provider CLIs

**File**: `packages/providers/fal/text-to-video/fal_text_to_video/cli.py`

Add to Click group:
```python
@click.option('--json', 'json_mode', is_flag=True, help='Output as JSON')
```

In `list_models`:
```python
@cli.command("list-models")
@click.option('--json', 'json_mode', is_flag=True, help='Output as JSON')
def list_models(json_mode):
    if json_mode:
        data = [{"key": k, **info} for k, info in models.items()]
        click.echo(json.dumps({"schema_version": "1", "data": data}, indent=2))
        return
    # ... existing human output ...
```

Same pattern for `fal_image_to_video/cli.py`.

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
