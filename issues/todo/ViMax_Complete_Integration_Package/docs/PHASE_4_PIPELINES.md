# Phase 4: Pipeline Integration

**Duration**: 2-3 days
**Dependencies**: Phase 3 completed (Agents)
**Outcome**: Complete pipelines orchestrating multiple agents

---

## Overview

Pipelines orchestrate multiple agents to achieve end-to-end content generation workflows.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Idea2VideoPipeline                          │
├───────────┬───────────┬───────────┬───────────┬─────────────────┤
│   Idea    │  Script   │Character  │Storyboard │    Video        │
│           │           │Extraction │ Generation│  Generation     │
└───────────┴───────────┴───────────┴───────────┴─────────────────┘
     ↓           ↓           ↓           ↓            ↓
 User Input → Screenwriter→ Extractor → Artist → CameraGenerator
```

---

## Subtask 4.1: Idea2VideoPipeline

**Estimated Time**: 4-5 hours

### Description
Complete pipeline from text idea to final video.

### Target File
```
packages/core/ai_content_platform/vimax/pipelines/idea2video.py
```

### Implementation

```python
"""
Idea to Video Pipeline

Complete workflow from a text idea to a final video:
1. Screenwriter: Idea → Script
2. CharacterExtractor: Script → Characters
3. CharacterPortraitsGenerator: Characters → Portraits
4. StoryboardArtist: Script → Storyboard images
5. CameraImageGenerator: Storyboard → Videos
6. Concatenation: Videos → Final video
"""

from typing import Optional, Dict, Any
from pathlib import Path
import logging
import yaml
from datetime import datetime

from pydantic import BaseModel, Field

from ..agents import (
    Screenwriter, ScreenwriterConfig, Script,
    CharacterExtractor, CharacterExtractorConfig,
    CharacterPortraitsGenerator, PortraitsGeneratorConfig,
    StoryboardArtist, StoryboardArtistConfig, StoryboardResult,
    CameraImageGenerator, CameraGeneratorConfig,
)
from ..interfaces import PipelineOutput, CharacterPortrait


class Idea2VideoConfig(BaseModel):
    """Configuration for Idea2Video pipeline."""

    # Output settings
    output_dir: str = "output/vimax/idea2video"
    save_intermediate: bool = True

    # Target settings
    target_duration: float = 60.0  # seconds
    video_model: str = "kling"
    image_model: str = "flux_dev"
    llm_model: str = "claude-3.5-sonnet"

    # Agent configs (optional overrides)
    screenwriter: Optional[ScreenwriterConfig] = None
    character_extractor: Optional[CharacterExtractorConfig] = None
    portraits_generator: Optional[PortraitsGeneratorConfig] = None
    storyboard_artist: Optional[StoryboardArtistConfig] = None
    camera_generator: Optional[CameraGeneratorConfig] = None

    # Feature flags
    generate_portraits: bool = True
    parallel_generation: bool = False

    @classmethod
    def from_yaml(cls, path: str) -> "Idea2VideoConfig":
        """Load config from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


class Idea2VideoResult(BaseModel):
    """Result from Idea2Video pipeline."""

    success: bool
    idea: str
    script: Optional[Script] = None
    characters: list = Field(default_factory=list)
    portraits: Dict[str, CharacterPortrait] = Field(default_factory=dict)
    storyboard: Optional[StoryboardResult] = None
    output: Optional[PipelineOutput] = None

    # Timing and cost
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_cost: float = 0.0
    errors: list = Field(default_factory=list)

    @property
    def duration(self) -> Optional[float]:
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class Idea2VideoPipeline:
    """
    Pipeline that converts an idea into a video.

    Usage:
        pipeline = Idea2VideoPipeline(config)
        result = await pipeline.run("A samurai's journey at sunrise")
        if result.success:
            print(f"Video: {result.output.final_video.video_path}")
    """

    def __init__(self, config: Optional[Idea2VideoConfig] = None):
        self.config = config or Idea2VideoConfig()
        self.logger = logging.getLogger("vimax.pipelines.idea2video")

        # Initialize agents with config
        self._init_agents()

    def _init_agents(self):
        """Initialize all agents with configuration."""
        # Screenwriter
        screenwriter_config = self.config.screenwriter or ScreenwriterConfig(
            model=self.config.llm_model,
            target_duration=self.config.target_duration,
        )
        self.screenwriter = Screenwriter(screenwriter_config)

        # Character Extractor
        extractor_config = self.config.character_extractor or CharacterExtractorConfig(
            model=self.config.llm_model,
        )
        self.character_extractor = CharacterExtractor(extractor_config)

        # Portraits Generator
        portraits_config = self.config.portraits_generator or PortraitsGeneratorConfig(
            image_model=self.config.image_model,
            llm_model=self.config.llm_model,
            output_dir=f"{self.config.output_dir}/portraits",
        )
        self.portraits_generator = CharacterPortraitsGenerator(portraits_config)

        # Storyboard Artist
        storyboard_config = self.config.storyboard_artist or StoryboardArtistConfig(
            image_model=self.config.image_model,
            output_dir=f"{self.config.output_dir}/storyboard",
        )
        self.storyboard_artist = StoryboardArtist(storyboard_config)

        # Camera Generator
        camera_config = self.config.camera_generator or CameraGeneratorConfig(
            video_model=self.config.video_model,
            output_dir=f"{self.config.output_dir}/videos",
        )
        self.camera_generator = CameraImageGenerator(camera_config)

    async def run(self, idea: str) -> Idea2VideoResult:
        """
        Run the complete pipeline.

        Args:
            idea: Text idea or concept for the video

        Returns:
            Idea2VideoResult with all generated content
        """
        result = Idea2VideoResult(idea=idea, success=False)

        self.logger.info(f"Starting Idea2Video pipeline for: {idea[:100]}...")

        try:
            # Create output directory
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Step 1: Generate Script
            self.logger.info("Step 1/5: Generating script...")
            script_result = await self.screenwriter.process(idea)
            if not script_result.success:
                result.errors.append(f"Script generation failed: {script_result.error}")
                return result
            result.script = script_result.result
            result.total_cost += script_result.metadata.get("cost", 0)

            if self.config.save_intermediate:
                self._save_script(result.script, output_dir / "script.json")

            # Step 2: Extract Characters
            self.logger.info("Step 2/5: Extracting characters...")
            # Use script content for character extraction
            script_text = self._script_to_text(result.script)
            char_result = await self.character_extractor.process(script_text)
            if char_result.success:
                result.characters = char_result.result
                result.total_cost += char_result.metadata.get("cost", 0)
            else:
                self.logger.warning(f"Character extraction failed: {char_result.error}")

            # Step 3: Generate Character Portraits (optional)
            if self.config.generate_portraits and result.characters:
                self.logger.info("Step 3/5: Generating character portraits...")
                result.portraits = await self.portraits_generator.generate_batch(
                    result.characters[:5]  # Limit to main characters
                )
                for portrait in result.portraits.values():
                    result.total_cost += len(portrait.views) * 0.003  # Approximate

            # Step 4: Generate Storyboard
            self.logger.info("Step 4/5: Generating storyboard...")
            storyboard_result = await self.storyboard_artist.process(result.script)
            if not storyboard_result.success:
                result.errors.append(f"Storyboard generation failed: {storyboard_result.error}")
                return result
            result.storyboard = storyboard_result.result
            result.total_cost += storyboard_result.metadata.get("cost", 0)

            # Step 5: Generate Videos
            self.logger.info("Step 5/5: Generating videos...")
            video_result = await self.camera_generator.process(result.storyboard)
            if not video_result.success:
                result.errors.append(f"Video generation failed: {video_result.error}")
                return result
            result.output = video_result.result
            result.total_cost += video_result.metadata.get("cost", 0)

            # Mark success
            result.success = True
            result.completed_at = datetime.now()

            self.logger.info(
                f"Pipeline completed successfully! "
                f"Duration: {result.duration:.1f}s, "
                f"Cost: ${result.total_cost:.3f}"
            )

            # Save summary
            if self.config.save_intermediate:
                self._save_summary(result, output_dir / "summary.json")

        except Exception as e:
            self.logger.error(f"Pipeline failed with error: {e}")
            result.errors.append(str(e))

        return result

    def _script_to_text(self, script: Script) -> str:
        """Convert script to text for character extraction."""
        parts = [f"Title: {script.title}", f"Logline: {script.logline}", ""]

        for scene in script.scenes:
            parts.append(f"Scene: {scene.title}")
            parts.append(f"Location: {scene.location}")
            for shot in scene.shots:
                parts.append(f"- {shot.description}")
            parts.append("")

        return "\n".join(parts)

    def _save_script(self, script: Script, path: Path):
        """Save script to JSON file."""
        import json
        with open(path, "w") as f:
            json.dump(script.model_dump(), f, indent=2, default=str)

    def _save_summary(self, result: Idea2VideoResult, path: Path):
        """Save pipeline summary to JSON file."""
        import json
        summary = {
            "success": result.success,
            "idea": result.idea,
            "script_title": result.script.title if result.script else None,
            "scene_count": result.script.scene_count if result.script else 0,
            "character_count": len(result.characters),
            "portrait_count": len(result.portraits),
            "video_count": len(result.output.videos) if result.output else 0,
            "final_video": result.output.final_video.video_path if result.output and result.output.final_video else None,
            "total_cost": result.total_cost,
            "duration_seconds": result.duration,
            "errors": result.errors,
        }
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)


# Factory function
def create_pipeline(config_path: Optional[str] = None) -> Idea2VideoPipeline:
    """Create pipeline from config file or defaults."""
    if config_path:
        config = Idea2VideoConfig.from_yaml(config_path)
    else:
        config = Idea2VideoConfig()
    return Idea2VideoPipeline(config)
```

---

## Subtask 4.2: Script2VideoPipeline

**Estimated Time**: 3-4 hours

### Description
Pipeline that takes an existing script and generates video.

### Target File
```
packages/core/ai_content_platform/vimax/pipelines/script2video.py
```

### Implementation

```python
"""
Script to Video Pipeline

Converts an existing script into a video:
1. Parse script
2. Generate storyboard
3. Generate videos
4. Concatenate to final video
"""

from typing import Optional, Union
from pathlib import Path
import logging
from datetime import datetime

from pydantic import BaseModel, Field

from ..agents import (
    Script,
    StoryboardArtist, StoryboardArtistConfig,
    CameraImageGenerator, CameraGeneratorConfig,
)
from ..interfaces import PipelineOutput


class Script2VideoConfig(BaseModel):
    """Configuration for Script2Video pipeline."""

    output_dir: str = "output/vimax/script2video"
    video_model: str = "kling"
    image_model: str = "flux_dev"

    storyboard_artist: Optional[StoryboardArtistConfig] = None
    camera_generator: Optional[CameraGeneratorConfig] = None


class Script2VideoResult(BaseModel):
    """Result from Script2Video pipeline."""

    success: bool
    script: Script
    output: Optional[PipelineOutput] = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_cost: float = 0.0
    errors: list = Field(default_factory=list)


class Script2VideoPipeline:
    """
    Pipeline that converts a script into a video.

    Usage:
        pipeline = Script2VideoPipeline(config)
        result = await pipeline.run(script)
        if result.success:
            print(f"Video: {result.output.final_video.video_path}")
    """

    def __init__(self, config: Optional[Script2VideoConfig] = None):
        self.config = config or Script2VideoConfig()
        self.logger = logging.getLogger("vimax.pipelines.script2video")
        self._init_agents()

    def _init_agents(self):
        """Initialize agents."""
        storyboard_config = self.config.storyboard_artist or StoryboardArtistConfig(
            image_model=self.config.image_model,
            output_dir=f"{self.config.output_dir}/storyboard",
        )
        self.storyboard_artist = StoryboardArtist(storyboard_config)

        camera_config = self.config.camera_generator or CameraGeneratorConfig(
            video_model=self.config.video_model,
            output_dir=f"{self.config.output_dir}/videos",
        )
        self.camera_generator = CameraImageGenerator(camera_config)

    async def run(self, script: Union[Script, dict, str]) -> Script2VideoResult:
        """
        Run the pipeline.

        Args:
            script: Script object, dict, or path to JSON file

        Returns:
            Script2VideoResult
        """
        # Parse script input
        if isinstance(script, str):
            script = self._load_script(script)
        elif isinstance(script, dict):
            script = Script(**script)

        result = Script2VideoResult(script=script, success=False)

        self.logger.info(f"Starting Script2Video pipeline for: {script.title}")

        try:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Step 1: Generate Storyboard
            self.logger.info("Step 1/2: Generating storyboard...")
            storyboard_result = await self.storyboard_artist.process(script)
            if not storyboard_result.success:
                result.errors.append(f"Storyboard failed: {storyboard_result.error}")
                return result
            result.total_cost += storyboard_result.metadata.get("cost", 0)

            # Step 2: Generate Videos
            self.logger.info("Step 2/2: Generating videos...")
            video_result = await self.camera_generator.process(storyboard_result.result)
            if not video_result.success:
                result.errors.append(f"Video generation failed: {video_result.error}")
                return result

            result.output = video_result.result
            result.total_cost += video_result.metadata.get("cost", 0)
            result.success = True
            result.completed_at = datetime.now()

            self.logger.info(f"Pipeline completed! Cost: ${result.total_cost:.3f}")

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            result.errors.append(str(e))

        return result

    def _load_script(self, path: str) -> Script:
        """Load script from JSON file."""
        import json
        with open(path) as f:
            data = json.load(f)
        return Script(**data)
```

---

## Subtask 4.3: Novel2MoviePipeline

**Estimated Time**: 4-5 hours

### Description
Extended pipeline for converting novels/long-form content to video.

### Target File
```
packages/core/ai_content_platform/vimax/pipelines/novel2movie.py
```

### Implementation

```python
"""
Novel to Movie Pipeline

Extended pipeline for converting novels or long-form content into videos:
1. Novel compression (extract key scenes)
2. Character extraction
3. Scene-by-scene video generation
4. Final assembly
"""

from typing import Optional, List
from pathlib import Path
import logging
from datetime import datetime

from pydantic import BaseModel, Field

from ..agents import (
    Screenwriter, ScreenwriterConfig, Script,
    CharacterExtractor, CharacterExtractorConfig,
    CharacterPortraitsGenerator, PortraitsGeneratorConfig,
    StoryboardArtist, StoryboardArtistConfig,
    CameraImageGenerator, CameraGeneratorConfig,
    AgentResult,
)
from ..adapters import LLMAdapter, LLMAdapterConfig, Message
from ..interfaces import PipelineOutput, CharacterInNovel


class Novel2MovieConfig(BaseModel):
    """Configuration for Novel2Movie pipeline."""

    output_dir: str = "output/vimax/novel2movie"
    max_scenes: int = 10
    scene_duration: float = 30.0  # seconds per scene
    video_model: str = "kling"
    image_model: str = "flux_dev"
    llm_model: str = "claude-3.5-sonnet"

    # Chunking settings
    chunk_size: int = 10000  # characters per chunk
    overlap: int = 500


class ChapterSummary(BaseModel):
    """Summary of a novel chapter."""

    chapter_id: str
    title: str
    summary: str
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
    output: Optional[PipelineOutput] = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_cost: float = 0.0
    errors: List[str] = Field(default_factory=list)


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

    def _init_components(self):
        """Initialize all components."""
        self._llm = LLMAdapter(LLMAdapterConfig(model=self.config.llm_model))

        self.screenwriter = Screenwriter(ScreenwriterConfig(
            model=self.config.llm_model,
            target_duration=self.config.scene_duration,
        ))

        self.character_extractor = CharacterExtractor(CharacterExtractorConfig(
            model=self.config.llm_model,
        ))

        self.storyboard_artist = StoryboardArtist(StoryboardArtistConfig(
            image_model=self.config.image_model,
            output_dir=f"{self.config.output_dir}/storyboard",
        ))

        self.camera_generator = CameraImageGenerator(CameraGeneratorConfig(
            video_model=self.config.video_model,
            output_dir=f"{self.config.output_dir}/videos",
        ))

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
            output_dir = Path(self.config.output_dir) / title.replace(" ", "_")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Initialize LLM
            await self._llm.initialize()

            # Step 1: Extract characters from full novel
            self.logger.info("Step 1: Extracting characters...")
            char_result = await self.character_extractor.process(novel_text[:50000])
            if char_result.success:
                result.characters = char_result.result
                result.total_cost += char_result.metadata.get("cost", 0)

            # Step 2: Compress novel into key scenes
            self.logger.info("Step 2: Compressing novel into scenes...")
            chapters = await self._compress_novel(novel_text)
            result.chapters = chapters

            # Step 3: Generate scripts for each chapter
            self.logger.info("Step 3: Generating scripts...")
            all_videos = []

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

                # Generate storyboard
                storyboard_result = await self.storyboard_artist.process(script_result.result)
                if not storyboard_result.success:
                    continue
                result.total_cost += storyboard_result.metadata.get("cost", 0)

                # Generate videos
                video_result = await self.camera_generator.process(storyboard_result.result)
                if video_result.success and video_result.result.videos:
                    all_videos.extend(video_result.result.videos)
                    result.total_cost += video_result.metadata.get("cost", 0)

            # Step 4: Concatenate all chapter videos
            if all_videos:
                self.logger.info("Step 4: Assembling final video...")
                final_path = str(output_dir / "final_movie.mp4")

                from ..adapters import VideoGeneratorAdapter, VideoAdapterConfig
                video_adapter = VideoGeneratorAdapter(VideoAdapterConfig())
                await video_adapter.initialize()

                final_video = await video_adapter.concatenate_videos(all_videos, final_path)

                result.output = PipelineOutput(
                    pipeline_name=f"novel2movie_{title}",
                    videos=all_videos,
                    final_video=final_video,
                    total_cost=result.total_cost,
                    output_directory=str(output_dir),
                )

            result.success = len(result.scripts) > 0
            result.completed_at = datetime.now()

            self.logger.info(
                f"Pipeline completed! "
                f"Chapters: {len(result.chapters)}, "
                f"Scripts: {len(result.scripts)}, "
                f"Cost: ${result.total_cost:.3f}"
            )

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
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

            response = await self._llm.chat([Message(role="user", content=prompt)])

            try:
                import json
                import re
                match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    chapter = ChapterSummary(
                        chapter_id=f"chapter_{i+1}",
                        title=data.get("title", f"Chapter {i+1}"),
                        summary="",
                        key_events=[s.get("description", "") for s in data.get("scenes", [])],
                        characters=[c for s in data.get("scenes", []) for c in s.get("characters", [])],
                    )
                    chapters.append(chapter)
            except Exception as e:
                self.logger.warning(f"Failed to parse chapter {i+1}: {e}")

        return chapters

    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
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
            parts.append(f"Characters: {', '.join(set(chapter.characters)[:5])}")

        return "\n".join(parts)
```

---

## Subtask 4.4: Update Pipeline Exports

**Estimated Time**: 30 minutes

### File: `packages/core/ai_content_platform/vimax/pipelines/__init__.py`

```python
"""
ViMax Pipelines

End-to-end content generation workflows.
"""

from .idea2video import (
    Idea2VideoPipeline,
    Idea2VideoConfig,
    Idea2VideoResult,
    create_pipeline,
)
from .script2video import (
    Script2VideoPipeline,
    Script2VideoConfig,
    Script2VideoResult,
)
from .novel2movie import (
    Novel2MoviePipeline,
    Novel2MovieConfig,
    Novel2MovieResult,
)

__all__ = [
    # Idea2Video
    "Idea2VideoPipeline",
    "Idea2VideoConfig",
    "Idea2VideoResult",
    "create_pipeline",
    # Script2Video
    "Script2VideoPipeline",
    "Script2VideoConfig",
    "Script2VideoResult",
    # Novel2Movie
    "Novel2MoviePipeline",
    "Novel2MovieConfig",
    "Novel2MovieResult",
]
```

---

## Subtask 4.5: Pipeline Unit Tests

**Estimated Time**: 2-3 hours

### File: `tests/unit/vimax/test_pipelines.py`

```python
"""
Tests for ViMax pipelines.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from ai_content_platform.vimax.pipelines import (
    Idea2VideoPipeline,
    Idea2VideoConfig,
    Script2VideoPipeline,
    Script2VideoConfig,
)
from ai_content_platform.vimax.agents import Script, AgentResult
from ai_content_platform.vimax.agents.storyboard_artist import StoryboardResult
from ai_content_platform.vimax.interfaces import (
    Scene, ShotDescription, ImageOutput, VideoOutput, PipelineOutput,
)


@pytest.fixture
def mock_script():
    """Create a mock script."""
    return Script(
        title="Test Script",
        logline="A test story",
        scenes=[
            Scene(
                scene_id="scene_001",
                title="Opening",
                shots=[
                    ShotDescription(
                        shot_id="shot_001",
                        description="Hero at sunrise",
                        duration_seconds=5,
                    )
                ],
            )
        ],
        total_duration=5.0,
    )


@pytest.fixture
def mock_storyboard(mock_script):
    """Create a mock storyboard."""
    return StoryboardResult(
        title=mock_script.title,
        scenes=mock_script.scenes,
        images=[
            ImageOutput(
                image_path="/tmp/shot_001.png",
                prompt="Hero at sunrise",
            )
        ],
        total_cost=0.003,
    )


class TestIdea2VideoPipeline:
    """Tests for Idea2VideoPipeline."""

    @pytest.fixture
    def pipeline_config(self, tmp_path):
        return Idea2VideoConfig(
            output_dir=str(tmp_path / "output"),
            generate_portraits=False,  # Skip for faster tests
        )

    @pytest.mark.asyncio
    async def test_pipeline_success(self, pipeline_config, mock_script, mock_storyboard):
        """Test successful pipeline execution."""
        pipeline = Idea2VideoPipeline(pipeline_config)

        # Mock all agents
        pipeline.screenwriter.process = AsyncMock(return_value=AgentResult.ok(
            mock_script, cost=0.01
        ))
        pipeline.character_extractor.process = AsyncMock(return_value=AgentResult.ok(
            [], cost=0.01
        ))
        pipeline.storyboard_artist.process = AsyncMock(return_value=AgentResult.ok(
            mock_storyboard, cost=0.003
        ))
        pipeline.camera_generator.process = AsyncMock(return_value=AgentResult.ok(
            PipelineOutput(
                pipeline_name="test",
                videos=[VideoOutput(video_path="/tmp/video.mp4", duration=5)],
                final_video=VideoOutput(video_path="/tmp/final.mp4", duration=5),
            ),
            cost=0.15,
        ))

        result = await pipeline.run("A samurai at sunrise")

        assert result.success
        assert result.script is not None
        assert result.output is not None
        assert result.total_cost > 0

    @pytest.mark.asyncio
    async def test_pipeline_script_failure(self, pipeline_config):
        """Test pipeline handles script generation failure."""
        pipeline = Idea2VideoPipeline(pipeline_config)

        pipeline.screenwriter.process = AsyncMock(return_value=AgentResult.fail(
            "LLM error"
        ))

        result = await pipeline.run("A samurai at sunrise")

        assert not result.success
        assert len(result.errors) > 0
        assert "Script generation failed" in result.errors[0]


class TestScript2VideoPipeline:
    """Tests for Script2VideoPipeline."""

    @pytest.fixture
    def pipeline_config(self, tmp_path):
        return Script2VideoConfig(
            output_dir=str(tmp_path / "output"),
        )

    @pytest.mark.asyncio
    async def test_pipeline_with_script_object(self, pipeline_config, mock_script, mock_storyboard):
        """Test pipeline with Script object input."""
        pipeline = Script2VideoPipeline(pipeline_config)

        pipeline.storyboard_artist.process = AsyncMock(return_value=AgentResult.ok(
            mock_storyboard, cost=0.003
        ))
        pipeline.camera_generator.process = AsyncMock(return_value=AgentResult.ok(
            PipelineOutput(
                pipeline_name="test",
                final_video=VideoOutput(video_path="/tmp/final.mp4", duration=5),
            ),
            cost=0.15,
        ))

        result = await pipeline.run(mock_script)

        assert result.success
        assert result.output is not None

    @pytest.mark.asyncio
    async def test_pipeline_with_dict_input(self, pipeline_config, mock_storyboard):
        """Test pipeline with dict input."""
        pipeline = Script2VideoPipeline(pipeline_config)

        pipeline.storyboard_artist.process = AsyncMock(return_value=AgentResult.ok(
            mock_storyboard, cost=0.003
        ))
        pipeline.camera_generator.process = AsyncMock(return_value=AgentResult.ok(
            PipelineOutput(
                pipeline_name="test",
                final_video=VideoOutput(video_path="/tmp/final.mp4", duration=5),
            ),
            cost=0.15,
        ))

        script_dict = {
            "title": "Test",
            "scenes": [],
        }

        result = await pipeline.run(script_dict)

        assert result.success
```

---

## Phase 4 Completion Checklist

- [ ] **4.1** Idea2VideoPipeline implemented
- [ ] **4.2** Script2VideoPipeline implemented
- [ ] **4.3** Novel2MoviePipeline implemented
- [ ] **4.4** Exports updated
- [ ] **4.5** Pipeline tests passing

### Verification Commands

```bash
# Test imports
python -c "from ai_content_platform.vimax.pipelines import *; print('Pipelines OK')"

# Run pipeline tests
pytest tests/unit/vimax/test_pipelines.py -v

# Quick integration test
python -c "
import asyncio
from ai_content_platform.vimax.pipelines import Idea2VideoPipeline, Idea2VideoConfig

async def test():
    config = Idea2VideoConfig(generate_portraits=False)
    pipeline = Idea2VideoPipeline(config)
    print('Pipeline initialized successfully')

asyncio.run(test())
"
```

---

*Previous Phase*: [PHASE_3_AGENTS.md](./PHASE_3_AGENTS.md)
*Next Phase*: [PHASE_5_CLI_TESTING.md](./PHASE_5_CLI_TESTING.md)
