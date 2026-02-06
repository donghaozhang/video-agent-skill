# Unify CLI Framework: Migrate Argparse Provider CLIs to Click

## Problem Statement

The project uses **two CLI frameworks** side by side:

| Framework | Used By | Entry Points |
|-----------|---------|--------------|
| **Argparse** | Unified pipeline (`ai-content-pipeline`), FAL provider CLIs | `ai-content-pipeline`, `aicp`, `fal-text-to-video`, `fal-image-to-video` |
| **Click** | ViMax pipeline, AI Content Platform | `vimax` |

This creates three problems:
1. **Cognitive overhead** - Contributors (human or LLM) must understand two patterns
2. **No composability** - Argparse CLIs can't be nested as Click subgroups
3. **Inconsistent UX** - Different help formatting, option styles, and error handling

## Goal

Migrate the two argparse **provider CLIs** (`fal-text-to-video`, `fal-image-to-video`) to Click, then register them as subcommand groups under the unified `ai-content-pipeline` CLI. Keep the standalone entry points working for backward compatibility.

**Estimated total implementation time: ~2 hours**

---

## Current Architecture

```
ENTRY POINTS (setup.py):
  ai-content-pipeline  → __main__.py:main()        [argparse, 25 commands]
  aicp                 → __main__.py:main()        [alias]
  fal-text-to-video    → fal_text_to_video/cli.py  [argparse, 4 commands]
  fal-image-to-video   → fal_image_to_video/cli.py [argparse, 4 commands]
  vimax                → vimax/cli/commands.py      [click, 11 commands]
```

## Target Architecture

```
ENTRY POINTS (setup.py):
  ai-content-pipeline  → __main__.py:main()        [click, all commands]
  aicp                 → __main__.py:main()        [alias]
  fal-text-to-video    → fal_text_to_video/cli.py  [click, 4 commands]  ← thin wrapper
  fal-image-to-video   → fal_image_to_video/cli.py [click, 4 commands]  ← thin wrapper
  vimax                → vimax/cli/commands.py      [click, 11 commands]
```

All CLIs use Click. Provider CLIs can run standalone **or** as subgroups of the unified CLI.

---

## Subtask 1: Migrate `fal-text-to-video` CLI from Argparse to Click

**Time estimate:** 30 minutes

### Files to modify

**File 1:** `packages/providers/fal/text-to-video/fal_text_to_video/cli.py`
- Current: 283 lines, argparse with 4 subcommands (`generate`, `list-models`, `model-info`, `estimate-cost`)
- Target: Click group with 4 commands, same behavior

### What to build

Replace the entire argparse-based CLI with Click equivalents:

```python
# cli.py - AFTER migration
import click
from ai_content_pipeline.registry import ModelRegistry
import ai_content_pipeline.registry_data  # noqa: F401
from .generator import FALTextToVideoGenerator

T2V_MODELS = ModelRegistry.keys_for_category("text_to_video")


@click.group()
def cli():
    """FAL Text-to-Video Generation CLI."""
    pass


@cli.command()
@click.option("--prompt", "-p", required=True, help="Text prompt for video generation")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(T2V_MODELS, case_sensitive=True),
              help="Model to use")
@click.option("--duration", "-d", default=None, help="Video duration")
@click.option("--aspect-ratio", "-a", default="16:9",
              type=click.Choice(["16:9", "9:16", "1:1", "4:3", "3:2", "2:3", "3:4"]),
              help="Aspect ratio")
@click.option("--resolution", "-r", default="720p",
              type=click.Choice(["480p", "720p", "1080p"]),
              help="Resolution")
@click.option("--output", "-o", default="output", help="Output directory")
@click.option("--negative-prompt", default=None, help="Negative prompt (Kling only)")
@click.option("--cfg-scale", type=float, default=0.5, help="CFG scale 0-1 (Kling only)")
@click.option("--audio", is_flag=True, help="Generate audio")
@click.option("--keep-remote", is_flag=True, help="Keep video on remote server (Sora only)")
@click.option("--mock", is_flag=True, help="Mock mode: simulate without API call (FREE)")
def generate(prompt, model, duration, aspect_ratio, resolution, output,
             negative_prompt, cfg_scale, audio, keep_remote, mock):
    """Generate video from text prompt."""
    # ... (handler logic stays the same, just uses click params directly)


@cli.command("list-models")
def list_models():
    """List available text-to-video models."""
    # ...


@cli.command("model-info")
@click.argument("model", type=click.Choice(T2V_MODELS, case_sensitive=True))
def model_info(model):
    """Show detailed model information."""
    # ...


@cli.command("estimate-cost")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(T2V_MODELS, case_sensitive=True))
@click.option("--duration", "-d", default=None)
@click.option("--resolution", "-r", default="720p", type=click.Choice(["720p", "1080p"]))
@click.option("--audio", is_flag=True)
def estimate_cost(model, duration, resolution, audio):
    """Estimate cost for video generation."""
    # ...


def main():
    """Entry point for console_scripts."""
    cli()
```

### Key migration notes

- `argparse.add_argument("--flag", action="store_true")` → `@click.option("--flag", is_flag=True)`
- `subparsers.add_parser("cmd")` → `@cli.command("cmd")`
- `args.func(args)` dispatch → Click handles routing automatically
- `choices=[...]` → `type=click.Choice([...])`
- Positional `add_argument("model")` → `@click.argument("model")`
- Handler functions receive named params instead of `args` namespace

### Test file

**New file:** `tests/test_t2v_cli.py`

```python
import pytest
from click.testing import CliRunner
from fal_text_to_video.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "FAL Text-to-Video" in result.output

def test_generate_help(runner):
    result = runner.invoke(cli, ["generate", "--help"])
    assert result.exit_code == 0
    assert "--prompt" in result.output

def test_list_models(runner):
    result = runner.invoke(cli, ["list-models"])
    assert result.exit_code == 0
    assert "kling_2_6_pro" in result.output

def test_model_info(runner):
    result = runner.invoke(cli, ["model-info", "kling_2_6_pro"])
    assert result.exit_code == 0
    assert "Kling" in result.output

def test_estimate_cost(runner):
    result = runner.invoke(cli, ["estimate-cost", "--model", "kling_2_6_pro", "--duration", "5"])
    assert result.exit_code == 0
    assert "$" in result.output

def test_generate_missing_prompt(runner):
    result = runner.invoke(cli, ["generate", "--model", "kling_2_6_pro"])
    assert result.exit_code != 0  # Missing required --prompt

def test_generate_invalid_model(runner):
    result = runner.invoke(cli, ["generate", "--prompt", "test", "--model", "nonexistent"])
    assert result.exit_code != 0
```

---

## Subtask 2: Migrate `fal-image-to-video` CLI from Argparse to Click

**Time estimate:** 30 minutes

### Files to modify

**File 1:** `packages/providers/fal/image-to-video/fal_image_to_video/cli.py`
- Current: 237 lines, argparse with 4 subcommands (`generate`, `interpolate`, `list-models`, `model-info`)
- Target: Click group with 4 commands, same behavior

### What to build

Same migration pattern as Subtask 1. Key differences:

- Has an `interpolate` command (frame interpolation between two images)
- `generate` takes `--image` as required input (local path or URL)
- Model choices use `I2V_MODELS` (provider keys, not registry keys)
- No `estimate-cost` command; has `interpolate` instead

```python
@cli.command()
@click.option("--image", "-i", required=True, help="Input image path or URL")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(I2V_MODELS, case_sensitive=True))
@click.option("--prompt", "-p", required=True, help="Text prompt")
@click.option("--duration", "-d", default="5", help="Video duration")
@click.option("--output", "-o", default="output", help="Output directory")
@click.option("--end-frame", default=None, help="End frame for interpolation")
@click.option("--negative-prompt", default="blur, distortion, low quality")
@click.option("--cfg-scale", type=float, default=0.5, help="CFG scale (0-1)")
@click.option("--audio", is_flag=True, help="Generate audio")
def generate(image, model, prompt, duration, output, end_frame,
             negative_prompt, cfg_scale, audio):
    """Generate video from image."""
    # ...


@cli.command()
@click.option("--start-frame", "-s", required=True, help="Start frame image")
@click.option("--end-frame", "-e", required=True, help="End frame image")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(["kling_2_1", "kling_2_6_pro", "kling_3_standard", "kling_3_pro"]))
@click.option("--prompt", "-p", required=True, help="Text prompt")
@click.option("--duration", "-d", default="5", help="Duration")
def interpolate(start_frame, end_frame, model, prompt, duration):
    """Generate video interpolating between two frames."""
    # ...
```

### Test file

**New file:** `tests/test_i2v_cli.py`

```python
import pytest
from click.testing import CliRunner
from fal_image_to_video.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0

def test_generate_help(runner):
    result = runner.invoke(cli, ["generate", "--help"])
    assert result.exit_code == 0
    assert "--image" in result.output

def test_list_models(runner):
    result = runner.invoke(cli, ["list-models"])
    assert result.exit_code == 0
    assert "hailuo" in result.output

def test_model_info(runner):
    result = runner.invoke(cli, ["model-info", "kling_2_6_pro"])
    assert result.exit_code == 0

def test_interpolate_help(runner):
    result = runner.invoke(cli, ["interpolate", "--help"])
    assert result.exit_code == 0
    assert "--start-frame" in result.output

def test_generate_missing_image(runner):
    result = runner.invoke(cli, ["generate", "--prompt", "test", "--model", "hailuo"])
    assert result.exit_code != 0  # Missing required --image
```

---

## Subtask 3: Migrate Unified Pipeline CLI from Argparse to Click

**Time estimate:** 45 minutes

### Files to modify

**File 1:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`
- Current: ~1,003 lines, argparse with 25+ subcommands
- Target: Click group with same commands, modular command registration

### What to build

This is the largest migration. The approach:

1. Create a top-level Click group `@click.group()` named `cli`
2. Convert each `cmd_*` handler + its argparse definition into a `@cli.command()` with `@click.option()` decorators
3. Keep all handler logic identical - only the argument parsing layer changes
4. Organize commands into logical Click subgroups where it makes sense

```python
# __main__.py - AFTER migration (structure)
import click

@click.group()
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.option("--base-dir", default=".", help="Base directory")
@click.pass_context
def cli(ctx, debug, base_dir):
    """AI Content Pipeline - Multi-modal AI content generation."""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["base_dir"] = base_dir


@cli.command("list-models")
def list_models():
    """List all supported AI models."""
    # ... (existing print_models() logic)


@cli.command("generate-image")
@click.option("--text", "-t", required=True, help="Text prompt")
@click.option("--model", "-m", default="flux_dev", help="Image model")
@click.option("--aspect-ratio", default="16:9")
@click.option("--resolution", default=None)
@click.option("--output-dir", "-o", default="output")
def generate_image(text, model, aspect_ratio, resolution, output_dir):
    """Generate image from text prompt."""
    # ... (existing generate_image() logic)


# ... (repeat for all 25 commands)


def main():
    cli()
```

### Key migration concerns for this file

- **25 commands** - largest migration surface
- **Global `--debug` and `--base-dir`** - use Click's `@click.pass_context` pattern
- **Some commands import lazily** (e.g., `analyze_video_command` imports `video_analysis` module) - keep lazy imports
- **Several commands have complex argument parsing** (e.g., `run-chain` with multiple config sources) - map carefully
- **Existing tests in `test_integration.py`** call `subprocess.run("ai-content-pipeline ...")` - these must still work

### Test updates

**File:** `tests/test_integration.py`
- The `test_console_scripts` test uses `subprocess.run()` so it will keep working as long as the entry point still exists (it will - Click CLIs work the same way from the shell)
- No changes needed to integration tests

**New file:** `tests/test_unified_cli.py` (targeted Click CliRunner tests)

```python
import pytest
from click.testing import CliRunner
from ai_content_pipeline.__main__ import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "AI Content Pipeline" in result.output

def test_list_models(runner):
    result = runner.invoke(cli, ["list-models"])
    assert result.exit_code == 0

def test_generate_image_help(runner):
    result = runner.invoke(cli, ["generate-image", "--help"])
    assert result.exit_code == 0
    assert "--text" in result.output

def test_generate_avatar_help(runner):
    result = runner.invoke(cli, ["generate-avatar", "--help"])
    assert result.exit_code == 0
```

---

## Subtask 4: Register Provider CLIs as Subgroups of Unified CLI

**Time estimate:** 15 minutes

### Files to modify

**File 1:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`
- Add provider CLI groups as nested subcommands

### What to build

After Subtasks 1-3, all CLIs are Click groups. Register the provider groups under the unified CLI:

```python
# __main__.py - add at end of command definitions
from fal_text_to_video.cli import cli as t2v_cli
from fal_image_to_video.cli import cli as i2v_cli

cli.add_command(t2v_cli, "t2v")
cli.add_command(i2v_cli, "i2v")
```

This enables:
```bash
# Standalone (backward compatible)
fal-text-to-video generate --prompt "..."

# As subgroup of unified CLI (new)
ai-content-pipeline t2v generate --prompt "..."
aicp t2v list-models
aicp i2v generate --image img.png --prompt "..."
```

### Test file

Add to `tests/test_unified_cli.py`:

```python
def test_t2v_subgroup(runner):
    result = runner.invoke(cli, ["t2v", "--help"])
    assert result.exit_code == 0
    assert "generate" in result.output

def test_i2v_subgroup(runner):
    result = runner.invoke(cli, ["i2v", "--help"])
    assert result.exit_code == 0
    assert "generate" in result.output
```

---

## Subtask 5: Cleanup and Verification

**Time estimate:** 15 minutes

### Files to modify

**File 1:** `setup.py` (lines 210-221)
- Verify all console_scripts entry points still work

**File 2:** `requirements.txt` or `setup.py`
- Ensure `click` is listed as a dependency (it should already be for ViMax)

### What to verify

1. Run full test suite: `python -m pytest tests/ -v`
2. Verify all entry points work:
   ```bash
   ai-content-pipeline --help
   aicp --help
   fal-text-to-video --help
   fal-image-to-video --help
   aicp t2v --help
   aicp i2v --help
   ```
3. Verify backward compatibility: all existing shell invocations produce same behavior
4. Remove any leftover argparse imports

### Test file

**New file:** `tests/test_cli_entry_points.py`

```python
"""Verify all CLI entry points are functional."""
import subprocess
import pytest

ENTRY_POINTS = [
    "ai-content-pipeline",
    "aicp",
    "fal-text-to-video",
    "fal-image-to-video",
]

@pytest.mark.parametrize("cmd", ENTRY_POINTS)
def test_entry_point_help(cmd):
    result = subprocess.run([cmd, "--help"], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    assert "Usage" in result.stdout or "usage" in result.stdout.lower()
```

---

## Implementation Order & Dependencies

```
Subtask 1: Migrate fal-text-to-video (30 min) ----+
                                                    |
Subtask 2: Migrate fal-image-to-video (30 min) ----+ (independent of 1)
                                                    |
Subtask 3: Migrate unified pipeline (45 min) ------+ (independent of 1,2)
                                                    |
         +------- all depend on 1,2,3 ------------+
         |
Subtask 4: Register as subgroups (15 min)
         |
Subtask 5: Cleanup and verification (15 min)
```

**Subtasks 1, 2, and 3 can be done in parallel** since each modifies a different CLI file.

**Total: ~2 hours 15 minutes**

---

## Impact After Implementation

| Metric | Before | After |
|---|---|---|
| CLI frameworks used | 2 (argparse + Click) | 1 (Click only) |
| Testability | subprocess only for argparse | CliRunner for all |
| Composability | Provider CLIs isolated | Provider CLIs nested under unified CLI |
| Help formatting | Inconsistent | Consistent Click style |
| Backward compatibility | N/A | All existing entry points preserved |
| New capability | None | `aicp t2v ...` and `aicp i2v ...` shortcuts |

---

## Files Summary

### Files to create
| File | Purpose |
|---|---|
| `tests/test_t2v_cli.py` | Click CliRunner tests for text-to-video CLI |
| `tests/test_i2v_cli.py` | Click CliRunner tests for image-to-video CLI |
| `tests/test_unified_cli.py` | Click CliRunner tests for unified pipeline CLI |
| `tests/test_cli_entry_points.py` | Entry point smoke tests |

### Files to modify
| File | Change |
|---|---|
| `packages/providers/fal/text-to-video/fal_text_to_video/cli.py` | Argparse → Click |
| `packages/providers/fal/image-to-video/fal_image_to_video/cli.py` | Argparse → Click |
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Argparse → Click + register subgroups |
| `setup.py` | Verify entry points (may need no changes) |

---

## References

- Click docs: https://click.palletsprojects.com/
- Current CLI issue: `issues/cli-redesign-unix-style.md` (Recommendation 4)
- Central registry PR: PR #19 (provides dynamic model lists used by CLIs)
- ViMax CLI (Click reference impl): `packages/core/ai_content_platform/vimax/cli/commands.py`
