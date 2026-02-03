# Phase 1: Infrastructure & Directory Setup

**Duration**: 1-2 days
**Dependencies**: None
**Outcome**: Project structure ready for ViMax integration

---

## Subtask 1.1: Create Directory Structure

**Estimated Time**: 30 minutes

### Description
Create the directory structure for the ViMax integration module within the existing package.

### Files to Create

```
packages/core/ai_content_platform/vimax/
├── __init__.py
├── adapters/
│   └── __init__.py
├── agents/
│   └── __init__.py
├── interfaces/
│   └── __init__.py
├── pipelines/
│   └── __init__.py
└── cli/
    └── __init__.py
```

### Implementation

```bash
# Create directories
cd packages/core/ai_content_platform
mkdir -p vimax/adapters vimax/agents vimax/interfaces vimax/pipelines vimax/cli

# Create __init__.py files
touch vimax/__init__.py
touch vimax/adapters/__init__.py
touch vimax/agents/__init__.py
touch vimax/interfaces/__init__.py
touch vimax/pipelines/__init__.py
touch vimax/cli/__init__.py
```

### File: `packages/core/ai_content_platform/vimax/__init__.py`

```python
"""
ViMax Integration Module

Novel-to-video pipeline integration with character consistency,
storyboard generation, and multi-agent collaboration.
"""

__version__ = "1.0.0"

from .pipelines import (
    Idea2VideoPipeline,
    Script2VideoPipeline,
    Novel2MoviePipeline,
)

__all__ = [
    "Idea2VideoPipeline",
    "Script2VideoPipeline",
    "Novel2MoviePipeline",
]
```

### Acceptance Criteria
- [ ] All directories created
- [ ] All `__init__.py` files present
- [ ] Package is importable: `from ai_content_platform.vimax import *`

---

## Subtask 1.2: Copy and Adapt Interfaces

**Estimated Time**: 2-3 hours

### Description
Copy ViMax interface definitions and adapt them to use Pydantic v2 patterns consistent with the existing codebase.

### Source Files
```
issues/todo/ViMax_Complete_Integration_Package/src/interfaces/
├── character.py
├── shot_description.py
├── camera.py
├── frame.py
├── scene.py
├── event.py
├── environment.py
├── image_output.py
└── video_output.py
```

### Target Files
```
packages/core/ai_content_platform/vimax/interfaces/
├── __init__.py
├── character.py
├── shot.py
├── camera.py
└── output.py
```

### File: `packages/core/ai_content_platform/vimax/interfaces/character.py`

```python
"""
Character data models for ViMax pipeline.

Handles character information at different levels:
- CharacterInNovel: Full character description from novel
- CharacterInScene: Character appearance in a scene
- CharacterInEvent: Character involvement in an event
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class CharacterBase(BaseModel):
    """Base character model with common fields."""

    name: str = Field(..., description="Character name")
    description: str = Field(default="", description="Character description")

    class Config:
        extra = "allow"  # Allow additional fields for flexibility


class CharacterInNovel(CharacterBase):
    """Full character description extracted from novel."""

    age: Optional[str] = Field(default=None, description="Character age or age range")
    gender: Optional[str] = Field(default=None, description="Character gender")
    appearance: str = Field(default="", description="Physical appearance description")
    personality: str = Field(default="", description="Personality traits")
    role: str = Field(default="", description="Role in the story (protagonist, antagonist, etc.)")
    relationships: List[str] = Field(default_factory=list, description="Relationships with other characters")


class CharacterInScene(CharacterBase):
    """Character appearance in a specific scene."""

    scene_id: Optional[str] = Field(default=None, description="Scene identifier")
    position: Optional[str] = Field(default=None, description="Position in scene")
    action: str = Field(default="", description="What the character is doing")
    emotion: str = Field(default="", description="Emotional state")
    dialogue: Optional[str] = Field(default=None, description="Character dialogue")


class CharacterInEvent(CharacterBase):
    """Character involvement in a specific event."""

    event_id: Optional[str] = Field(default=None, description="Event identifier")
    involvement: str = Field(default="", description="How character is involved")
    importance: int = Field(default=1, ge=1, le=5, description="Importance level 1-5")


class CharacterPortrait(BaseModel):
    """Generated character portrait with multiple angles."""

    character_name: str
    front_view: Optional[str] = Field(default=None, description="Path to front view image")
    side_view: Optional[str] = Field(default=None, description="Path to side view image")
    back_view: Optional[str] = Field(default=None, description="Path to back view image")
    three_quarter_view: Optional[str] = Field(default=None, description="Path to 3/4 view image")

    @property
    def views(self) -> dict:
        """Return all available views as dict."""
        return {
            k: v for k, v in {
                "front": self.front_view,
                "side": self.side_view,
                "back": self.back_view,
                "three_quarter": self.three_quarter_view,
            }.items() if v is not None
        }
```

### File: `packages/core/ai_content_platform/vimax/interfaces/shot.py`

```python
"""
Shot and scene data models for ViMax pipeline.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ShotType(str, Enum):
    """Camera shot types."""
    WIDE = "wide"
    MEDIUM = "medium"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    ESTABLISHING = "establishing"
    OVER_THE_SHOULDER = "over_the_shoulder"
    POV = "pov"
    TWO_SHOT = "two_shot"
    INSERT = "insert"


class CameraMovement(str, Enum):
    """Camera movement types."""
    STATIC = "static"
    PAN = "pan"
    TILT = "tilt"
    ZOOM = "zoom"
    DOLLY = "dolly"
    TRACKING = "tracking"
    CRANE = "crane"
    HANDHELD = "handheld"


class ShotDescription(BaseModel):
    """Complete shot description for video generation."""

    shot_id: str = Field(..., description="Unique shot identifier")
    shot_type: ShotType = Field(default=ShotType.MEDIUM, description="Type of shot")
    description: str = Field(..., description="Visual description of the shot")

    # Camera settings
    camera_movement: CameraMovement = Field(default=CameraMovement.STATIC)
    camera_angle: str = Field(default="eye_level", description="Camera angle")

    # Scene context
    location: str = Field(default="", description="Location/setting")
    time_of_day: str = Field(default="", description="Time of day")
    lighting: str = Field(default="", description="Lighting description")

    # Characters
    characters: List[str] = Field(default_factory=list, description="Characters in shot")

    # Duration
    duration_seconds: float = Field(default=5.0, ge=1.0, le=60.0)

    # Generation prompts
    image_prompt: Optional[str] = Field(default=None, description="Prompt for image generation")
    video_prompt: Optional[str] = Field(default=None, description="Prompt for video generation")


class ShotBriefDescription(BaseModel):
    """Simplified shot description for quick reference."""

    shot_id: str
    shot_type: ShotType
    brief: str = Field(..., max_length=200, description="Brief shot description")


class Scene(BaseModel):
    """Scene containing multiple shots."""

    scene_id: str = Field(..., description="Unique scene identifier")
    title: str = Field(default="", description="Scene title")
    description: str = Field(default="", description="Scene description")
    location: str = Field(default="", description="Scene location")
    time: str = Field(default="", description="Time context")
    shots: List[ShotDescription] = Field(default_factory=list)

    @property
    def shot_count(self) -> int:
        return len(self.shots)

    @property
    def total_duration(self) -> float:
        return sum(shot.duration_seconds for shot in self.shots)


class Storyboard(BaseModel):
    """Complete storyboard with scenes and shots."""

    title: str = Field(..., description="Storyboard title")
    description: str = Field(default="", description="Overall description")
    scenes: List[Scene] = Field(default_factory=list)

    @property
    def total_shots(self) -> int:
        return sum(scene.shot_count for scene in self.scenes)

    @property
    def total_duration(self) -> float:
        return sum(scene.total_duration for scene in self.scenes)
```

### File: `packages/core/ai_content_platform/vimax/interfaces/camera.py`

```python
"""
Camera configuration and hierarchy for ViMax pipeline.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class CameraType(str, Enum):
    """Camera types for different shot contexts."""
    MAIN = "main"
    SECONDARY = "secondary"
    DETAIL = "detail"
    ACTION = "action"
    DIALOGUE = "dialogue"


class CameraPosition(BaseModel):
    """Camera position in 3D space."""

    x: float = Field(default=0.0, description="X position")
    y: float = Field(default=0.0, description="Y position (height)")
    z: float = Field(default=0.0, description="Z position (depth)")


class CameraConfig(BaseModel):
    """Camera configuration for shot generation."""

    camera_id: str = Field(..., description="Unique camera identifier")
    camera_type: CameraType = Field(default=CameraType.MAIN)

    # Position and orientation
    position: CameraPosition = Field(default_factory=CameraPosition)
    look_at: Optional[CameraPosition] = Field(default=None)

    # Lens settings
    focal_length: float = Field(default=50.0, ge=10.0, le=200.0, description="Focal length in mm")
    aperture: float = Field(default=2.8, ge=1.0, le=22.0, description="Aperture f-stop")

    # Movement
    movement_type: str = Field(default="static")
    movement_speed: float = Field(default=1.0, ge=0.1, le=10.0)

    # Additional settings
    settings: Dict[str, Any] = Field(default_factory=dict)


class CameraHierarchy(BaseModel):
    """Hierarchical camera setup for complex scenes."""

    scene_id: str
    primary_camera: CameraConfig
    secondary_cameras: List[CameraConfig] = Field(default_factory=list)

    def get_camera(self, camera_id: str) -> Optional[CameraConfig]:
        """Get camera by ID."""
        if self.primary_camera.camera_id == camera_id:
            return self.primary_camera
        for cam in self.secondary_cameras:
            if cam.camera_id == camera_id:
                return cam
        return None

    @property
    def all_cameras(self) -> List[CameraConfig]:
        return [self.primary_camera] + self.secondary_cameras
```

### File: `packages/core/ai_content_platform/vimax/interfaces/output.py`

```python
"""
Output data models for ViMax pipeline.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field
from datetime import datetime


class ImageOutput(BaseModel):
    """Image generation output."""

    image_path: str = Field(..., description="Path to generated image")
    prompt: str = Field(default="", description="Prompt used for generation")
    model: str = Field(default="", description="Model used")
    width: int = Field(default=0)
    height: int = Field(default=0)
    generation_time: float = Field(default=0.0, description="Generation time in seconds")
    cost: float = Field(default=0.0, description="Generation cost in USD")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def exists(self) -> bool:
        return Path(self.image_path).exists()


class VideoOutput(BaseModel):
    """Video generation output."""

    video_path: str = Field(..., description="Path to generated video")
    source_image: Optional[str] = Field(default=None, description="Source image path")
    prompt: str = Field(default="", description="Prompt used for generation")
    model: str = Field(default="", description="Model used")
    duration: float = Field(default=0.0, description="Video duration in seconds")
    width: int = Field(default=0)
    height: int = Field(default=0)
    fps: int = Field(default=24)
    generation_time: float = Field(default=0.0)
    cost: float = Field(default=0.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def exists(self) -> bool:
        return Path(self.video_path).exists()


class PipelineOutput(BaseModel):
    """Complete pipeline output."""

    pipeline_name: str
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(default=None)

    # Outputs
    images: List[ImageOutput] = Field(default_factory=list)
    videos: List[VideoOutput] = Field(default_factory=list)
    final_video: Optional[VideoOutput] = Field(default=None)

    # Metadata
    total_cost: float = Field(default=0.0)
    output_directory: str = Field(default="")
    config_path: Optional[str] = Field(default=None)
    errors: List[str] = Field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0 and self.final_video is not None

    @property
    def duration(self) -> Optional[float]:
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def add_image(self, output: ImageOutput):
        self.images.append(output)
        self.total_cost += output.cost

    def add_video(self, output: VideoOutput):
        self.videos.append(output)
        self.total_cost += output.cost
```

### File: `packages/core/ai_content_platform/vimax/interfaces/__init__.py`

```python
"""
ViMax Interface Definitions

Pydantic models for character, shot, camera, and output data.
"""

from .character import (
    CharacterBase,
    CharacterInNovel,
    CharacterInScene,
    CharacterInEvent,
    CharacterPortrait,
)
from .shot import (
    ShotType,
    CameraMovement,
    ShotDescription,
    ShotBriefDescription,
    Scene,
    Storyboard,
)
from .camera import (
    CameraType,
    CameraPosition,
    CameraConfig,
    CameraHierarchy,
)
from .output import (
    ImageOutput,
    VideoOutput,
    PipelineOutput,
)

__all__ = [
    # Character
    "CharacterBase",
    "CharacterInNovel",
    "CharacterInScene",
    "CharacterInEvent",
    "CharacterPortrait",
    # Shot
    "ShotType",
    "CameraMovement",
    "ShotDescription",
    "ShotBriefDescription",
    "Scene",
    "Storyboard",
    # Camera
    "CameraType",
    "CameraPosition",
    "CameraConfig",
    "CameraHierarchy",
    # Output
    "ImageOutput",
    "VideoOutput",
    "PipelineOutput",
]
```

### Acceptance Criteria
- [ ] All interface files created
- [ ] Models use Pydantic v2 patterns
- [ ] All imports work correctly
- [ ] Type hints complete

---

## Subtask 1.3: Add Dependencies

**Estimated Time**: 30 minutes

### Description
Add required dependencies to requirements.txt and ensure compatibility.

### File: `requirements.txt` (additions)

```
# ViMax Integration Dependencies
litellm>=1.0.0                  # Unified LLM interface
tenacity>=8.0.0                 # Retry logic with backoff
scenedetect[opencv]>=0.6.0      # Scene detection (optional)
```

### Implementation

```bash
# Add to requirements.txt
echo "" >> requirements.txt
echo "# ViMax Integration Dependencies" >> requirements.txt
echo "litellm>=1.0.0" >> requirements.txt
echo "tenacity>=8.0.0" >> requirements.txt
echo "scenedetect[opencv]>=0.6.0" >> requirements.txt

# Install
pip install -r requirements.txt
```

### Acceptance Criteria
- [ ] Dependencies added to requirements.txt
- [ ] All dependencies install without conflicts
- [ ] No version conflicts with existing packages

---

## Subtask 1.4: Create Base Classes

**Estimated Time**: 2 hours

### Description
Create base classes for agents and adapters that establish patterns for the integration.

### File: `packages/core/ai_content_platform/vimax/agents/base.py`

```python
"""
Base classes for ViMax agents.

All agents inherit from BaseAgent and implement the process() method.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel
import logging

T = TypeVar('T')  # Input type
R = TypeVar('R')  # Result type


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    name: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_retries: int = 3
    timeout: float = 60.0
    extra: Dict[str, Any] = {}


class AgentResult(BaseModel, Generic[R]):
    """Result from an agent execution."""

    success: bool
    result: Optional[R] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

    @classmethod
    def ok(cls, result: R, **metadata) -> "AgentResult[R]":
        return cls(success=True, result=result, metadata=metadata)

    @classmethod
    def fail(cls, error: str, **metadata) -> "AgentResult[R]":
        return cls(success=False, error=error, metadata=metadata)


class BaseAgent(ABC, Generic[T, R]):
    """
    Base class for all ViMax agents.

    Agents are responsible for specific tasks in the pipeline:
    - CharacterExtractor: Extract characters from text
    - Screenwriter: Generate screenplay from idea
    - StoryboardArtist: Create visual storyboard
    - etc.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig(name=self.__class__.__name__)
        self.logger = logging.getLogger(f"vimax.agents.{self.config.name}")

    @abstractmethod
    async def process(self, input_data: T) -> AgentResult[R]:
        """
        Process input data and return result.

        Args:
            input_data: Input data specific to this agent

        Returns:
            AgentResult containing the processed output or error
        """
        pass

    def validate_input(self, input_data: T) -> bool:
        """Validate input data before processing. Override if needed."""
        return input_data is not None

    async def __call__(self, input_data: T) -> AgentResult[R]:
        """Convenience method to call process()."""
        if not self.validate_input(input_data):
            return AgentResult.fail("Invalid input data")
        return await self.process(input_data)
```

### File: `packages/core/ai_content_platform/vimax/adapters/base.py`

```python
"""
Base classes for ViMax adapters.

Adapters bridge ViMax agents to the underlying generators/services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel
import logging

T = TypeVar('T')  # Input type
R = TypeVar('R')  # Result type


class AdapterConfig(BaseModel):
    """Configuration for an adapter."""

    provider: str = "fal"  # fal, replicate, google, openrouter
    model: str = ""
    timeout: float = 120.0
    max_retries: int = 3
    extra: Dict[str, Any] = {}


class BaseAdapter(ABC, Generic[T, R]):
    """
    Base class for all ViMax adapters.

    Adapters translate between ViMax agent interfaces and
    underlying service APIs (FAL, Replicate, OpenRouter, etc.)
    """

    def __init__(self, config: Optional[AdapterConfig] = None):
        self.config = config or AdapterConfig()
        self.logger = logging.getLogger(f"vimax.adapters.{self.__class__.__name__}")
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the adapter (connect to services, etc.)."""
        pass

    @abstractmethod
    async def execute(self, input_data: T) -> R:
        """Execute the adapter's main function."""
        pass

    async def ensure_initialized(self):
        """Ensure adapter is initialized before use."""
        if not self._initialized:
            self._initialized = await self.initialize()
            if not self._initialized:
                raise RuntimeError(f"Failed to initialize {self.__class__.__name__}")

    async def __call__(self, input_data: T) -> R:
        """Convenience method to execute."""
        await self.ensure_initialized()
        return await self.execute(input_data)
```

### File: `packages/core/ai_content_platform/vimax/agents/__init__.py`

```python
"""
ViMax Agents

LLM-powered agents for content generation pipeline.
"""

from .base import BaseAgent, AgentConfig, AgentResult

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "AgentResult",
]
```

### File: `packages/core/ai_content_platform/vimax/adapters/__init__.py`

```python
"""
ViMax Adapters

Bridges between agents and underlying services.
"""

from .base import BaseAdapter, AdapterConfig

__all__ = [
    "BaseAdapter",
    "AdapterConfig",
]
```

### Acceptance Criteria
- [ ] Base classes created with proper abstractions
- [ ] Type hints complete
- [ ] Logging configured
- [ ] All imports work

---

## Subtask 1.5: Create Test Structure

**Estimated Time**: 1 hour

### Description
Set up the test directory structure and base test fixtures.

### Files to Create

```
tests/unit/vimax/
├── __init__.py
├── conftest.py
├── test_interfaces.py
└── test_base_classes.py
```

### File: `tests/unit/vimax/conftest.py`

```python
"""
Pytest fixtures for ViMax tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        "choices": [{
            "message": {
                "content": "Test response"
            }
        }]
    }


@pytest.fixture
def mock_image_generator():
    """Mock image generator."""
    mock = AsyncMock()
    mock.generate.return_value = {
        "image_path": "/tmp/test_image.png",
        "width": 1024,
        "height": 1024,
    }
    return mock


@pytest.fixture
def mock_video_generator():
    """Mock video generator."""
    mock = AsyncMock()
    mock.generate.return_value = {
        "video_path": "/tmp/test_video.mp4",
        "duration": 5.0,
    }
    return mock


@pytest.fixture
def sample_character_data():
    """Sample character data for testing."""
    return {
        "name": "John",
        "description": "A young warrior",
        "age": "25",
        "gender": "male",
        "appearance": "Tall with dark hair",
        "personality": "Brave and determined",
    }


@pytest.fixture
def sample_shot_data():
    """Sample shot data for testing."""
    return {
        "shot_id": "shot_001",
        "shot_type": "medium",
        "description": "Hero standing at crossroads",
        "duration_seconds": 5.0,
    }
```

### File: `tests/unit/vimax/test_interfaces.py`

```python
"""
Tests for ViMax interface models.
"""

import pytest
from ai_content_platform.vimax.interfaces import (
    CharacterInNovel,
    CharacterInScene,
    CharacterPortrait,
    ShotDescription,
    ShotType,
    Scene,
    Storyboard,
    ImageOutput,
    VideoOutput,
    PipelineOutput,
)


class TestCharacterModels:
    """Tests for character models."""

    def test_character_in_novel_creation(self, sample_character_data):
        """Test CharacterInNovel creation."""
        char = CharacterInNovel(**sample_character_data)
        assert char.name == "John"
        assert char.age == "25"

    def test_character_in_novel_defaults(self):
        """Test CharacterInNovel with minimal data."""
        char = CharacterInNovel(name="Test")
        assert char.name == "Test"
        assert char.description == ""
        assert char.relationships == []

    def test_character_portrait_views(self):
        """Test CharacterPortrait views property."""
        portrait = CharacterPortrait(
            character_name="John",
            front_view="/path/front.png",
            side_view="/path/side.png",
        )
        views = portrait.views
        assert "front" in views
        assert "side" in views
        assert "back" not in views


class TestShotModels:
    """Tests for shot models."""

    def test_shot_description_creation(self, sample_shot_data):
        """Test ShotDescription creation."""
        shot = ShotDescription(**sample_shot_data)
        assert shot.shot_id == "shot_001"
        assert shot.shot_type == ShotType.MEDIUM

    def test_shot_type_enum(self):
        """Test ShotType enum values."""
        assert ShotType.WIDE.value == "wide"
        assert ShotType.CLOSE_UP.value == "close_up"

    def test_scene_properties(self):
        """Test Scene properties."""
        scene = Scene(
            scene_id="scene_001",
            title="Opening",
            shots=[
                ShotDescription(shot_id="s1", description="Shot 1", duration_seconds=5),
                ShotDescription(shot_id="s2", description="Shot 2", duration_seconds=3),
            ]
        )
        assert scene.shot_count == 2
        assert scene.total_duration == 8.0


class TestOutputModels:
    """Tests for output models."""

    def test_image_output(self):
        """Test ImageOutput creation."""
        output = ImageOutput(
            image_path="/tmp/test.png",
            prompt="Test prompt",
            model="flux_dev",
            cost=0.003,
        )
        assert output.cost == 0.003

    def test_pipeline_output_success(self):
        """Test PipelineOutput success property."""
        output = PipelineOutput(
            pipeline_name="test",
            final_video=VideoOutput(video_path="/tmp/test.mp4"),
        )
        assert output.success is True

    def test_pipeline_output_failure(self):
        """Test PipelineOutput failure."""
        output = PipelineOutput(
            pipeline_name="test",
            errors=["Something went wrong"],
        )
        assert output.success is False
```

### File: `tests/unit/vimax/test_base_classes.py`

```python
"""
Tests for ViMax base classes.
"""

import pytest
from ai_content_platform.vimax.agents.base import (
    BaseAgent,
    AgentConfig,
    AgentResult,
)
from ai_content_platform.vimax.adapters.base import (
    BaseAdapter,
    AdapterConfig,
)


class TestAgentResult:
    """Tests for AgentResult."""

    def test_ok_result(self):
        """Test successful result."""
        result = AgentResult.ok("test_data", elapsed=1.5)
        assert result.success is True
        assert result.result == "test_data"
        assert result.metadata["elapsed"] == 1.5

    def test_fail_result(self):
        """Test failed result."""
        result = AgentResult.fail("error message")
        assert result.success is False
        assert result.error == "error message"
        assert result.result is None


class TestAgentConfig:
    """Tests for AgentConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = AgentConfig(name="test_agent")
        assert config.name == "test_agent"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7

    def test_custom_config(self):
        """Test custom configuration."""
        config = AgentConfig(
            name="test",
            model="claude-3",
            temperature=0.5,
            max_retries=5,
        )
        assert config.model == "claude-3"
        assert config.max_retries == 5


class TestAdapterConfig:
    """Tests for AdapterConfig."""

    def test_default_adapter_config(self):
        """Test default adapter config."""
        config = AdapterConfig()
        assert config.provider == "fal"
        assert config.timeout == 120.0
```

### Acceptance Criteria
- [ ] Test directory structure created
- [ ] Fixtures defined in conftest.py
- [ ] Basic tests for interfaces pass
- [ ] Basic tests for base classes pass

---

## Phase 1 Completion Checklist

- [ ] **1.1** Directory structure created
- [ ] **1.2** Interface models implemented
- [ ] **1.3** Dependencies added and installed
- [ ] **1.4** Base classes created
- [ ] **1.5** Test structure set up

### Verification Commands

```bash
# Verify package imports
python -c "from ai_content_platform.vimax.interfaces import *; print('Interfaces OK')"
python -c "from ai_content_platform.vimax.agents import *; print('Agents OK')"
python -c "from ai_content_platform.vimax.adapters import *; print('Adapters OK')"

# Run tests
pytest tests/unit/vimax/ -v

# Check dependencies
pip check
```

---

*Next Phase*: [PHASE_2_ADAPTERS.md](./PHASE_2_ADAPTERS.md)
