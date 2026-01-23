# Generate Grid CLI Implementation Plan

**Feature:** Add CLI commands for image grid generation (2x2, 3x3) and upscaling
**Created:** 2026-01-22
**Completed:** 2026-01-22
**Status:** ✅ IMPLEMENTED (CLI) | ✅ IMPLEMENTED (YAML Pipeline Split)
**Priority:** Medium
**Branch:** shot

---

# Phase 2: YAML Pipeline with Split & Upscale

**Feature:** Enable complete grid workflow (generate → split → upscale) via single YAML pipeline
**Created:** 2026-01-23
**Completed:** 2026-01-23
**Status:** ✅ IMPLEMENTED

## Overview

Add `split_image` and `upscale_image` step types to the YAML pipeline system, enabling:

```
Text Prompt → Generate 2x2/3x3 Grid → Split into 4/9 Panels → Upscale Each Panel
```

All configurable via a single YAML file.

## Current Gap

**What exists:**
- `generate-grid` CLI generates 2x2/3x3 composite images ✅
- `upscale-image` CLI upscales single images ✅
- YAML pipeline with 12+ step types ✅

**Now implemented:**
- `split_image` step type to divide grid into individual panels ✅
- `upscale_image` step type for image upscaling ✅

## Target YAML Configuration

```yaml
name: "grid_split_upscale_pipeline"
description: "Generate 2x2 grid, split into panels, upscale each"

steps:
  # Step 1: Generate 2x2 grid image
  - name: "generate_grid"
    type: "text_to_image"
    model: "nano_banana_pro"
    params:
      prompt: |
        A 2x2 grid of 4 panels showing:
        Panel 1 (top-left): A sunrise over mountains
        Panel 2 (top-right): A forest at noon
        Panel 3 (bottom-left): A beach at sunset
        Panel 4 (bottom-right): A city at night
        Style: cinematic, vibrant colors

  # Step 2: Split grid into individual panels
  - name: "split_panels"
    type: "split_image"
    params:
      grid: "2x2"           # or "3x3"
      output_format: "png"
      naming: "panel_{n}"   # panel_1.png, panel_2.png, etc.

output_dir: "output/grid_pipeline"
save_intermediates: true
```

## Implementation Plan

### Subtask 2.1: Create Image Splitter Utility (15 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/image_splitter.py`

```python
"""
Image splitting utility for grid images.
Splits 2x2 or 3x3 grid images into individual panels.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image


@dataclass
class SplitConfig:
    """Configuration for image splitting."""
    grid: str = "2x2"              # "2x2" or "3x3"
    output_format: str = "png"     # png, jpg, webp
    naming_pattern: str = "panel_{n}"  # {n} = panel number
    quality: int = 95              # JPEG quality


GRID_CONFIGS = {
    "2x2": {"rows": 2, "cols": 2, "panels": 4},
    "3x3": {"rows": 3, "cols": 3, "panels": 9},
}


def split_grid_image(
    image_path: str,
    output_dir: str,
    config: Optional[SplitConfig] = None
) -> List[str]:
    """
    Split a grid image into individual panels.

    Args:
        image_path: Path to the grid image
        output_dir: Directory to save split panels
        config: Split configuration

    Returns:
        List of paths to the split panel images
    """
    config = config or SplitConfig()

    if config.grid not in GRID_CONFIGS:
        raise ValueError(f"Invalid grid: {config.grid}")

    grid_info = GRID_CONFIGS[config.grid]
    rows, cols = grid_info["rows"], grid_info["cols"]

    img = Image.open(image_path)
    width, height = img.size
    panel_width = width // cols
    panel_height = height // rows

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    panel_paths = []
    panel_num = 1

    for row in range(rows):
        for col in range(cols):
            left = col * panel_width
            upper = row * panel_height
            right = left + panel_width
            lower = upper + panel_height

            panel = img.crop((left, upper, right, lower))

            filename = config.naming_pattern.replace("{n}", str(panel_num))
            filename = f"{filename}.{config.output_format}"
            panel_path = output_path / filename

            if config.output_format.lower() == "jpg":
                panel.save(panel_path, "JPEG", quality=config.quality)
            else:
                panel.save(panel_path)

            panel_paths.append(str(panel_path))
            panel_num += 1

    return panel_paths
```

---

### Subtask 2.2: Add Step Types to Chain (5 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/chain.py`

Add to `StepType` enum:
```python
class StepType(Enum):
    # ... existing ...
    SPLIT_IMAGE = "split_image"
    UPSCALE_IMAGE = "upscale_image"
```

Add type mappings:
```python
STEP_INPUT_TYPES = {
    # ... existing ...
    StepType.SPLIT_IMAGE: "image",
    StepType.UPSCALE_IMAGE: "image",
}

STEP_OUTPUT_TYPES = {
    # ... existing ...
    StepType.SPLIT_IMAGE: "images",  # Multiple outputs
    StepType.UPSCALE_IMAGE: "image",
}
```

---

### Subtask 2.3: Create Step Executors (15 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/image_steps.py`

```python
from ...image_splitter import split_grid_image, SplitConfig
from ...grid_generator import upscale_image

class SplitImageExecutor(BaseStepExecutor):
    """Executor for splitting grid images into panels."""

    def execute(self, step, input_data, chain_config, step_context, **kwargs):
        start_time = time.time()
        params = step.params or {}

        try:
            image_path = input_data
            if isinstance(input_data, dict):
                image_path = input_data.get("output_path") or input_data.get("path")

            if not image_path:
                return {"success": False, "error": "No input image"}

            config = SplitConfig(
                grid=params.get("grid", "2x2"),
                output_format=params.get("output_format", "png"),
                naming_pattern=params.get("naming", "panel_{n}"),
            )

            output_dir = chain_config.get("output_dir", "output")
            step_output_dir = Path(output_dir) / step.name

            panel_paths = split_grid_image(image_path, str(step_output_dir), config)

            return {
                "success": True,
                "output_paths": panel_paths,
                "output_path": panel_paths[0] if panel_paths else None,
                "panel_count": len(panel_paths),
                "processing_time": time.time() - start_time,
                "cost": 0,  # Local operation
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class UpscaleImageExecutor(BaseStepExecutor):
    """Executor for upscaling images using SeedVR2."""

    def execute(self, step, input_data, chain_config, step_context, **kwargs):
        start_time = time.time()
        params = step.params or {}

        try:
            image_path = input_data
            if isinstance(input_data, dict):
                image_path = input_data.get("output_path") or input_data.get("path")

            if not image_path:
                return {"success": False, "error": "No input image"}

            output_dir = chain_config.get("output_dir", "output")

            result = upscale_image(
                image_path=image_path,
                factor=params.get("factor", 2),
                target=params.get("target"),
                output_dir=output_dir,
                output_format=params.get("output_format", "png"),
            )

            if not result.success:
                return {"success": False, "error": result.error}

            return {
                "success": True,
                "output_path": result.local_path,
                "output_url": result.image_url,
                "upscaled_size": result.upscaled_size,
                "processing_time": result.processing_time,
                "cost": result.cost,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

---

### Subtask 2.4: Register Executors (5 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/manager.py`

```python
from .step_executors.image_steps import (
    # ... existing ...
    SplitImageExecutor,
    UpscaleImageExecutor,
)

# In _get_step_executor method:
step_executors = {
    # ... existing ...
    StepType.SPLIT_IMAGE: SplitImageExecutor,
    StepType.UPSCALE_IMAGE: UpscaleImageExecutor,
}
```

---

### Subtask 2.5: Unit Tests (10 min)

**File:** `tests/test_image_splitter.py`

```python
"""Unit tests for image_splitter module."""

import pytest
from pathlib import Path
from PIL import Image
import tempfile
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "packages/core/ai_content_pipeline"))

from ai_content_pipeline.image_splitter import (
    split_grid_image, SplitConfig, GRID_CONFIGS
)


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


@pytest.fixture
def sample_2x2_image(temp_dir):
    """Create sample 2x2 grid image."""
    img = Image.new("RGB", (1024, 1024), "white")
    path = Path(temp_dir) / "grid.png"
    img.save(path)
    return str(path)


class TestSplitGridImage:
    def test_split_2x2(self, sample_2x2_image, temp_dir):
        """2x2 grid splits into 4 panels."""
        output_dir = Path(temp_dir) / "output"
        paths = split_grid_image(sample_2x2_image, str(output_dir), SplitConfig(grid="2x2"))

        assert len(paths) == 4
        for p in paths:
            assert Path(p).exists()
            img = Image.open(p)
            assert img.size == (512, 512)

    def test_split_3x3(self, temp_dir):
        """3x3 grid splits into 9 panels."""
        img = Image.new("RGB", (900, 900), "white")
        path = Path(temp_dir) / "grid3x3.png"
        img.save(path)

        output_dir = Path(temp_dir) / "output"
        paths = split_grid_image(str(path), str(output_dir), SplitConfig(grid="3x3"))

        assert len(paths) == 9

    def test_invalid_grid_raises(self, sample_2x2_image, temp_dir):
        """Invalid grid raises ValueError."""
        with pytest.raises(ValueError):
            split_grid_image(sample_2x2_image, temp_dir, SplitConfig(grid="5x5"))


class TestSplitConfig:
    def test_defaults(self):
        config = SplitConfig()
        assert config.grid == "2x2"
        assert config.output_format == "png"
        assert config.naming_pattern == "panel_{n}"
```

---

## File Summary (Phase 2)

| File | Action | Est. Time |
|------|--------|-----------|
| `ai_content_pipeline/image_splitter.py` | **Create** | 15 min |
| `ai_content_pipeline/pipeline/chain.py` | Modify | 5 min |
| `ai_content_pipeline/pipeline/step_executors/image_steps.py` | Modify | 15 min |
| `ai_content_pipeline/pipeline/manager.py` | Modify | 5 min |
| `tests/test_image_splitter.py` | **Create** | 10 min |

**Total Phase 2:** ~45 minutes

---

## CLI Usage After Phase 2

```bash
# Run grid split pipeline
./venv/Scripts/aicp.exe run-chain --config input/pipelines/grid_2x2_split.yaml
```

---

## Benefits

1. **Single YAML File**: Complete workflow in one configuration
2. **Reusable Module**: Split utility works standalone or in pipelines
3. **Extensible**: Easy to add more grid sizes
4. **Cost Efficient**: Splitting is local (free)
5. **Follows Patterns**: Consistent with existing pipeline architecture

---

# Phase 1: CLI Commands (Original Implementation Below)

## Overview

Implement two CLI commands:
1. `generate-grid` - Generate 2x2 or 3x3 image grids from prompt files (single API call)
2. `upscale-image` - Upscale images using SeedVR2 API

## Features

### Grid Generation
- Support **2x2** (4 panels) and **3x3** (9 panels) layouts
- Single API call per grid (no stitching)
- Prompt-based layout description
- Optional upscaling after generation

### Image Upscaling
- SeedVR2 API: `fal-ai/seedvr/upscale/image`
- Factor mode: 1x-8x upscale
- Target mode: 720p, 1080p, 1440p, 2160p
- Local file and URL support

## Target CLI Usage

```bash
# Generate 3x3 grid (default)
aicp generate-grid --prompt-file storyboard.md

# Generate 2x2 grid
aicp generate-grid --prompt-file storyboard.md --grid 2x2

# Generate and upscale
aicp generate-grid --prompt-file storyboard.md --upscale 2

# Upscale existing image
aicp upscale-image -i image.png --factor 2

# Upscale to target resolution
aicp upscale-image -i image.png --target 1080p

# Upscale from URL
aicp upscale-image -i "https://example.com/image.jpg" --target 2160p
```

## Prompt File Format

```markdown
# My Storyboard

## Style
2000s music video aesthetic, film grain, golden hour

## Panels
1. Wide shot of characters on a porch
2. Close-up of person looking at phone
3. Macro shot of phone screen
4. Medium shot of two people leaning in
5. Low-angle fisheye of trio walking
6. Medium shot on couch with green glow
7. News graphic overlay of group dancing
8. Over-the-shoulder shot of phone
9. Final wide shot, trio staring at camera
```

For 2x2 grid, only first 4 panels are used.

---

## Implementation Subtasks

### Subtask 1: Create Grid Generator Module (12 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/grid_generator.py`

```python
"""
Grid generator and image upscaler CLI commands.

- generate-grid: Generate 2x2 or 3x3 image grids
- upscale-image: Upscale images using SeedVR2
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Try to import FAL client
try:
    import fal_client
    FAL_CLIENT_AVAILABLE = True
except ImportError:
    FAL_CLIENT_AVAILABLE = False

from .pipeline.manager import AIPipelineManager


# Grid configurations
GRID_CONFIGS = {
    "2x2": {"rows": 2, "cols": 2, "panels": 4},
    "3x3": {"rows": 3, "cols": 3, "panels": 9},
}

DEFAULTS = {
    "model": "nano_banana_pro",
    "grid": "3x3",
    "aspect_ratio": "1:1",
    "output_dir": "output",
}

MODEL_COSTS = {
    "nano_banana_pro": 0.002,
    "flux_schnell": 0.001,
    "flux_dev": 0.003,
}

# Upscale configurations
UPSCALE_ENDPOINT = "fal-ai/seedvr/upscale/image"
UPSCALE_TARGETS = ["720p", "1080p", "1440p", "2160p"]
UPSCALE_COST_ESTIMATE = 0.01  # Estimated cost per upscale


@dataclass
class GridGenerationResult:
    """Result from grid generation."""
    success: bool
    image_url: Optional[str] = None
    local_path: Optional[str] = None
    prompt_used: Optional[str] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UpscaleResult:
    """Result from image upscaling."""
    success: bool
    image_url: Optional[str] = None
    local_path: Optional[str] = None
    original_size: Optional[Tuple[int, int]] = None
    upscaled_size: Optional[Tuple[int, int]] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def parse_prompt_file(file_path: str) -> Dict[str, Any]:
    """
    Parse markdown prompt file into structured data.

    Expected format:
    # Title
    ## Style
    style description
    ## Panels
    1. Panel 1 description
    2. Panel 2 description
    ...
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {
        "title": "",
        "style": "",
        "panels": [],
        "raw_content": content,
    }

    # Extract title
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Extract style section
    style_match = re.search(
        r'##\s*(?:Style|STYLE|Technical Specs|TECHNICAL SPECS).*?\n(.*?)(?=##|\Z)',
        content, re.DOTALL | re.IGNORECASE
    )
    if style_match:
        style_text = style_match.group(1).strip()
        # Clean up bullet points and formatting
        style_lines = [line.strip().lstrip('*-•').strip()
                      for line in style_text.split('\n') if line.strip()]
        result["style"] = ", ".join(style_lines)

    # Extract panels
    panels_match = re.search(
        r'##\s*(?:Panels|PANELS|PANELS & LAYOUT).*?\n(.*?)(?=##|\Z)',
        content, re.DOTALL | re.IGNORECASE
    )
    if panels_match:
        panels_text = panels_match.group(1)
        # Match various formats: "1.", "* **Panel 1:**", "- Panel 1:", etc.
        panel_items = re.findall(
            r'(?:^|\n)\s*(?:\d+\.|\*|\-)\s*\*?\*?(?:Panel\s*\d+:?\s*\*?\*?)?\s*(.+?)(?=\n\s*(?:\d+\.|\*|\-)|\n\n|\Z)',
            panels_text, re.DOTALL
        )
        result["panels"] = [p.strip().replace('\n', ' ') for p in panel_items if p.strip()]

    return result


def format_grid_prompt(
    parsed: Dict[str, Any],
    grid_size: str = "3x3",
    style_override: Optional[str] = None
) -> str:
    """Format parsed prompt data into a single grid generation prompt."""
    config = GRID_CONFIGS.get(grid_size, GRID_CONFIGS["3x3"])
    num_panels = config["panels"]
    rows = config["rows"]
    cols = config["cols"]

    panels = parsed.get("panels", [])
    style = style_override or parsed.get("style", "")

    # Build the prompt
    prompt_parts = [
        f"A {rows}x{cols} grid of {num_panels} panels showing a chronological sequence:",
    ]

    for i, panel in enumerate(panels[:num_panels], 1):
        prompt_parts.append(f"Panel {i}: {panel}")

    if style:
        prompt_parts.append(f"Style: {style}")

    return " ".join(prompt_parts)


def upload_if_local(file_path: str) -> str:
    """Upload local file to FAL if needed, return URL."""
    if file_path.startswith(("http://", "https://")):
        return file_path

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not FAL_CLIENT_AVAILABLE:
        raise RuntimeError("fal-client not installed")

    print(f"📤 Uploading: {path.name}")
    url = fal_client.upload_file(str(path))
    print(f"✅ Uploaded: {url[:60]}...")
    return url


def upscale_image(
    image_path: str,
    factor: Optional[float] = None,
    target: Optional[str] = None,
    output_dir: str = "output",
    output_format: str = "png",
    noise_scale: float = 0.1,
) -> UpscaleResult:
    """
    Upscale an image using SeedVR2 API.

    Args:
        image_path: Local path or URL to image
        factor: Upscale factor (1-8), mutually exclusive with target
        target: Target resolution (720p, 1080p, 1440p, 2160p)
        output_dir: Output directory
        output_format: Output format (png, jpg, webp)
        noise_scale: Noise scale (0-1)

    Returns:
        UpscaleResult with upscaled image details
    """
    import time
    start_time = time.time()

    if not FAL_CLIENT_AVAILABLE:
        return UpscaleResult(success=False, error="fal-client not installed")

    if not os.getenv("FAL_KEY"):
        return UpscaleResult(success=False, error="FAL_KEY not set")

    # Determine upscale mode
    if target and factor:
        return UpscaleResult(success=False, error="Cannot specify both factor and target")

    if not target and not factor:
        factor = 2  # Default to 2x

    try:
        # Upload if local
        image_url = upload_if_local(image_path)

        # Build request
        arguments = {
            "image_url": image_url,
            "noise_scale": noise_scale,
            "output_format": output_format,
        }

        if target:
            arguments["upscale_mode"] = "target"
            arguments["target_resolution"] = target
        else:
            arguments["upscale_mode"] = "factor"
            arguments["upscale_factor"] = factor

        print(f"\n🔍 Upscaling image...")
        if target:
            print(f"   Target: {target}")
        else:
            print(f"   Factor: {factor}x")

        # Call API
        result = fal_client.subscribe(
            UPSCALE_ENDPOINT,
            arguments=arguments,
            with_logs=False,
        )

        if not result or "image" not in result:
            return UpscaleResult(success=False, error="No image in response")

        image_data = result["image"]
        image_url = image_data.get("url")
        width = image_data.get("width")
        height = image_data.get("height")

        # Download result
        local_path = None
        if image_url:
            import requests
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"upscaled_{timestamp}.{output_format}"
            local_path = output_path / filename

            response = requests.get(image_url, timeout=60)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                f.write(response.content)
            local_path = str(local_path)

        processing_time = time.time() - start_time

        return UpscaleResult(
            success=True,
            image_url=image_url,
            local_path=local_path,
            upscaled_size=(width, height) if width and height else None,
            cost=UPSCALE_COST_ESTIMATE,
            processing_time=processing_time,
            metadata={
                "mode": "target" if target else "factor",
                "target": target,
                "factor": factor,
                "noise_scale": noise_scale,
                "output_format": output_format,
            }
        )

    except Exception as e:
        return UpscaleResult(success=False, error=str(e))


def generate_grid(
    prompt_file: str,
    model: str = "nano_banana_pro",
    grid_size: str = "3x3",
    style_override: Optional[str] = None,
    output_dir: str = "output",
    aspect_ratio: str = "1:1",
    upscale_factor: Optional[float] = None,
) -> GridGenerationResult:
    """
    Generate a grid image from a prompt file.

    Args:
        prompt_file: Path to markdown prompt file
        model: Model to use for generation
        grid_size: Grid size ("2x2" or "3x3")
        style_override: Optional style to override prompt file style
        output_dir: Output directory
        aspect_ratio: Aspect ratio for the image
        upscale_factor: Optional upscale factor after generation

    Returns:
        GridGenerationResult with image details
    """
    import time
    start_time = time.time()

    # Validate grid size
    if grid_size not in GRID_CONFIGS:
        return GridGenerationResult(
            success=False,
            error=f"Invalid grid size: {grid_size}. Use: {', '.join(GRID_CONFIGS.keys())}"
        )

    config = GRID_CONFIGS[grid_size]

    # Parse prompt file
    try:
        parsed = parse_prompt_file(prompt_file)
    except Exception as e:
        return GridGenerationResult(success=False, error=f"Failed to parse prompt file: {e}")

    if len(parsed["panels"]) < config["panels"]:
        return GridGenerationResult(
            success=False,
            error=f"Need {config['panels']} panels for {grid_size} grid, found {len(parsed['panels'])}"
        )

    # Format the prompt
    prompt = format_grid_prompt(parsed, grid_size, style_override)

    # Generate image
    try:
        manager = AIPipelineManager()
        result = manager.text_to_image.generate(
            prompt=prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            output_format="png",
        )

        if not result.get("success", False) and not result.get("image_url"):
            return GridGenerationResult(
                success=False,
                error=result.get("error", "Generation failed"),
            )

        image_url = result.get("image_url")
        local_path = result.get("local_path")
        total_cost = MODEL_COSTS.get(model, 0.002)

        # Upscale if requested
        if upscale_factor and local_path:
            print(f"\n📈 Upscaling {upscale_factor}x...")
            upscale_result = upscale_image(
                image_path=local_path,
                factor=upscale_factor,
                output_dir=output_dir,
            )
            if upscale_result.success:
                image_url = upscale_result.image_url
                local_path = upscale_result.local_path
                total_cost += upscale_result.cost or 0

        processing_time = time.time() - start_time

        return GridGenerationResult(
            success=True,
            image_url=image_url,
            local_path=local_path,
            prompt_used=prompt,
            cost=total_cost,
            processing_time=processing_time,
            metadata={
                "model": model,
                "grid_size": grid_size,
                "title": parsed.get("title"),
                "panels": parsed["panels"][:config["panels"]],
                "style": style_override or parsed.get("style"),
                "upscaled": upscale_factor is not None,
            }
        )

    except Exception as e:
        return GridGenerationResult(success=False, error=f"Generation error: {e}")


def generate_grid_command(args) -> None:
    """Handle generate-grid CLI command."""
    load_dotenv()

    grid_size = args.grid
    config = GRID_CONFIGS.get(grid_size, GRID_CONFIGS["3x3"])

    # Print header
    print(f"\n🖼️  IMAGE GRID GENERATOR")
    print("=" * 50)
    print(f"📄 Prompt file: {args.prompt_file}")
    print(f"📐 Grid: {grid_size} ({config['panels']} panels)")
    print(f"🤖 Model: {args.model}")
    if args.style:
        print(f"🎨 Style override: {args.style}")
    if args.upscale:
        print(f"📈 Upscale: {args.upscale}x")
    print(f"📁 Output: {args.output}")

    cost = MODEL_COSTS.get(args.model, 0.002)
    if args.upscale:
        cost += UPSCALE_COST_ESTIMATE
    print(f"💰 Estimated cost: ${cost:.3f}")
    print()

    # Generate grid
    result = generate_grid(
        prompt_file=args.prompt_file,
        model=args.model,
        grid_size=grid_size,
        style_override=args.style,
        output_dir=args.output,
        upscale_factor=args.upscale,
    )

    # Display results
    if result.success:
        print(f"\n✅ Grid generated successfully!")
        if result.local_path:
            print(f"📁 Output: {result.local_path}")
        elif result.image_url:
            print(f"🔗 URL: {result.image_url}")
        if result.cost:
            print(f"💰 Cost: ${result.cost:.4f}")
        if result.processing_time:
            print(f"⏱️  Processing: {result.processing_time:.1f}s")

        # Save JSON if requested
        if args.save_json:
            json_path = Path(args.output) / args.save_json
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "success": True,
                    "image_url": result.image_url,
                    "local_path": result.local_path,
                    "prompt_used": result.prompt_used,
                    "cost": result.cost,
                    "processing_time": result.processing_time,
                    "metadata": result.metadata,
                }, f, indent=2)
            print(f"📄 Metadata: {json_path}")
    else:
        print(f"\n❌ Grid generation failed!")
        print(f"   Error: {result.error}")
        sys.exit(1)


def upscale_image_command(args) -> None:
    """Handle upscale-image CLI command."""
    load_dotenv()

    # Print header
    print(f"\n🔍 IMAGE UPSCALER (SeedVR2)")
    print("=" * 50)
    print(f"📁 Input: {args.input}")
    if args.target:
        print(f"🎯 Target: {args.target}")
    else:
        print(f"📈 Factor: {args.factor}x")
    print(f"📁 Output: {args.output}")
    print(f"💰 Estimated cost: ${UPSCALE_COST_ESTIMATE:.3f}")
    print()

    # Upscale
    result = upscale_image(
        image_path=args.input,
        factor=args.factor if not args.target else None,
        target=args.target,
        output_dir=args.output,
        output_format=args.format,
    )

    # Display results
    if result.success:
        print(f"\n✅ Upscale complete!")
        if result.local_path:
            print(f"📁 Output: {result.local_path}")
        elif result.image_url:
            print(f"🔗 URL: {result.image_url}")
        if result.upscaled_size:
            print(f"📐 Size: {result.upscaled_size[0]}x{result.upscaled_size[1]}")
        if result.cost:
            print(f"💰 Cost: ${result.cost:.4f}")
        if result.processing_time:
            print(f"⏱️  Processing: {result.processing_time:.1f}s")

        # Save JSON if requested
        if args.save_json:
            json_path = Path(args.output) / args.save_json
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "success": True,
                    "image_url": result.image_url,
                    "local_path": result.local_path,
                    "upscaled_size": result.upscaled_size,
                    "cost": result.cost,
                    "processing_time": result.processing_time,
                    "metadata": result.metadata,
                }, f, indent=2)
            print(f"📄 Metadata: {json_path}")
    else:
        print(f"\n❌ Upscale failed!")
        print(f"   Error: {result.error}")
        sys.exit(1)
```

---

### Subtask 2: Integrate CLI into Main Entry Point (5 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

**Add import:**
```python
from .grid_generator import (
    generate_grid_command,
    upscale_image_command,
    GRID_CONFIGS,
    UPSCALE_TARGETS,
)
```

**Add generate-grid subparser:**
```python
# Generate grid command
grid_parser = subparsers.add_parser(
    "generate-grid",
    help="Generate 2x2 or 3x3 image grid from prompt file"
)
grid_parser.add_argument(
    "--prompt-file", "-f",
    required=True,
    help="Markdown file with panel descriptions"
)
grid_parser.add_argument(
    "--grid", "-g",
    choices=list(GRID_CONFIGS.keys()),
    default="3x3",
    help="Grid size: 2x2 (4 panels) or 3x3 (9 panels). Default: 3x3"
)
grid_parser.add_argument(
    "--style", "-s",
    help="Style override (replaces prompt file style)"
)
grid_parser.add_argument(
    "--model", "-m",
    default="nano_banana_pro",
    help="Model to use (default: nano_banana_pro)"
)
grid_parser.add_argument(
    "--upscale",
    type=float,
    help="Upscale factor after generation (e.g., 2 for 2x)"
)
grid_parser.add_argument(
    "-o", "--output",
    default="output",
    help="Output directory (default: output)"
)
grid_parser.add_argument(
    "--save-json",
    metavar="FILENAME",
    help="Save metadata as JSON file"
)
```

**Add upscale-image subparser:**
```python
# Upscale image command
upscale_parser = subparsers.add_parser(
    "upscale-image",
    help="Upscale image using SeedVR2"
)
upscale_parser.add_argument(
    "-i", "--input",
    required=True,
    help="Input image path or URL"
)
upscale_parser.add_argument(
    "--factor",
    type=float,
    default=2,
    help="Upscale factor 1-8 (default: 2)"
)
upscale_parser.add_argument(
    "--target",
    choices=UPSCALE_TARGETS,
    help="Target resolution (720p, 1080p, 1440p, 2160p). Overrides --factor"
)
upscale_parser.add_argument(
    "--format",
    choices=["png", "jpg", "webp"],
    default="png",
    help="Output format (default: png)"
)
upscale_parser.add_argument(
    "-o", "--output",
    default="output",
    help="Output directory (default: output)"
)
upscale_parser.add_argument(
    "--save-json",
    metavar="FILENAME",
    help="Save metadata as JSON file"
)
```

**Add dispatch:**
```python
elif args.command == "generate-grid":
    generate_grid_command(args)
elif args.command == "upscale-image":
    upscale_image_command(args)
```

---

### Subtask 3: Update Skill Documentation (3 min)

**File:** `.claude/skills/ai-content-pipeline/Skill.md`

Add after Transcribe Audio section:

```markdown
### Generate Image Grid
Generate 2x2 or 3x3 image grids from structured prompt files.

```bash
# Generate 3x3 grid (default)
./venv/Scripts/aicp.exe generate-grid --prompt-file storyboard.md

# Generate 2x2 grid
./venv/Scripts/aicp.exe generate-grid -f storyboard.md --grid 2x2

# With style override
./venv/Scripts/aicp.exe generate-grid -f storyboard.md --style "anime, vibrant"

# Generate and upscale 2x
./venv/Scripts/aicp.exe generate-grid -f storyboard.md --upscale 2
```

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--prompt-file` | `-f` | required | Markdown file with panels |
| `--grid` | `-g` | 3x3 | Grid size (2x2 or 3x3) |
| `--style` | `-s` | | Style override |
| `--model` | `-m` | nano_banana_pro | Model to use |
| `--upscale` | | | Upscale factor (1-8) |
| `--output` | `-o` | output/ | Output directory |

**Pricing:** $0.002/grid + $0.01 if upscaled

### Upscale Image
Upscale images using SeedVR2 API.

```bash
# Upscale 2x (default)
./venv/Scripts/aicp.exe upscale-image -i image.png

# Upscale 4x
./venv/Scripts/aicp.exe upscale-image -i image.png --factor 4

# Upscale to 1080p
./venv/Scripts/aicp.exe upscale-image -i image.png --target 1080p

# Upscale to 4K
./venv/Scripts/aicp.exe upscale-image -i image.png --target 2160p
```

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input` | `-i` | required | Image path or URL |
| `--factor` | | 2 | Upscale factor (1-8) |
| `--target` | | | Target: 720p/1080p/1440p/2160p |
| `--format` | | png | Output format (png/jpg/webp) |
| `--output` | `-o` | output/ | Output directory |

**Pricing:** ~$0.01/image
```

---

## File Summary

| File | Action | Description |
|------|--------|-------------|
| `ai_content_pipeline/grid_generator.py` | **Create** | Grid + upscale CLI module |
| `ai_content_pipeline/__main__.py` | **Modify** | Add both commands |
| `.claude/skills/ai-content-pipeline/Skill.md` | **Modify** | Add documentation |
| `input/prompts/higgs-music-video-grid.md` | **Already created** | Example prompt file |

## API Reference

### SeedVR2 Upscale API
- **Endpoint:** `fal-ai/seedvr/upscale/image`
- **Required:** `image_url`
- **Modes:**
  - Factor mode: `upscale_factor` (1-8)
  - Target mode: `target_resolution` (720p, 1080p, 1440p, 2160p)
- **Options:** `noise_scale` (0-1), `output_format` (png/jpg/webp)

## Testing

```bash
# Test 3x3 grid
aicp generate-grid --prompt-file input/prompts/higgs-music-video-grid.md

# Test 2x2 grid
aicp generate-grid --prompt-file input/prompts/higgs-music-video-grid.md --grid 2x2

# Test upscale
aicp upscale-image -i output/grid.png --factor 2

# Test upscale to 4K
aicp upscale-image -i output/grid.png --target 2160p
```

## Cost Summary

| Operation | Cost |
|-----------|------|
| 2x2 grid (Nano Banana Pro) | $0.002 |
| 3x3 grid (Nano Banana Pro) | $0.002 |
| Image upscale | ~$0.01 |
| Grid + upscale | ~$0.012 |
