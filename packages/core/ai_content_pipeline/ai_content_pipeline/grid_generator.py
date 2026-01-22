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

    Args:
        file_path: Path to the markdown prompt file

    Returns:
        Dict with title, style, panels, and raw_content
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

    # Extract style from STYLE PROMPT SUFFIX code block first (preferred)
    style_code_match = re.search(
        r'##\s*STYLE\s*PROMPT\s*SUFFIX.*?```(?:\w+)?\s*\n(.*?)```',
        content, re.DOTALL | re.IGNORECASE
    )
    if style_code_match:
        result["style"] = style_code_match.group(1).strip()
    else:
        # Fall back to other style sections
        style_match = re.search(
            r'##\s*(?:Style|STYLE|Technical Specs|TECHNICAL SPECS).*?\n(.*?)(?=##|\Z)',
            content, re.DOTALL | re.IGNORECASE
        )
        if style_match:
            style_text = style_match.group(1).strip()
            # Clean up bullet points, code blocks, and formatting
            style_text = re.sub(r'```[\s\S]*?```', '', style_text)  # Remove code blocks
            style_lines = [line.strip().lstrip('*-•').strip()
                          for line in style_text.split('\n') if line.strip() and not line.strip().startswith('```')]
            result["style"] = ", ".join(filter(None, style_lines))

    # Extract panels - try table format first (look for PANELS section with table)
    panels_section = re.search(
        r'##\s*(?:PANELS|PANELS\s*&\s*LAYOUT).*?\n(.*?)(?=##|\Z)',
        content, re.DOTALL | re.IGNORECASE
    )
    if panels_section:
        section_content = panels_section.group(1)
        # Check if it contains a markdown table with Panel rows
        if '|' in section_content and 'Panel' in section_content:
            # Parse markdown table - match rows like | **Panel 1** | Description text |
            rows = re.findall(
                r'\|\s*\*?\*?Panel\s*\d+\*?\*?\s*\|\s*(.+?)\s*\|',
                section_content, re.MULTILINE
            )
            result["panels"] = [row.strip() for row in rows if row.strip()]

    # If no table panels, try list format
    if not result["panels"]:
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
    """
    Format parsed prompt data into a single grid generation prompt.

    Args:
        parsed: Parsed prompt file data
        grid_size: Grid size (2x2 or 3x3)
        style_override: Optional style to override parsed style

    Returns:
        Formatted prompt string for image generation
    """
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
    """
    Upload local file to FAL if needed, return URL.

    Args:
        file_path: Local file path or URL

    Returns:
        URL to the file (original if already URL, or FAL upload URL)
    """
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
        factor: Upscale factor (2-10), mutually exclusive with target
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

        # Handle ModelResult dataclass (has attributes, not dict access)
        if not result.success:
            return GridGenerationResult(
                success=False,
                error=result.error or "Generation failed",
            )

        image_url = result.output_url
        local_path = result.output_path
        total_cost = result.cost_estimate or MODEL_COSTS.get(model, 0.002)

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
