# Unify CLI Framework: Migrate Argparse Provider CLIs to Click - COMPLETE

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

---

## Long-Term Strategy: Strangler Fig Migration

> **Principle: Migrate what's small and self-contained. Leave what works and is complex. Never rewrite 1,000 lines for cosmetic consistency.**

### Why NOT migrate `__main__.py` (the unified CLI)

The original plan called for migrating all 3 CLIs to Click in one shot. After deep analysis, **migrating `__main__.py` is high risk, low reward**:

| Factor | Provider CLIs (t2v, i2v) | Unified CLI (`__main__.py`) |
|--------|--------------------------|----------------------------|
| Size | 256 / 237 lines | **1,010 lines** |
| Commands | 4 each | **25 commands** |
| Handler coupling | Self-contained in same file | **18 handlers across 5 external modules** |
| Handler signature | N/A (inline) | **All take `args` namespace** (argparse-coupled) |
| `sys.exit()` calls | 0 | **12 across handler modules** |
| Tests affected | 0 existing tests | **3 test files use MagicMock(args)** |
| Risk of regression | Low | **High** |

**The 5 handler modules that would need changes if we migrated `__main__.py`:**
- `video_analysis.py` - `analyze_video_command(args)` accesses `args.model`, `args.input`, `args.output`, `args.type`, `args.debug` + 7 `sys.exit()` calls
- `motion_transfer.py` - `transfer_motion_command(args)` accesses `args.orientation`, `args.no_sound`, `args.image`, `args.video`, `args.output`, `args.prompt`, `args.save_json` + 2 `sys.exit()` calls
- `speech_to_text.py` - `transcribe_command(args)` accesses 11 `args.*` attributes + 1 `sys.exit()` call
- `grid_generator.py` - `generate_grid_command(args)` + `upscale_image_command(args)` access 13 combined `args.*` attributes + 2 `sys.exit()` calls
- `project_structure_cli.py` - 3 functions all take `args` with `hasattr` checks

**The 3 test files that would break:**
- `tests/test_video_analysis_cli.py` - Uses `MagicMock()` to simulate argparse `args` namespace
- `tests/test_speech_to_text_cli.py` - Same pattern
- `tests/test_motion_transfer_cli.py` - Same pattern

### What we DO migrate

| CLI | Action | Reason |
|-----|--------|--------|
| `fal-text-to-video` (256 lines, 4 commands) | **Migrate to Click** | Self-contained, small, enables CliRunner testing |
| `fal-image-to-video` (237 lines, 4 commands) | **Migrate to Click** | Self-contained, small, enables CliRunner testing |
| `__main__.py` (1,010 lines, 25 commands) | **Keep argparse** | Too coupled to external handlers, tests, and `sys.exit()` patterns |

**Estimated total implementation time: ~1 hour**

---

## Current Architecture

```text
ENTRY POINTS (setup.py lines 210-221):
  ai-content-pipeline  -> __main__.py:main()        [argparse, 25 commands]
  aicp                 -> __main__.py:main()        [alias]
  fal-text-to-video    -> fal_text_to_video/cli.py  [argparse, 4 commands]
  fal-image-to-video   -> fal_image_to_video/cli.py [argparse, 4 commands]
  vimax                -> vimax/cli/commands.py      [click, 11 commands]
```

## Target Architecture

```text
ENTRY POINTS (setup.py):
  ai-content-pipeline  -> __main__.py:main()        [argparse, 25 commands]  <- UNCHANGED
  aicp                 -> __main__.py:main()        [alias]                  <- UNCHANGED
  fal-text-to-video    -> fal_text_to_video/cli.py  [CLICK, 4 commands]     <- MIGRATED
  fal-image-to-video   -> fal_image_to_video/cli.py [CLICK, 4 commands]     <- MIGRATED
  vimax                -> vimax/cli/commands.py      [click, 11 commands]    <- UNCHANGED
```

Provider CLIs run standalone. Unified CLI stays argparse until handler modules are decoupled (tracked as future work).

---

## Subtask 1: Migrate `fal-text-to-video` CLI from Argparse to Click - DONE

**Time estimate:** 30 minutes

### File to modify

**`packages/providers/fal/text-to-video/fal_text_to_video/cli.py`**
- Current: 256 lines, argparse with 4 subcommands
- Target: Click group with 4 commands, identical behavior

### DELETE: Entire current file (256 lines)

The entire argparse-based implementation gets replaced.

### REPLACE WITH: Complete Click implementation

```python
#!/usr/bin/env python3
"""
CLI for FAL Text-to-Video Generation.

Usage:
    fal-text-to-video generate --prompt "A cat playing" --model kling_2_6_pro
    fal-text-to-video list-models
    fal-text-to-video model-info kling_2_6_pro
    fal-text-to-video estimate-cost --model sora_2_pro --duration 8 --resolution 1080p
"""

import sys

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
              help="Model to use (default: kling_2_6_pro)")
@click.option("--duration", "-d", default=None, help="Video duration (default: model-specific)")
@click.option("--aspect-ratio", "-a", default="16:9",
              type=click.Choice(["16:9", "9:16", "1:1", "4:3", "3:2", "2:3", "3:4"]),
              help="Aspect ratio (default: 16:9)")
@click.option("--resolution", "-r", default="720p",
              type=click.Choice(["480p", "720p", "1080p"]),
              help="Resolution (default: 720p)")
@click.option("--output", "-o", default="output", help="Output directory")
@click.option("--negative-prompt", default=None, help="Negative prompt (Kling only)")
@click.option("--cfg-scale", type=float, default=0.5, help="CFG scale 0-1 (Kling only)")
@click.option("--audio", is_flag=True, help="Generate audio (Kling only)")
@click.option("--keep-remote", is_flag=True, help="Keep video on remote server (Sora only)")
@click.option("--mock", is_flag=True, help="Mock mode: simulate without API call (FREE)")
def generate(prompt, model, duration, aspect_ratio, resolution, output,
             negative_prompt, cfg_scale, audio, keep_remote, mock):
    """Generate video from text prompt."""
    generator = FALTextToVideoGenerator(default_model=model)

    mock_label = " [MOCK]" if mock else ""
    print(f"\U0001f3ac Generating video with {model}{mock_label}...")
    print(f"   Prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

    kwargs = {}

    model_def = ModelRegistry.get(model)
    if duration:
        kwargs["duration"] = duration
    else:
        kwargs["duration"] = model_def.defaults.get("duration", "5")
    kwargs["aspect_ratio"] = aspect_ratio
    if cfg_scale is not None:
        kwargs["cfg_scale"] = cfg_scale
    if audio:
        kwargs["generate_audio"] = True
    if negative_prompt:
        kwargs["negative_prompt"] = negative_prompt
    if resolution:
        kwargs["resolution"] = resolution
    if keep_remote:
        kwargs["delete_video"] = False

    result = generator.generate_video(
        prompt=prompt,
        model=model,
        output_dir=output,
        verbose=True,
        mock=mock,
        **kwargs
    )

    if result.get("success"):
        print(f"\n\u2705 Success{'  [MOCK - No actual API call]' if result.get('mock') else ''}!")
        print(f"   \U0001f4c1 Output: {result.get('local_path')}")
        if result.get('mock'):
            print(f"   \U0001f4b0 Estimated cost: ${result.get('estimated_cost', 0):.2f} (not charged)")
        else:
            print(f"   \U0001f4b0 Cost: ${result.get('cost_usd', 0):.2f}")
            print(f"   \U0001f517 URL: {result.get('video_url', 'N/A')}")
        sys.exit(0)
    else:
        print(f"\n\u274c Failed: {result.get('error')}")
        sys.exit(1)


@cli.command("list-models")
def list_models():
    """List available text-to-video models."""
    generator = FALTextToVideoGenerator()

    print("\U0001f4cb Available Text-to-Video Models:")
    print("=" * 60)

    comparison = generator.compare_models()
    for model_key, info in comparison.items():
        print(f"\n\U0001f3a5 {info['name']} ({model_key})")
        print(f"   Provider: {info['provider']}")
        print(f"   Max duration: {info['max_duration']}s")
        print(f"   Pricing: {info['pricing']}")
        print(f"   Features: {', '.join(info['features'])}")


@cli.command("model-info")
@click.argument("model", type=click.Choice(T2V_MODELS, case_sensitive=True))
def model_info(model):
    """Show detailed model information."""
    generator = FALTextToVideoGenerator()

    try:
        info = generator.get_model_info(model)

        print(f"\n\U0001f4cb Model: {info.get('name', model)}")
        print("=" * 50)
        print(f"Provider: {info.get('provider', 'Unknown')}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Endpoint: {info.get('endpoint', 'N/A')}")
        print(f"Max duration: {info.get('max_duration', 'N/A')}s")

        print(f"\nFeatures:")
        for feature in info.get('features', []):
            print(f"   \u2022 {feature}")

        print(f"\nPricing:")
        pricing = info.get('pricing', {})
        for key, value in pricing.items():
            print(f"   \u2022 {key}: ${value}")

    except ValueError as e:
        print(f"\u274c Error: {e}")
        sys.exit(1)


@cli.command("estimate-cost")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(T2V_MODELS, case_sensitive=True),
              help="Model to estimate (default: kling_2_6_pro)")
@click.option("--duration", "-d", default=None, help="Video duration (default: model-specific)")
@click.option("--resolution", "-r", default="720p",
              type=click.Choice(["720p", "1080p"]),
              help="Resolution (Sora 2 Pro only)")
@click.option("--audio", is_flag=True, help="Include audio (Kling only)")
def estimate_cost(model, duration, resolution, audio):
    """Estimate cost for video generation."""
    generator = FALTextToVideoGenerator()

    try:
        kwargs = {}

        model_def = ModelRegistry.get(model)
        if duration:
            kwargs["duration"] = duration
        else:
            kwargs["duration"] = model_def.defaults.get("duration", "5")
        if audio:
            kwargs["generate_audio"] = True
        if resolution:
            kwargs["resolution"] = resolution

        cost = generator.estimate_cost(model=model, **kwargs)

        print(f"\n\U0001f4b0 Cost Estimate for {model}:")
        print(f"   Estimated cost: ${cost:.2f}")
        print(f"   Parameters: {kwargs}")

    except ValueError as e:
        print(f"\u274c Error: {e}")
        sys.exit(1)


def main():
    """Entry point for console_scripts."""
    cli()


if __name__ == "__main__":
    main()
```

### Migration mapping (argparse -> Click)

| Argparse (BEFORE) | Click (AFTER) | Notes |
|---|---|---|
| `parser = argparse.ArgumentParser(...)` | `@click.group()` | Group replaces parser |
| `subparsers.add_parser("generate")` | `@cli.command()` | Decorator replaces add_parser |
| `gen_parser.add_argument("--prompt", "-p", required=True)` | `@click.option("--prompt", "-p", required=True)` | 1:1 mapping |
| `gen_parser.add_argument("--model", choices=T2V_MODELS)` | `@click.option("--model", type=click.Choice(T2V_MODELS))` | `choices=` -> `type=click.Choice()` |
| `gen_parser.add_argument("--audio", action="store_true")` | `@click.option("--audio", is_flag=True)` | `action="store_true"` -> `is_flag=True` |
| `info_parser.add_argument("model", choices=...)` | `@click.argument("model", type=click.Choice(...))` | Positional arg stays as argument |
| `gen_parser.set_defaults(func=cmd_generate)` | N/A | Click routes automatically |
| `args = parser.parse_args(); args.func(args)` | `cli()` | Click handles dispatch |
| `def cmd_generate(args): args.prompt` | `def generate(prompt, ...): prompt` | Named params replace namespace |
| `if hasattr(args, "cfg_scale") and args.cfg_scale` | `if cfg_scale is not None:` | Simpler with Click defaults |

---

## Subtask 2: Migrate `fal-image-to-video` CLI from Argparse to Click - DONE

**Time estimate:** 30 minutes

### File to modify

**`packages/providers/fal/image-to-video/fal_image_to_video/cli.py`**
- Current: 237 lines, argparse with 4 subcommands
- Target: Click group with 4 commands, identical behavior

### DELETE: Entire current file (237 lines)

### REPLACE WITH: Complete Click implementation

```python
#!/usr/bin/env python3
"""
CLI for FAL Image-to-Video Generation.

Usage:
    fal-image-to-video generate --image path/to/image.png --model kling_2_6_pro --prompt "..."
    fal-image-to-video interpolate --start-frame start.png --end-frame end.png --prompt "..."
    fal-image-to-video list-models
    fal-image-to-video model-info kling_2_6_pro
"""

import sys

import click

from ai_content_pipeline.registry import ModelRegistry
import ai_content_pipeline.registry_data  # noqa: F401

from .generator import FALImageToVideoGenerator

I2V_MODELS = ModelRegistry.provider_keys_for_category("image_to_video")


@click.group()
def cli():
    """FAL Image-to-Video Generation CLI."""
    pass


@cli.command()
@click.option("--image", "-i", required=True, help="Input image path or URL")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(I2V_MODELS, case_sensitive=True),
              help="Model to use (default: kling_2_6_pro)")
@click.option("--prompt", "-p", required=True, help="Text prompt for video generation")
@click.option("--duration", "-d", default="5", help="Video duration (default: 5)")
@click.option("--output", "-o", default="output", help="Output directory")
@click.option("--end-frame", default=None, help="End frame for interpolation (Kling only)")
@click.option("--negative-prompt", default="blur, distortion, low quality", help="Negative prompt")
@click.option("--cfg-scale", type=float, default=0.5, help="CFG scale (0-1)")
@click.option("--audio", is_flag=True, help="Generate audio (Veo only)")
def generate(image, model, prompt, duration, output, end_frame,
             negative_prompt, cfg_scale, audio):
    """Generate video from image."""
    generator = FALImageToVideoGenerator()

    # Determine image source
    image_url = image
    start_frame = None

    # If it's a local file path, pass it via start_frame parameter.
    if not image_url.startswith(('http://', 'https://')):
        start_frame = image_url
        image_url = None

    print(f"\U0001f3ac Generating video with {model}...")
    print(f"   Image: {image}")
    print(f"   Duration: {duration}")
    if end_frame:
        print(f"   End frame: {end_frame}")

    result = generator.generate_video(
        prompt=prompt,
        image_url=image_url,
        model=model,
        start_frame=start_frame,
        end_frame=end_frame,
        duration=duration,
        output_dir=output,
        negative_prompt=negative_prompt,
        cfg_scale=cfg_scale,
        generate_audio=audio if audio else None,
    )

    if result.get("success"):
        print(f"\n\u2705 Success!")
        print(f"   \U0001f4c1 Output: {result.get('local_path')}")
        print(f"   \U0001f4b0 Cost: ${result.get('cost_estimate', 0):.2f}")
        print(f"   \u23f1\ufe0f Time: {result.get('processing_time', 0):.1f}s")
        sys.exit(0)
    else:
        print(f"\n\u274c Failed: {result.get('error')}")
        sys.exit(1)


@cli.command()
@click.option("--start-frame", "-s", required=True, help="Start frame image")
@click.option("--end-frame", "-e", required=True, help="End frame image")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(["kling_2_1", "kling_2_6_pro", "kling_3_standard", "kling_3_pro"]),
              help="Model for interpolation (Kling only)")
@click.option("--prompt", "-p", required=True, help="Text prompt")
@click.option("--duration", "-d", default="5", help="Duration")
def interpolate(start_frame, end_frame, model, prompt, duration):
    """Generate video interpolating between two frames."""
    generator = FALImageToVideoGenerator()

    print(f"\U0001f3ac Generating interpolation video...")
    print(f"   Start frame: {start_frame}")
    print(f"   End frame: {end_frame}")
    print(f"   Model: {model}")

    result = generator.generate_with_interpolation(
        prompt=prompt,
        start_frame=start_frame,
        end_frame=end_frame,
        model=model,
        duration=duration,
    )

    if result.get("success"):
        print(f"\n\u2705 Success!")
        print(f"   \U0001f4c1 Output: {result.get('local_path')}")
        print(f"   \U0001f4b0 Cost: ${result.get('cost_estimate', 0):.2f}")
        sys.exit(0)
    else:
        print(f"\n\u274c Failed: {result.get('error')}")
        sys.exit(1)


@cli.command("list-models")
def list_models():
    """List available image-to-video models."""
    generator = FALImageToVideoGenerator()

    print("\U0001f4cb Available Image-to-Video Models:")
    print("=" * 60)

    comparison = generator.compare_models()
    for model_key, info in comparison.items():
        print(f"\n\U0001f3a5 {info['name']} ({model_key})")
        print(f"   Provider: {info['provider']}")
        # Handle both simple float and dict pricing structures
        price = info['price_per_second']
        if isinstance(price, dict):
            prices = [f"${v:.3f}" for k, v in price.items()]
            print(f"   Price: {' / '.join(prices)}/second (varies by audio)")
        else:
            print(f"   Price: ${price:.2f}/second")
        print(f"   Max duration: {info['max_duration']}s")
        print(f"   Features: {', '.join(info['features'])}")


@cli.command("model-info")
@click.argument("model")
def model_info(model):
    """Show detailed model information."""
    generator = FALImageToVideoGenerator()

    try:
        info = generator.get_model_info(model)
        features = generator.get_model_features(model)

        print(f"\n\U0001f4cb Model: {info.get('name', model)}")
        print("=" * 50)
        print(f"Provider: {info.get('provider', 'Unknown')}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Endpoint: {info.get('endpoint', 'N/A')}")
        # Handle both simple float and dict pricing structures
        price = info.get('price_per_second', 0)
        if isinstance(price, dict):
            print("Pricing (per second):")
            for tier, cost in price.items():
                print(f"   - {tier}: ${cost:.3f}")
        else:
            print(f"Price: ${price:.2f}/second")
        print(f"Max duration: {info.get('max_duration', 'N/A')}s")

        print(f"\nFeatures:")
        for feature in info.get('features', []):
            print(f"   \u2022 {feature}")

        print(f"\nExtended Parameters:")
        for param, supported in features.items():
            status = "\u2705" if supported else "\u274c"
            print(f"   {status} {param}")

    except ValueError as e:
        print(f"\u274c Error: {e}")
        sys.exit(1)


def main():
    """Entry point for console_scripts."""
    cli()


if __name__ == "__main__":
    main()
```

---

## Subtask 3: Add Click CliRunner Tests for Provider CLIs - DONE

**Time estimate:** 15 minutes

### File to create: `tests/test_t2v_cli_click.py`

```python
"""Click CliRunner tests for fal-text-to-video CLI."""

import pytest
from click.testing import CliRunner
from fal_text_to_video.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestTextToVideoCLI:
    """Test fal-text-to-video Click CLI."""

    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "FAL Text-to-Video" in result.output

    def test_generate_help(self, runner):
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--prompt" in result.output
        assert "--model" in result.output
        assert "--duration" in result.output
        assert "--audio" in result.output
        assert "--mock" in result.output

    def test_list_models(self, runner):
        result = runner.invoke(cli, ["list-models"])
        assert result.exit_code == 0
        assert "Available Text-to-Video Models" in result.output

    def test_model_info(self, runner):
        result = runner.invoke(cli, ["model-info", "kling_2_6_pro"])
        assert result.exit_code == 0
        assert "Kling" in result.output

    def test_estimate_cost_help(self, runner):
        result = runner.invoke(cli, ["estimate-cost", "--help"])
        assert result.exit_code == 0
        assert "--model" in result.output
        assert "--duration" in result.output

    def test_generate_missing_prompt(self, runner):
        """Missing required --prompt should fail."""
        result = runner.invoke(cli, ["generate", "--model", "kling_2_6_pro"])
        assert result.exit_code != 0

    def test_generate_invalid_model(self, runner):
        """Invalid model name should fail."""
        result = runner.invoke(cli, ["generate", "--prompt", "test", "--model", "nonexistent"])
        assert result.exit_code != 0

    def test_no_command_shows_help(self, runner):
        """No subcommand should show help."""
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "Usage" in result.output
```

### File to create: `tests/test_i2v_cli_click.py`

```python
"""Click CliRunner tests for fal-image-to-video CLI."""

import pytest
from click.testing import CliRunner
from fal_image_to_video.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestImageToVideoCLI:
    """Test fal-image-to-video Click CLI."""

    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "FAL Image-to-Video" in result.output

    def test_generate_help(self, runner):
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--image" in result.output
        assert "--prompt" in result.output
        assert "--model" in result.output

    def test_list_models(self, runner):
        result = runner.invoke(cli, ["list-models"])
        assert result.exit_code == 0
        assert "Available Image-to-Video Models" in result.output

    def test_model_info(self, runner):
        result = runner.invoke(cli, ["model-info", "kling_2_6_pro"])
        assert result.exit_code == 0

    def test_interpolate_help(self, runner):
        result = runner.invoke(cli, ["interpolate", "--help"])
        assert result.exit_code == 0
        assert "--start-frame" in result.output
        assert "--end-frame" in result.output

    def test_generate_missing_image(self, runner):
        """Missing required --image should fail."""
        result = runner.invoke(cli, ["generate", "--prompt", "test", "--model", "hailuo"])
        assert result.exit_code != 0

    def test_generate_missing_prompt(self, runner):
        """Missing required --prompt should fail."""
        result = runner.invoke(cli, ["generate", "--image", "test.png", "--model", "hailuo"])
        assert result.exit_code != 0

    def test_no_command_shows_help(self, runner):
        """No subcommand should show help."""
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "Usage" in result.output
```

---

## Subtask 4: Verify setup.py and Dependencies - DONE

**Time estimate:** 10 minutes

### File to check: `setup.py`

**No changes needed to entry points** (lines 210-221). Both `fal-text-to-video` and `fal-image-to-video` still point to `cli:main`, and Click CLIs expose the same `main()` function signature.

```python
# setup.py lines 210-221 - UNCHANGED
entry_points={
    "console_scripts": [
        "ai-content-pipeline=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
        "aicp=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
        "vimax=packages.core.ai_content_platform.vimax.cli.commands:main",
        "fal-image-to-video=fal_image_to_video.cli:main",  # main() now calls cli()
        "fal-text-to-video=fal_text_to_video.cli:main",    # main() now calls cli()
    ],
},
```

### Dependency check: `click` in `setup.py`

Click is already an indirect dependency (via ViMax/ai_content_platform). But it should be added as a direct dependency:

**ADD** to `install_requires` list in `setup.py` (line 39-56):

```python
# BEFORE (line 39-56):
install_requires = [
    "python-dotenv>=1.0.0",
    "requests>=2.31.0",
    ...
    "argparse>=1.4.0",     # <-- can remove, argparse is stdlib since Python 2.7
    ...
]

# AFTER:
install_requires = [
    "python-dotenv>=1.0.0",
    "requests>=2.31.0",
    ...
    "click>=8.0.0",        # <-- ADD: CLI framework for provider CLIs and ViMax
    ...
]
```

**DELETE** the `argparse>=1.4.0` line - argparse has been part of the Python standard library since Python 2.7. This dependency is unnecessary.

---

## Subtask 5: Verification - DONE

**Time estimate:** 10 minutes

### Run tests

```bash
# Full test suite
python -m pytest tests/ -v

# Specifically the new CLI tests
python -m pytest tests/test_t2v_cli_click.py tests/test_i2v_cli_click.py -v

# Verify entry points still work
fal-text-to-video --help
fal-image-to-video --help
fal-text-to-video list-models
fal-image-to-video list-models
```

### Existing tests that should still pass

| Test File | Status | Why |
|-----------|--------|-----|
| `tests/test_integration.py` | **Pass** | Uses subprocess, entry points unchanged |
| `tests/test_video_analysis_cli.py` | **Pass** | Tests handler modules, not CLI framework |
| `tests/test_speech_to_text_cli.py` | **Pass** | Tests handler modules, not CLI framework |
| `tests/test_motion_transfer_cli.py` | **Pass** | Tests handler modules, not CLI framework |
| `tests/test_auto_discovery.py` | **Pass** | Tests registry, unrelated |
| `tests/test_registry.py` | **Pass** | Tests registry, unrelated |

---

## Implementation Order & Dependencies

```text
Subtask 1: Migrate fal-text-to-video CLI (30 min) ----+
                                                        |
Subtask 2: Migrate fal-image-to-video CLI (30 min) ----+ (parallel with 1)
                                                        |
         +------- depends on 1 and 2 -----------------+
         |
Subtask 3: Add CliRunner tests (15 min)
         |
Subtask 4: Verify setup.py + deps (10 min)  (parallel with 3)
         |
Subtask 5: Run full verification (10 min)
```

**Total: ~1 hour**

---

## Impact After Implementation

| Metric | Before | After |
|---|---|---|
| Provider CLI framework | argparse | Click |
| Provider CLI testability | MagicMock args only | CliRunner + MagicMock |
| Unified CLI framework | argparse | argparse (unchanged) |
| Handler modules touched | 0 | 0 |
| Existing tests broken | 0 | 0 |
| Entry points changed | 0 | 0 |
| New CliRunner tests | 0 | ~16 tests across 2 files |

---

## Future Work (NOT in this PR)

### Phase 2: Migrate `__main__.py` to Click (when handler modules are decoupled)

This becomes viable when:
1. Handler modules accept keyword arguments instead of `args` namespace
2. Handler modules use exceptions instead of `sys.exit()`
3. Existing CLI tests are migrated to CliRunner

**Pre-requisite refactoring for each handler module:**

```python
# CURRENT pattern in video_analysis.py, motion_transfer.py, etc:
def analyze_video_command(args):
    model = args.model       # <-- coupled to argparse namespace
    input_path = args.input  # <-- coupled to argparse namespace
    sys.exit(1)              # <-- anti-pattern for Click

# TARGET pattern (future):
def analyze_video_command(*, model, input, output, type, debug=False):
    model = model            # <-- keyword arguments, framework-agnostic
    raise click.ClickException("...")  # <-- Click-native error handling
```

**Modules to refactor (5 files, 18 functions):**
- `video_analysis.py`: `analyze_video_command(args)` -> `analyze_video_command(*, model, input, output, type, debug=False)`
- `motion_transfer.py`: `transfer_motion_command(args)` -> `transfer_motion_command(*, image, video, output, orientation, no_sound, prompt, save_json)`
- `speech_to_text.py`: `transcribe_command(args)` -> `transcribe_command(*, input, output, language, diarize, tag_events, keyterms, save_json, raw_json, srt, srt_max_words, srt_max_duration)`
- `grid_generator.py`: 2 functions
- `project_structure_cli.py`: 3 functions

**Tests to update (3 files):**
- `tests/test_video_analysis_cli.py`: Replace `MagicMock()` args with keyword calls or CliRunner
- `tests/test_speech_to_text_cli.py`: Same
- `tests/test_motion_transfer_cli.py`: Same

### Phase 3: Register provider CLIs as unified CLI subgroups

Once `__main__.py` is Click-based (Phase 2), add:

```python
# __main__.py
from fal_text_to_video.cli import cli as t2v_cli
from fal_image_to_video.cli import cli as i2v_cli

cli.add_command(t2v_cli, "t2v")
cli.add_command(i2v_cli, "i2v")
```

This enables `aicp t2v generate --prompt "..."` and `aicp i2v generate --image img.png --prompt "..."`.

---

## Files Summary

### Files to create
| File | Purpose | Lines |
|---|---|---|
| `tests/test_t2v_cli_click.py` | Click CliRunner tests for text-to-video | ~60 |
| `tests/test_i2v_cli_click.py` | Click CliRunner tests for image-to-video | ~60 |

### Files to modify
| File | Change | Risk |
|---|---|---|
| `packages/providers/fal/text-to-video/fal_text_to_video/cli.py` | Full rewrite: argparse -> Click | Low (self-contained) |
| `packages/providers/fal/image-to-video/fal_image_to_video/cli.py` | Full rewrite: argparse -> Click | Low (self-contained) |
| `setup.py` | Add `click>=8.0.0` dep, remove `argparse>=1.4.0` | Minimal |

### Files NOT modified (explicitly preserved)
| File | Why |
|---|---|
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | 1,010 lines, 25 commands, 18 coupled handlers - too risky |
| `ai_content_pipeline/video_analysis.py` | Handler takes `args` namespace, 7 `sys.exit()` calls |
| `ai_content_pipeline/motion_transfer.py` | Handler takes `args` namespace, 2 `sys.exit()` calls |
| `ai_content_pipeline/speech_to_text.py` | Handler takes `args` namespace, 1 `sys.exit()` call |
| `ai_content_pipeline/grid_generator.py` | 2 handlers take `args` namespace, 2 `sys.exit()` calls |
| `ai_content_pipeline/project_structure_cli.py` | 3 handlers take `args` namespace |
| `tests/test_video_analysis_cli.py` | Uses MagicMock args, still works |
| `tests/test_speech_to_text_cli.py` | Uses MagicMock args, still works |
| `tests/test_motion_transfer_cli.py` | Uses MagicMock args, still works |
| `tests/test_integration.py` | Uses subprocess, still works |

---

## References

- Click docs: https://click.palletsprojects.com/
- Current CLI issue: `issues/cli-redesign-unix-style.md` (Recommendation 5)
- Central registry PR: PR #19 (provides dynamic model lists used by CLIs)
- ViMax CLI (Click reference impl): `packages/core/ai_content_platform/vimax/cli/commands.py`
- ViMax CLI tests (CliRunner reference): `tests/unit/vimax/test_cli.py`
