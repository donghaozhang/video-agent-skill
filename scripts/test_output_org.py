"""
Quick E2E test: verify output folder organization and meaningful file names.

Runs novel2movie with minimal settings:
- 1 scene max (1 storyboard chapter)
- 2 characters max
- 2 portrait views (front + three_quarter) = 4 images
- storyboard_only (skip video gen)
- Total expected images: ~4 portraits + ~3 storyboard = ~7 images (~$0.02)
"""

import asyncio
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stdout,
)

# Reduce noise from HTTP libs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


async def main():
    from packages.core.ai_content_platform.vimax.pipelines.novel2movie import (
        Novel2MoviePipeline,
        Novel2MovieConfig,
    )
    from packages.core.ai_content_platform.vimax.agents.character_portraits import (
        PortraitsGeneratorConfig,
    )

    # Read test novel
    novel_path = Path("input/text/test_novel.txt")
    novel_text = novel_path.read_text(encoding="utf-8")
    print(f"\nNovel length: {len(novel_text):,} chars")

    # Minimal config: 1 scene, 2 chars, storyboard_only
    config = Novel2MovieConfig(
        output_dir="media/generated/vimax/novel2movie",
        max_scenes=1,
        max_characters=2,
        storyboard_only=True,
        save_intermediate=True,
        image_model="nano_banana_pro",
        llm_model="kimi-k2.5",
    )

    pipeline = Novel2MoviePipeline(config)

    # Override portrait views to just 2 (instead of 4) to save cost
    pipeline.portraits_generator.config.views = ["front", "three_quarter"]

    title = "Output Org Test"
    print(f"\nRunning pipeline: {title}")
    print(f"  max_scenes={config.max_scenes}")
    print(f"  max_characters={config.max_characters}")
    print(f"  storyboard_only={config.storyboard_only}")
    print(f"  portrait views: {pipeline.portraits_generator.config.views}")
    print()

    result = await pipeline.run(novel_text, title=title)

    # Report results
    print("\n" + "=" * 60)
    print(f"SUCCESS: {result.success}")
    print(f"Characters: {len(result.characters)}")
    print(f"Portraits: {len(result.portraits)}")
    print(f"Chapters: {len(result.chapters)}")
    print(f"Scripts: {len(result.scripts)}")
    print(f"Cost: ${result.total_cost:.3f}")
    print(f"Errors: {result.errors}")

    # Show output folder structure
    output_dir = Path(config.output_dir) / pipeline._safe_slug(title)
    print(f"\nOutput directory: {output_dir}")
    if output_dir.exists():
        print("\nFile tree:")
        for p in sorted(output_dir.rglob("*")):
            rel = p.relative_to(output_dir)
            indent = "  " * len(rel.parts)
            if p.is_dir():
                print(f"  {indent}{rel.name}/")
            else:
                size = p.stat().st_size
                print(f"  {indent}{rel.name}  ({size:,} bytes)")

    # Verify naming
    print("\n" + "=" * 60)
    print("VERIFICATION:")

    # Check portraits have character name folders
    portraits_dir = output_dir / "portraits"
    if portraits_dir.exists():
        portrait_files = list(portraits_dir.rglob("*.png"))
        print(f"\nPortrait files ({len(portrait_files)}):")
        for f in sorted(portrait_files):
            print(f"  {f.relative_to(output_dir)}")

        # Verify no timestamp-based names
        has_timestamp_names = any("nano_banana" in f.name or f.name.startswith("mock_") for f in portrait_files)
        print(f"  Has timestamp names (BAD): {has_timestamp_names}")
        has_meaningful_names = all(f.stem in ["front", "side", "back", "three_quarter"] for f in portrait_files)
        print(f"  Has meaningful names (GOOD): {has_meaningful_names}")
    else:
        print("\n  No portraits directory found!")

    # Check storyboard has chapter folders
    storyboard_dir = output_dir / "storyboard"
    if storyboard_dir.exists():
        storyboard_files = list(storyboard_dir.rglob("*.png"))
        print(f"\nStoryboard files ({len(storyboard_files)}):")
        for f in sorted(storyboard_files):
            print(f"  {f.relative_to(output_dir)}")

        has_scene_prefix = all("scene_" in f.name for f in storyboard_files)
        print(f"  Has scene prefix (GOOD): {has_scene_prefix}")
        has_chapter_folder = any("chapter_" in p.name for p in storyboard_dir.iterdir() if p.is_dir())
        print(f"  Has chapter folder (GOOD): {has_chapter_folder}")
    else:
        print("\n  No storyboard directory found!")


if __name__ == "__main__":
    asyncio.run(main())
