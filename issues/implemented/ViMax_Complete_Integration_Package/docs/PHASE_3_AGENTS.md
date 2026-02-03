# Phase 3: Agent Migration

**Duration**: 3-5 days
**Dependencies**: Phase 2 completed (Adapters)
**Outcome**: All ViMax agents migrated and working with adapters

---

## Overview

Agents are LLM-powered components that perform specific tasks in the pipeline. Each agent uses adapters to interact with underlying services.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Layer                               │
├───────────────┬───────────────┬───────────────┬─────────────────┤
│ Character     │ Screenwriter  │ Storyboard    │ Camera          │
│ Extractor     │               │ Artist        │ Generator       │
├───────────────┼───────────────┼───────────────┼─────────────────┤
│ Character     │ Reference     │ Script        │ Scene           │
│ Portraits     │ Selector      │ Planner       │ Extractor       │
└───────────────┴───────────────┴───────────────┴─────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Adapter Layer                               │
│         LLMAdapter | ImageAdapter | VideoAdapter                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Subtask 3.1: CharacterExtractor Agent

**Estimated Time**: 3-4 hours

### Description
Extract character information from scripts/novels using LLM.

### Source Reference
```
issues/todo/ViMax_Complete_Integration_Package/src/agents/character_extractor.py
```

### Target File
```
packages/core/ai_content_platform/vimax/agents/character_extractor.py
```

### Implementation

```python
"""
Character Extractor Agent

Extracts character information from scripts, novels, or story text
using LLM analysis.
"""

from typing import List, Optional
import logging

from .base import BaseAgent, AgentConfig, AgentResult
from ..adapters import LLMAdapter, LLMAdapterConfig, Message
from ..interfaces import CharacterInNovel


class CharacterExtractorConfig(AgentConfig):
    """Configuration for CharacterExtractor."""

    name: str = "CharacterExtractor"
    model: str = "claude-3.5-sonnet"
    max_characters: int = 20


EXTRACTION_PROMPT = """You are an expert story analyst. Extract all characters from the following text.

For each character, provide:
- name: Character's name
- description: Brief description
- age: Age or age range (if mentioned or can be inferred)
- gender: Gender (if mentioned or can be inferred)
- appearance: Physical appearance description
- personality: Personality traits
- role: Role in the story (protagonist, antagonist, supporting, minor)
- relationships: List of relationships with other characters

Return a JSON array of characters. Only include characters that appear in the text.
If a field cannot be determined, use an empty string or empty list.

TEXT:
{text}

Respond ONLY with a JSON array, no other text."""


class CharacterExtractor(BaseAgent[str, List[CharacterInNovel]]):
    """
    Agent that extracts character information from text.

    Usage:
        extractor = CharacterExtractor()
        result = await extractor.process(novel_text)
        if result.success:
            for char in result.result:
                print(f"Found character: {char.name}")
    """

    def __init__(self, config: Optional[CharacterExtractorConfig] = None):
        super().__init__(config or CharacterExtractorConfig())
        self.config: CharacterExtractorConfig = self.config
        self._llm: Optional[LLMAdapter] = None
        self.logger = logging.getLogger("vimax.agents.character_extractor")

    async def _ensure_llm(self):
        """Initialize LLM adapter if needed."""
        if self._llm is None:
            self._llm = LLMAdapter(LLMAdapterConfig(model=self.config.model))
            await self._llm.initialize()

    async def process(self, text: str) -> AgentResult[List[CharacterInNovel]]:
        """
        Extract characters from text.

        Args:
            text: Story text, script, or novel content

        Returns:
            AgentResult containing list of extracted characters
        """
        await self._ensure_llm()

        self.logger.info(f"Extracting characters from text ({len(text)} chars)")

        try:
            # Build prompt
            prompt = EXTRACTION_PROMPT.format(text=text[:50000])  # Limit text length

            messages = [
                Message(role="user", content=prompt)
            ]

            # Call LLM with structured output
            response = await self._llm.chat(messages, temperature=0.3)

            # Parse response
            import json
            try:
                data = json.loads(response.content)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                else:
                    raise ValueError("Could not parse character data from response")

            # Convert to CharacterInNovel objects
            characters = []
            for item in data[:self.config.max_characters]:
                char = CharacterInNovel(
                    name=item.get("name", "Unknown"),
                    description=item.get("description", ""),
                    age=item.get("age"),
                    gender=item.get("gender"),
                    appearance=item.get("appearance", ""),
                    personality=item.get("personality", ""),
                    role=item.get("role", ""),
                    relationships=item.get("relationships", []),
                )
                characters.append(char)

            self.logger.info(f"Extracted {len(characters)} characters")

            return AgentResult.ok(
                characters,
                character_count=len(characters),
                cost=response.cost,
            )

        except Exception as e:
            self.logger.error(f"Character extraction failed: {e}")
            return AgentResult.fail(str(e))

    async def extract_main_characters(
        self,
        text: str,
        max_characters: int = 5,
    ) -> List[CharacterInNovel]:
        """
        Extract only main characters.

        Args:
            text: Story text
            max_characters: Maximum number of main characters

        Returns:
            List of main characters
        """
        result = await self.process(text)
        if not result.success:
            return []

        # Filter to main characters (protagonist, antagonist, supporting)
        main_roles = {"protagonist", "antagonist", "supporting"}
        main_chars = [
            c for c in result.result
            if c.role.lower() in main_roles
        ]

        return main_chars[:max_characters]
```

### Unit Tests

**File**: `tests/unit/vimax/test_agents.py`

```python
"""
Tests for ViMax agents.
"""

import pytest
from unittest.mock import AsyncMock, patch
import json

from ai_content_platform.vimax.agents.character_extractor import (
    CharacterExtractor,
    CharacterExtractorConfig,
)
from ai_content_platform.vimax.interfaces import CharacterInNovel
from ai_content_platform.vimax.adapters import LLMResponse


class TestCharacterExtractor:
    """Tests for CharacterExtractor agent."""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response with character data."""
        characters = [
            {
                "name": "John",
                "description": "A brave warrior",
                "age": "25",
                "gender": "male",
                "appearance": "Tall with dark hair",
                "personality": "Brave and determined",
                "role": "protagonist",
                "relationships": ["Friend of Mary"],
            },
            {
                "name": "Mary",
                "description": "A wise healer",
                "age": "23",
                "gender": "female",
                "appearance": "Short with red hair",
                "personality": "Kind and intelligent",
                "role": "supporting",
                "relationships": ["Friend of John"],
            },
        ]
        return LLMResponse(
            content=json.dumps(characters),
            model="claude-3.5-sonnet",
            usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
            cost=0.01,
        )

    @pytest.mark.asyncio
    async def test_extract_characters(self, mock_llm_response):
        """Test character extraction."""
        extractor = CharacterExtractor()

        with patch.object(extractor, '_llm') as mock_llm:
            mock_llm.chat = AsyncMock(return_value=mock_llm_response)
            extractor._llm = mock_llm

            result = await extractor.process("John and Mary went on an adventure...")

            assert result.success
            assert len(result.result) == 2
            assert result.result[0].name == "John"
            assert result.result[1].name == "Mary"

    @pytest.mark.asyncio
    async def test_extract_main_characters(self, mock_llm_response):
        """Test main character extraction."""
        extractor = CharacterExtractor()

        with patch.object(extractor, '_llm') as mock_llm:
            mock_llm.chat = AsyncMock(return_value=mock_llm_response)
            extractor._llm = mock_llm

            chars = await extractor.extract_main_characters(
                "John and Mary went on an adventure...",
                max_characters=1,
            )

            # Should only return protagonist
            assert len(chars) == 1
            assert chars[0].role == "protagonist"

    @pytest.mark.asyncio
    async def test_extraction_failure(self):
        """Test handling of extraction failure."""
        extractor = CharacterExtractor()

        with patch.object(extractor, '_llm') as mock_llm:
            mock_llm.chat = AsyncMock(side_effect=Exception("LLM error"))
            extractor._llm = mock_llm

            result = await extractor.process("Some text")

            assert not result.success
            assert "LLM error" in result.error
```

---

## Subtask 3.2: CharacterPortraitsGenerator Agent

**Estimated Time**: 3-4 hours

### Description
Generate multi-angle character portraits from character descriptions.

### Target File
```
packages/core/ai_content_platform/vimax/agents/character_portraits.py
```

### Implementation

```python
"""
Character Portraits Generator Agent

Generates multi-angle character portraits (front, side, back, 3/4)
from character descriptions to ensure visual consistency.
"""

from typing import List, Optional, Dict
import logging

from .base import BaseAgent, AgentConfig, AgentResult
from ..adapters import ImageGeneratorAdapter, ImageAdapterConfig, LLMAdapter, Message
from ..interfaces import CharacterInNovel, CharacterPortrait


class PortraitsGeneratorConfig(AgentConfig):
    """Configuration for CharacterPortraitsGenerator."""

    name: str = "CharacterPortraitsGenerator"
    image_model: str = "flux_dev"
    llm_model: str = "claude-3.5-sonnet"
    views: List[str] = ["front", "side", "back", "three_quarter"]
    style: str = "detailed character portrait, professional, consistent style"
    output_dir: str = "output/vimax/portraits"


PORTRAIT_PROMPT_TEMPLATE = """Create a detailed image generation prompt for a {view} view portrait.

CHARACTER INFORMATION:
Name: {name}
Description: {description}
Appearance: {appearance}
Age: {age}
Gender: {gender}

STYLE: {style}

Generate a single, detailed prompt that will create a {view} view portrait of this character.
The prompt should include specific details about pose, lighting, and composition for a {view} view.
Keep the character's appearance consistent across all views.

Respond with ONLY the image generation prompt, no other text."""


class CharacterPortraitsGenerator(BaseAgent[CharacterInNovel, CharacterPortrait]):
    """
    Agent that generates multi-angle character portraits.

    Usage:
        generator = CharacterPortraitsGenerator()
        result = await generator.process(character)
        if result.success:
            portrait = result.result
            print(f"Front view: {portrait.front_view}")
    """

    def __init__(self, config: Optional[PortraitsGeneratorConfig] = None):
        super().__init__(config or PortraitsGeneratorConfig())
        self.config: PortraitsGeneratorConfig = self.config
        self._image_adapter: Optional[ImageGeneratorAdapter] = None
        self._llm: Optional[LLMAdapter] = None
        self.logger = logging.getLogger("vimax.agents.portraits_generator")

    async def _ensure_adapters(self):
        """Initialize adapters if needed."""
        if self._image_adapter is None:
            self._image_adapter = ImageGeneratorAdapter(
                ImageAdapterConfig(
                    model=self.config.image_model,
                    output_dir=self.config.output_dir,
                )
            )
            await self._image_adapter.initialize()

        if self._llm is None:
            from ..adapters import LLMAdapterConfig
            self._llm = LLMAdapter(LLMAdapterConfig(model=self.config.llm_model))
            await self._llm.initialize()

    async def _generate_prompt(
        self,
        character: CharacterInNovel,
        view: str,
    ) -> str:
        """Generate optimized prompt for a specific view."""
        prompt = PORTRAIT_PROMPT_TEMPLATE.format(
            view=view,
            name=character.name,
            description=character.description,
            appearance=character.appearance,
            age=character.age or "unknown",
            gender=character.gender or "unknown",
            style=self.config.style,
        )

        response = await self._llm.chat([Message(role="user", content=prompt)])
        return response.content.strip()

    async def process(self, character: CharacterInNovel) -> AgentResult[CharacterPortrait]:
        """
        Generate portraits for a character.

        Args:
            character: Character information

        Returns:
            AgentResult containing CharacterPortrait with paths to generated images
        """
        await self._ensure_adapters()

        self.logger.info(f"Generating portraits for character: {character.name}")

        try:
            portrait = CharacterPortrait(character_name=character.name)
            total_cost = 0.0

            for view in self.config.views:
                self.logger.info(f"Generating {view} view for {character.name}")

                # Generate optimized prompt
                prompt = await self._generate_prompt(character, view)

                # Generate image
                result = await self._image_adapter.generate(
                    prompt=prompt,
                    aspect_ratio="1:1",
                )

                total_cost += result.cost

                # Set the appropriate view
                if view == "front":
                    portrait.front_view = result.image_path
                elif view == "side":
                    portrait.side_view = result.image_path
                elif view == "back":
                    portrait.back_view = result.image_path
                elif view == "three_quarter":
                    portrait.three_quarter_view = result.image_path

            self.logger.info(f"Generated {len(portrait.views)} portraits for {character.name}")

            return AgentResult.ok(
                portrait,
                views_generated=len(portrait.views),
                cost=total_cost,
            )

        except Exception as e:
            self.logger.error(f"Portrait generation failed: {e}")
            return AgentResult.fail(str(e))

    async def generate_batch(
        self,
        characters: List[CharacterInNovel],
    ) -> Dict[str, CharacterPortrait]:
        """
        Generate portraits for multiple characters.

        Args:
            characters: List of characters

        Returns:
            Dict mapping character names to portraits
        """
        portraits = {}
        for char in characters:
            result = await self.process(char)
            if result.success:
                portraits[char.name] = result.result
        return portraits
```

---

## Subtask 3.3: Screenwriter Agent

**Estimated Time**: 3-4 hours

### Description
Generate screenplay/script from an idea or story outline.

### Target File
```
packages/core/ai_content_platform/vimax/agents/screenwriter.py
```

### Implementation

```python
"""
Screenwriter Agent

Generates screenplay/script content from ideas, outlines, or stories.
Produces structured scripts with scenes, dialogue, and action descriptions.
"""

from typing import Optional, List
import logging

from pydantic import BaseModel, Field

from .base import BaseAgent, AgentConfig, AgentResult
from ..adapters import LLMAdapter, LLMAdapterConfig, Message
from ..interfaces import Scene, ShotDescription, ShotType


class Script(BaseModel):
    """Generated script structure."""

    title: str
    logline: str = ""  # One-sentence summary
    scenes: List[Scene] = Field(default_factory=list)
    total_duration: float = 0.0

    @property
    def scene_count(self) -> int:
        return len(self.scenes)


class ScreenwriterConfig(AgentConfig):
    """Configuration for Screenwriter."""

    name: str = "Screenwriter"
    model: str = "claude-3.5-sonnet"
    target_duration: float = 60.0  # Target video duration in seconds
    shots_per_scene: int = 3
    style: str = "cinematic, visually descriptive"


SCREENPLAY_PROMPT = """You are an expert screenwriter specializing in visual storytelling for AI video generation.

Create a detailed screenplay from this idea:
{idea}

Requirements:
- Target duration: {duration} seconds
- Style: {style}
- Number of scenes: {num_scenes}
- Shots per scene: {shots_per_scene}

For each scene, provide:
1. Scene title and location
2. Time of day and lighting
3. Multiple shots with:
   - Shot type (wide, medium, close_up, etc.)
   - Visual description (what we SEE)
   - Camera movement if any
   - Duration in seconds

Format your response as JSON with this structure:
{{
    "title": "Video Title",
    "logline": "One sentence summary",
    "scenes": [
        {{
            "scene_id": "scene_001",
            "title": "Scene Title",
            "location": "Location description",
            "time": "Time of day",
            "shots": [
                {{
                    "shot_id": "shot_001",
                    "shot_type": "wide",
                    "description": "Visual description",
                    "camera_movement": "static",
                    "duration_seconds": 5,
                    "image_prompt": "Detailed prompt for image generation",
                    "video_prompt": "Motion/animation description"
                }}
            ]
        }}
    ]
}}

Focus on VISUAL descriptions - what the camera sees, not dialogue or internal thoughts.
Each image_prompt should be detailed enough for AI image generation.
Each video_prompt should describe the motion/animation for that shot."""


class Screenwriter(BaseAgent[str, Script]):
    """
    Agent that generates screenplays from ideas.

    Usage:
        writer = Screenwriter()
        result = await writer.process("A samurai's journey at sunrise")
        if result.success:
            script = result.result
            for scene in script.scenes:
                print(f"Scene: {scene.title}")
    """

    def __init__(self, config: Optional[ScreenwriterConfig] = None):
        super().__init__(config or ScreenwriterConfig())
        self.config: ScreenwriterConfig = self.config
        self._llm: Optional[LLMAdapter] = None
        self.logger = logging.getLogger("vimax.agents.screenwriter")

    async def _ensure_llm(self):
        if self._llm is None:
            self._llm = LLMAdapter(LLMAdapterConfig(model=self.config.model))
            await self._llm.initialize()

    async def process(self, idea: str) -> AgentResult[Script]:
        """
        Generate screenplay from idea.

        Args:
            idea: Story idea or concept

        Returns:
            AgentResult containing generated Script
        """
        await self._ensure_llm()

        self.logger.info(f"Generating screenplay for: {idea[:100]}...")

        try:
            # Calculate scene count based on target duration
            avg_shot_duration = 5.0
            total_shots = self.config.target_duration / avg_shot_duration
            num_scenes = max(1, int(total_shots / self.config.shots_per_scene))

            prompt = SCREENPLAY_PROMPT.format(
                idea=idea,
                duration=self.config.target_duration,
                style=self.config.style,
                num_scenes=num_scenes,
                shots_per_scene=self.config.shots_per_scene,
            )

            response = await self._llm.chat(
                [Message(role="user", content=prompt)],
                temperature=0.7,
            )

            # Parse response
            import json
            import re

            content = response.content
            # Extract JSON from response
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                raise ValueError("Could not parse screenplay JSON")

            # Build Script object
            scenes = []
            total_duration = 0.0

            for scene_data in data.get("scenes", []):
                shots = []
                for shot_data in scene_data.get("shots", []):
                    shot = ShotDescription(
                        shot_id=shot_data.get("shot_id", f"shot_{len(shots)+1}"),
                        shot_type=ShotType(shot_data.get("shot_type", "medium")),
                        description=shot_data.get("description", ""),
                        camera_movement=shot_data.get("camera_movement", "static"),
                        duration_seconds=shot_data.get("duration_seconds", 5.0),
                        image_prompt=shot_data.get("image_prompt"),
                        video_prompt=shot_data.get("video_prompt"),
                    )
                    shots.append(shot)
                    total_duration += shot.duration_seconds

                scene = Scene(
                    scene_id=scene_data.get("scene_id", f"scene_{len(scenes)+1}"),
                    title=scene_data.get("title", ""),
                    description=scene_data.get("description", ""),
                    location=scene_data.get("location", ""),
                    time=scene_data.get("time", ""),
                    shots=shots,
                )
                scenes.append(scene)

            script = Script(
                title=data.get("title", "Untitled"),
                logline=data.get("logline", ""),
                scenes=scenes,
                total_duration=total_duration,
            )

            self.logger.info(
                f"Generated screenplay: {script.scene_count} scenes, "
                f"{sum(s.shot_count for s in script.scenes)} shots, "
                f"{total_duration:.1f}s total"
            )

            return AgentResult.ok(
                script,
                scene_count=script.scene_count,
                shot_count=sum(s.shot_count for s in script.scenes),
                duration=total_duration,
                cost=response.cost,
            )

        except Exception as e:
            self.logger.error(f"Screenplay generation failed: {e}")
            return AgentResult.fail(str(e))
```

---

## Subtask 3.4: StoryboardArtist Agent

**Estimated Time**: 3-4 hours

### Description
Generate visual storyboard images from script/screenplay.

### Target File
```
packages/core/ai_content_platform/vimax/agents/storyboard_artist.py
```

### Implementation

```python
"""
Storyboard Artist Agent

Generates visual storyboard images from scripts or shot descriptions.
Creates consistent visual representations for each shot.
"""

from typing import Optional, List
import logging
from pathlib import Path

from .base import BaseAgent, AgentConfig, AgentResult
from .screenwriter import Script
from ..adapters import ImageGeneratorAdapter, ImageAdapterConfig
from ..interfaces import (
    Storyboard, Scene, ShotDescription, ImageOutput,
)


class StoryboardResult(Storyboard):
    """Storyboard with generated images."""

    images: List[ImageOutput] = []
    total_cost: float = 0.0


class StoryboardArtistConfig(AgentConfig):
    """Configuration for StoryboardArtist."""

    name: str = "StoryboardArtist"
    image_model: str = "flux_dev"
    style_prefix: str = "storyboard panel, cinematic composition, "
    aspect_ratio: str = "16:9"
    output_dir: str = "output/vimax/storyboard"


class StoryboardArtist(BaseAgent[Script, StoryboardResult]):
    """
    Agent that generates storyboard images from scripts.

    Usage:
        artist = StoryboardArtist()
        result = await artist.process(script)
        if result.success:
            for img in result.result.images:
                print(f"Generated: {img.image_path}")
    """

    def __init__(self, config: Optional[StoryboardArtistConfig] = None):
        super().__init__(config or StoryboardArtistConfig())
        self.config: StoryboardArtistConfig = self.config
        self._image_adapter: Optional[ImageGeneratorAdapter] = None
        self.logger = logging.getLogger("vimax.agents.storyboard_artist")

    async def _ensure_adapter(self):
        if self._image_adapter is None:
            self._image_adapter = ImageGeneratorAdapter(
                ImageAdapterConfig(
                    model=self.config.image_model,
                    output_dir=self.config.output_dir,
                )
            )
            await self._image_adapter.initialize()

    def _build_prompt(self, shot: ShotDescription, scene: Scene) -> str:
        """Build image generation prompt from shot description."""
        parts = [self.config.style_prefix]

        # Add scene context
        if scene.location:
            parts.append(f"Location: {scene.location}.")
        if scene.time:
            parts.append(f"Time: {scene.time}.")

        # Add shot description
        if shot.image_prompt:
            parts.append(shot.image_prompt)
        else:
            parts.append(shot.description)

        # Add shot type context
        shot_type_hints = {
            "wide": "wide establishing shot, full scene visible",
            "medium": "medium shot, subject framed from waist up",
            "close_up": "close-up shot, face and expression detail",
            "extreme_close_up": "extreme close-up, detail shot",
        }
        if shot.shot_type.value in shot_type_hints:
            parts.append(shot_type_hints[shot.shot_type.value])

        return " ".join(parts)

    async def process(self, script: Script) -> AgentResult[StoryboardResult]:
        """
        Generate storyboard from script.

        Args:
            script: Script with scenes and shots

        Returns:
            AgentResult containing StoryboardResult with images
        """
        await self._ensure_adapter()

        self.logger.info(f"Generating storyboard for: {script.title}")

        try:
            images = []
            total_cost = 0.0

            # Create output directory
            output_dir = Path(self.config.output_dir) / script.title.replace(" ", "_")
            output_dir.mkdir(parents=True, exist_ok=True)

            shot_index = 0
            for scene in script.scenes:
                self.logger.info(f"Processing scene: {scene.title}")

                for shot in scene.shots:
                    shot_index += 1
                    self.logger.info(f"Generating shot {shot_index}: {shot.shot_id}")

                    # Build prompt
                    prompt = self._build_prompt(shot, scene)

                    # Generate image
                    output_path = str(output_dir / f"{shot.shot_id}.png")
                    result = await self._image_adapter.generate(
                        prompt=prompt,
                        aspect_ratio=self.config.aspect_ratio,
                        output_path=output_path,
                    )

                    images.append(result)
                    total_cost += result.cost

            # Build storyboard result
            storyboard = StoryboardResult(
                title=script.title,
                description=script.logline,
                scenes=script.scenes,
                images=images,
                total_cost=total_cost,
            )

            self.logger.info(
                f"Generated storyboard: {len(images)} images, "
                f"${total_cost:.3f} total cost"
            )

            return AgentResult.ok(
                storyboard,
                image_count=len(images),
                cost=total_cost,
            )

        except Exception as e:
            self.logger.error(f"Storyboard generation failed: {e}")
            return AgentResult.fail(str(e))

    async def generate_from_shots(
        self,
        shots: List[ShotDescription],
        title: str = "Storyboard",
    ) -> List[ImageOutput]:
        """
        Generate images directly from shot descriptions.

        Args:
            shots: List of shot descriptions
            title: Storyboard title

        Returns:
            List of generated images
        """
        await self._ensure_adapter()

        images = []
        output_dir = Path(self.config.output_dir) / title.replace(" ", "_")
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, shot in enumerate(shots):
            prompt = f"{self.config.style_prefix} {shot.image_prompt or shot.description}"
            output_path = str(output_dir / f"shot_{i+1:03d}.png")

            result = await self._image_adapter.generate(
                prompt=prompt,
                aspect_ratio=self.config.aspect_ratio,
                output_path=output_path,
            )
            images.append(result)

        return images
```

---

## Subtask 3.5: CameraImageGenerator Agent

**Estimated Time**: 3-4 hours

### Description
Generate videos from storyboard images with camera movements.

### Target File
```
packages/core/ai_content_platform/vimax/agents/camera_generator.py
```

### Implementation

```python
"""
Camera Image Generator Agent

Generates videos from storyboard images, applying camera movements
and animations based on shot descriptions.
"""

from typing import Optional, List
import logging
from pathlib import Path

from .base import BaseAgent, AgentConfig, AgentResult
from .storyboard_artist import StoryboardResult
from ..adapters import VideoGeneratorAdapter, VideoAdapterConfig
from ..interfaces import (
    ShotDescription, ImageOutput, VideoOutput, PipelineOutput,
)


class CameraGeneratorConfig(AgentConfig):
    """Configuration for CameraImageGenerator."""

    name: str = "CameraImageGenerator"
    video_model: str = "kling"
    default_duration: float = 5.0
    output_dir: str = "output/vimax/videos"


class CameraImageGenerator(BaseAgent[StoryboardResult, PipelineOutput]):
    """
    Agent that generates videos from storyboard images.

    Usage:
        generator = CameraImageGenerator()
        result = await generator.process(storyboard)
        if result.success:
            print(f"Final video: {result.result.final_video.video_path}")
    """

    def __init__(self, config: Optional[CameraGeneratorConfig] = None):
        super().__init__(config or CameraGeneratorConfig())
        self.config: CameraGeneratorConfig = self.config
        self._video_adapter: Optional[VideoGeneratorAdapter] = None
        self.logger = logging.getLogger("vimax.agents.camera_generator")

    async def _ensure_adapter(self):
        if self._video_adapter is None:
            self._video_adapter = VideoGeneratorAdapter(
                VideoAdapterConfig(
                    model=self.config.video_model,
                    output_dir=self.config.output_dir,
                )
            )
            await self._video_adapter.initialize()

    def _get_motion_prompt(self, shot: ShotDescription) -> str:
        """Generate motion prompt from shot description."""
        parts = []

        # Use video_prompt if available
        if shot.video_prompt:
            parts.append(shot.video_prompt)
        else:
            # Build from shot description
            parts.append(shot.description)

        # Add camera movement hints
        movement_hints = {
            "pan": "smooth horizontal camera pan",
            "tilt": "smooth vertical camera tilt",
            "zoom": "gradual zoom",
            "dolly": "camera moving forward/backward",
            "tracking": "camera tracking subject movement",
            "static": "subtle ambient motion, no camera movement",
        }

        movement = shot.camera_movement
        if hasattr(movement, 'value'):
            movement = movement.value

        if movement in movement_hints:
            parts.append(movement_hints[movement])

        return ", ".join(parts)

    async def process(self, storyboard: StoryboardResult) -> AgentResult[PipelineOutput]:
        """
        Generate videos from storyboard.

        Args:
            storyboard: Storyboard with images

        Returns:
            AgentResult containing PipelineOutput with videos
        """
        await self._ensure_adapter()

        self.logger.info(f"Generating videos for: {storyboard.title}")

        try:
            output = PipelineOutput(
                pipeline_name=f"camera_generator_{storyboard.title}",
                output_directory=self.config.output_dir,
            )

            # Create output directory
            output_dir = Path(self.config.output_dir) / storyboard.title.replace(" ", "_")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Match images with shots
            image_index = 0
            for scene in storyboard.scenes:
                for shot in scene.shots:
                    if image_index >= len(storyboard.images):
                        break

                    image = storyboard.images[image_index]
                    image_index += 1

                    self.logger.info(f"Generating video for shot: {shot.shot_id}")

                    # Get motion prompt
                    motion_prompt = self._get_motion_prompt(shot)

                    # Generate video
                    output_path = str(output_dir / f"{shot.shot_id}.mp4")
                    video = await self._video_adapter.generate(
                        image_path=image.image_path,
                        prompt=motion_prompt,
                        duration=shot.duration_seconds or self.config.default_duration,
                        output_path=output_path,
                    )

                    output.add_video(video)

            # Concatenate all videos
            if output.videos:
                final_path = str(output_dir / "final_video.mp4")
                final_video = await self._video_adapter.concatenate_videos(
                    output.videos,
                    final_path,
                )
                output.final_video = final_video

            from datetime import datetime
            output.completed_at = datetime.now()

            self.logger.info(
                f"Generated {len(output.videos)} videos, "
                f"final duration: {output.final_video.duration:.1f}s"
            )

            return AgentResult.ok(
                output,
                video_count=len(output.videos),
                total_duration=output.final_video.duration if output.final_video else 0,
                cost=output.total_cost,
            )

        except Exception as e:
            self.logger.error(f"Video generation failed: {e}")
            return AgentResult.fail(str(e))

    async def generate_from_images(
        self,
        images: List[ImageOutput],
        prompts: List[str],
        durations: Optional[List[float]] = None,
    ) -> List[VideoOutput]:
        """
        Generate videos from images with prompts.

        Args:
            images: List of input images
            prompts: Motion prompts for each image
            durations: Optional durations for each video

        Returns:
            List of generated videos
        """
        await self._ensure_adapter()

        if len(images) != len(prompts):
            raise ValueError("Number of images must match number of prompts")

        durations = durations or [self.config.default_duration] * len(images)

        videos = []
        for i, (img, prompt, duration) in enumerate(zip(images, prompts, durations)):
            video = await self._video_adapter.generate(
                image_path=img.image_path,
                prompt=prompt,
                duration=duration,
            )
            videos.append(video)

        return videos
```

---

## Subtask 3.6: Update Agent Exports

**Estimated Time**: 30 minutes

### File: `packages/core/ai_content_platform/vimax/agents/__init__.py`

```python
"""
ViMax Agents

LLM-powered agents for content generation pipeline.
"""

from .base import BaseAgent, AgentConfig, AgentResult
from .character_extractor import CharacterExtractor, CharacterExtractorConfig
from .character_portraits import CharacterPortraitsGenerator, PortraitsGeneratorConfig
from .screenwriter import Screenwriter, ScreenwriterConfig, Script
from .storyboard_artist import StoryboardArtist, StoryboardArtistConfig, StoryboardResult
from .camera_generator import CameraImageGenerator, CameraGeneratorConfig

__all__ = [
    # Base
    "BaseAgent",
    "AgentConfig",
    "AgentResult",
    # Agents
    "CharacterExtractor",
    "CharacterExtractorConfig",
    "CharacterPortraitsGenerator",
    "PortraitsGeneratorConfig",
    "Screenwriter",
    "ScreenwriterConfig",
    "Script",
    "StoryboardArtist",
    "StoryboardArtistConfig",
    "StoryboardResult",
    "CameraImageGenerator",
    "CameraGeneratorConfig",
]
```

---

## Phase 3 Completion Checklist

- [ ] **3.1** CharacterExtractor implemented
- [ ] **3.2** CharacterPortraitsGenerator implemented
- [ ] **3.3** Screenwriter implemented
- [ ] **3.4** StoryboardArtist implemented
- [ ] **3.5** CameraImageGenerator implemented
- [ ] **3.6** Exports updated

### Verification Commands

```bash
# Test imports
python -c "from ai_content_platform.vimax.agents import *; print('Agents OK')"

# Run agent tests
pytest tests/unit/vimax/test_agents.py -v

# Quick integration test
python -c "
import asyncio
from ai_content_platform.vimax.agents import Screenwriter

async def test():
    writer = Screenwriter()
    result = await writer.process('A samurai at sunrise')
    print(f'Success: {result.success}')
    if result.success:
        print(f'Scenes: {result.result.scene_count}')

asyncio.run(test())
"
```

---

*Previous Phase*: [PHASE_2_ADAPTERS.md](./PHASE_2_ADAPTERS.md)
*Next Phase*: [PHASE_4_PIPELINES.md](./PHASE_4_PIPELINES.md)
