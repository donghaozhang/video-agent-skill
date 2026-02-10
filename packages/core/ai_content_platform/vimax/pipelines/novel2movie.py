"""
Novel to Movie Pipeline

Extended pipeline for converting novels or long-form content into videos:
1. Novel compression (extract key scenes)
2. Character extraction
3. Scene-by-scene video generation
4. Final assembly
"""

from typing import Optional, List, Dict
from pathlib import Path
import logging
import json
import re
from datetime import datetime

from pydantic import BaseModel, Field

from ..agents import (
    Screenwriter, ScreenwriterConfig, Script,
    CharacterExtractor, CharacterExtractorConfig,
    CharacterPortraitsGenerator, PortraitsGeneratorConfig,
    StoryboardArtist, StoryboardArtistConfig,
    CameraImageGenerator, CameraGeneratorConfig,
)
from ..agents.schemas import ChapterCompressionResponse
from ..adapters import LLMAdapter, LLMAdapterConfig, Message, VideoGeneratorAdapter, VideoAdapterConfig
from ..interfaces import (
    PipelineOutput,
    CharacterInNovel,
    CharacterPortrait,
    CharacterPortraitRegistry,
)


class Novel2MovieConfig(BaseModel):
    """Configuration for Novel2Movie pipeline."""

    output_dir: str = "media/generated/vimax/novel2movie"
    max_scenes: int = 10
    scene_duration: float = 30.0  # seconds per scene
    video_model: str = "kling"
    image_model: str = "nano_banana_pro"
    llm_model: str = "kimi-k2.5"

    # Character consistency settings
    generate_portraits: bool = True
    use_character_references: bool = True  # Use portraits for storyboard consistency
    max_characters: int = 5  # Limit portraits to main characters

    # Pipeline control
    scripts_only: bool = False  # Stop after script generation (LLM-only, no images)
    storyboard_only: bool = False  # Stop after storyboard generation (skip video)
    save_intermediate: bool = True  # Save characters, scripts, chapters to disk

    # Chunking settings
    chunk_size: int = 10000  # characters per chunk
    overlap: int = 500


class ChapterSummary(BaseModel):
    """Summary of a novel chapter."""

    chapter_id: str
    title: str
    summary: str = ""
    key_events: List[str] = Field(default_factory=list)
    characters: List[str] = Field(default_factory=list)
    setting: str = ""


class Novel2MovieResult(BaseModel):
    """Result from Novel2Movie pipeline."""

    success: bool
    novel_title: str = ""
    chapters: List[ChapterSummary] = Field(default_factory=list)
    scripts: List[Script] = Field(default_factory=list)
    characters: List[CharacterInNovel] = Field(default_factory=list)
    portraits: Dict[str, CharacterPortrait] = Field(default_factory=dict)
    portrait_registry: Optional[CharacterPortraitRegistry] = None
    output: Optional[PipelineOutput] = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_cost: float = 0.0
    errors: List[str] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}


COMPRESSION_PROMPT = """You are an expert at adapting novels for film.

Analyze this section of text and extract the key visual scenes that would work for a short film adaptation.

TEXT:
{text}

For each key scene, provide:
1. A brief title
2. A visual description (what we would SEE on screen)
3. The main characters involved
4. The setting/location

Focus on scenes with strong visual potential. Limit to {max_scenes} scenes.

Return as JSON:
{{
    "title": "Section title or chapter name",
    "scenes": [
        {{
            "title": "Scene title",
            "description": "Visual description",
            "characters": ["character names"],
            "setting": "Location description"
        }}
    ]
}}"""


class Novel2MoviePipeline:
    """
    Pipeline that converts novels into movies.

    Usage:
        pipeline = Novel2MoviePipeline(config)
        result = await pipeline.run(novel_text)
    """

    def __init__(self, config: Optional[Novel2MovieConfig] = None):
        self.config = config or Novel2MovieConfig()
        self.logger = logging.getLogger("vimax.pipelines.novel2movie")
        self._init_components()

    def _init_components(self, output_dir: Optional[Path] = None):
        """Initialize all components.

        Args:
            output_dir: Per-run output directory. When provided, portraits
                and storyboard images are saved under this directory instead
                of shared root-level folders.
        """
        self._llm = LLMAdapter(LLMAdapterConfig(model=self.config.llm_model))

        self.screenwriter = Screenwriter(ScreenwriterConfig(
            model=self.config.llm_model,
            target_duration=self.config.scene_duration,
        ))

        self.character_extractor = CharacterExtractor(CharacterExtractorConfig(
            model=self.config.llm_model,
        ))

        # Route portraits and storyboard under per-run directory
        base = str(output_dir) if output_dir else self.config.output_dir

        self.portraits_generator = CharacterPortraitsGenerator(PortraitsGeneratorConfig(
            image_model=self.config.image_model,
            llm_model=self.config.llm_model,
            output_dir=f"{base}/portraits",
        ))

        self.storyboard_artist = StoryboardArtist(StoryboardArtistConfig(
            image_model=self.config.image_model,
            output_dir=f"{base}/storyboard",
        ))

        self.camera_generator = CameraImageGenerator(CameraGeneratorConfig(
            video_model=self.config.video_model,
            output_dir=f"{base}/videos",
        ))

    def _safe_slug(self, value: str) -> str:
        """Sanitize a string for use in filesystem paths."""
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
        return safe or "untitled"

    async def run(self, novel_text: str, title: str = "Untitled Novel") -> Novel2MovieResult:
        """
        Convert novel text to movie.

        Args:
            novel_text: Full novel text
            title: Novel title

        Returns:
            Novel2MovieResult
        """
        result = Novel2MovieResult(novel_title=title, success=False)

        self.logger.info(f"Starting Novel2Movie pipeline for: {title}")

        try:
            safe_title = self._safe_slug(title)
            output_dir = Path(self.config.output_dir) / safe_title
            output_dir.mkdir(parents=True, exist_ok=True)

            # Re-init components so portraits/storyboard are under per-title dir
            self._init_components(output_dir)

            # Initialize LLM
            await self._llm.initialize()

            # Step 1: Extract characters from full novel
            self.logger.info("Step 1: Extracting characters...")
            char_result = await self.character_extractor.process(novel_text[:50000])
            if char_result.success:
                result.characters = char_result.result
                result.total_cost += char_result.metadata.get("cost", 0)
                if self.config.save_intermediate:
                    self._save_characters(result.characters, output_dir / "characters.json")

            # Step 1b: Generate character portraits for consistency
            if self.config.generate_portraits and not self.config.scripts_only and result.characters:
                self.logger.info("Step 1b: Generating character portraits...")
                portraits_result = await self.portraits_generator.generate_batch(
                    result.characters[:self.config.max_characters]
                )
                result.portraits = portraits_result.result or {}
                result.total_cost += portraits_result.metadata.get("cost", 0)

                # Create portrait registry for storyboard reference
                if result.portraits and self.config.use_character_references:
                    result.portrait_registry = CharacterPortraitRegistry(
                        project_id=safe_title
                    )
                    for name, portrait in result.portraits.items():
                        result.portrait_registry.add_portrait(portrait)
                    self.logger.info(
                        f"Created portrait registry with {len(result.portraits)} characters"
                    )
                    if self.config.save_intermediate:
                        self._save_registry(result.portrait_registry, output_dir / "portrait_registry.json")
            elif self.config.scripts_only:
                self.logger.info("Step 1b: Skipped (scripts_only mode)")

            # Step 2: Compress novel into key scenes
            self.logger.info("Step 2: Compressing novel into scenes...")
            chapters = await self._compress_novel(novel_text)
            result.chapters = chapters
            if self.config.save_intermediate:
                self._save_chapters(chapters, output_dir / "chapters.json")

            # Step 3: Generate scripts for each chapter
            self.logger.info("Step 3: Generating scripts...")
            all_videos = []
            scripts_dir = output_dir / "scripts"
            if self.config.save_intermediate:
                scripts_dir.mkdir(parents=True, exist_ok=True)

            for i, chapter in enumerate(chapters[:self.config.max_scenes]):
                self.logger.info(f"Processing chapter {i+1}/{len(chapters)}: {chapter.title}")

                # Generate script from chapter summary
                script_idea = self._chapter_to_idea(chapter)
                script_result = await self.screenwriter.process(script_idea)

                if not script_result.success:
                    self.logger.warning(f"Script generation failed for chapter {i+1}")
                    continue

                result.scripts.append(script_result.result)
                result.total_cost += script_result.metadata.get("cost", 0)
                if self.config.save_intermediate:
                    self._save_script(script_result.result, scripts_dir / f"chapter_{i+1:03d}.json")

                # Skip image/video generation in scripts_only mode
                if self.config.scripts_only:
                    continue

                # Generate storyboard with character references
                storyboard_result = await self.storyboard_artist.process(
                    script_result.result,
                    portrait_registry=result.portrait_registry,
                    chapter_index=i + 1,
                )
                if not storyboard_result.success:
                    continue
                result.total_cost += storyboard_result.metadata.get("cost", 0)

                # Re-save script now that resolve_references has enriched shots
                if self.config.save_intermediate:
                    self._save_script(script_result.result, scripts_dir / f"chapter_{i+1:03d}.json")

                if self.config.storyboard_only:
                    continue

                # Generate videos
                video_result = await self.camera_generator.process(storyboard_result.result)
                if video_result.success and video_result.result.videos:
                    all_videos.extend(video_result.result.videos)
                    result.total_cost += video_result.metadata.get("cost", 0)

            # Step 4: Concatenate all chapter videos
            if all_videos and not self.config.storyboard_only and not self.config.scripts_only:
                self.logger.info("Step 4: Assembling final video...")
                final_path = str(output_dir / "final_movie.mp4")

                video_adapter = VideoGeneratorAdapter(VideoAdapterConfig())
                await video_adapter.initialize()

                final_video = await video_adapter.concatenate_videos(all_videos, final_path)

                result.output = PipelineOutput(
                    pipeline_name=f"novel2movie_{safe_title}",
                    videos=all_videos,
                    final_video=final_video,
                    output_directory=str(output_dir),
                )

            result.success = len(result.scripts) > 0
            result.completed_at = datetime.now()

            if self.config.save_intermediate:
                self._save_summary(result, output_dir / "summary.json")

            self.logger.info(
                f"Pipeline completed! "
                f"Chapters: {len(result.chapters)}, "
                f"Scripts: {len(result.scripts)}, "
                f"Cost: ${result.total_cost:.3f}"
            )

        except Exception as e:
            self.logger.exception("Pipeline failed")
            result.errors.append(str(e))

        return result

    async def _compress_novel(self, text: str) -> List[ChapterSummary]:
        """Compress novel into key scenes."""
        chapters = []

        # Split into chunks
        chunks = self._split_text(text)

        for i, chunk in enumerate(chunks):
            prompt = COMPRESSION_PROMPT.format(
                text=chunk,
                max_scenes=3,
            )

            try:
                # Use native structured output — API guarantees valid JSON
                result = await self._llm.chat_with_structured_output(
                    [Message(role="user", content=prompt)],
                    output_schema=ChapterCompressionResponse,
                    schema_name="chapter_compression",
                )
                chapter = ChapterSummary(
                    chapter_id=f"chapter_{i+1}",
                    title=result.title,
                    summary="",
                    key_events=[s.description for s in result.scenes],
                    characters=[c for s in result.scenes for c in s.characters],
                )
                chapters.append(chapter)
            except ValueError as e:
                self.logger.warning(f"Failed to parse chapter {i+1}: {e}")

        return chapters

    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if self.config.overlap >= self.config.chunk_size:
            raise ValueError(
                f"overlap ({self.config.overlap}) must be less than chunk_size ({self.config.chunk_size})"
            )

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.config.chunk_size
            chunk = text[start:end]

            # Try to end at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > self.config.chunk_size * 0.8:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1

            chunks.append(chunk)
            start = end - self.config.overlap

        return chunks

    def _chapter_to_idea(self, chapter: ChapterSummary) -> str:
        """Convert chapter summary to screenplay idea."""
        parts = [f"Scene: {chapter.title}"]

        if chapter.key_events:
            parts.append("Key moments:")
            for event in chapter.key_events[:3]:
                parts.append(f"- {event}")

        if chapter.characters:
            unique_chars = list(dict.fromkeys(chapter.characters))
            parts.append(f"Characters: {', '.join(unique_chars[:5])}")

        return "\n".join(parts)

    def _save_characters(self, characters: List[CharacterInNovel], path: Path):
        """Save extracted characters to JSON file."""
        data = [c.model_dump() for c in characters]
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        self.logger.info(f"Saved {len(characters)} characters to {path}")

    def _save_chapters(self, chapters: List[ChapterSummary], path: Path):
        """Save chapter summaries to JSON file."""
        data = [c.model_dump() for c in chapters]
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        self.logger.info(f"Saved {len(chapters)} chapters to {path}")

    def _save_script(self, script: Script, path: Path):
        """Save script to JSON file."""
        with open(path, "w") as f:
            json.dump(script.model_dump(), f, indent=2, default=str)
        self.logger.info(f"Saved script to {path}")

    def _save_registry(self, registry: CharacterPortraitRegistry, path: Path):
        """Save portrait registry to JSON file."""
        data = registry.model_dump()
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        self.logger.info(f"Saved portrait registry to {path}")

    def _save_summary(self, result: Novel2MovieResult, path: Path):
        """Save pipeline summary to JSON file."""
        summary = {
            "success": result.success,
            "novel_title": result.novel_title,
            "chapter_count": len(result.chapters),
            "script_count": len(result.scripts),
            "character_count": len(result.characters),
            "portrait_count": len(result.portraits),
            "used_character_references": result.portrait_registry is not None,
            "storyboard_only": self.config.storyboard_only,
            "video_count": len(result.output.videos) if result.output else 0,
            "final_video": result.output.final_video.video_path if result.output and result.output.final_video else None,
            "total_cost": result.total_cost,
            "started_at": str(result.started_at),
            "completed_at": str(result.completed_at),
            "errors": result.errors,
        }
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)
        self.logger.info(f"Saved summary to {path}")
