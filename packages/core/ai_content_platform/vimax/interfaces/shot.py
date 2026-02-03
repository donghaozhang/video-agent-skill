"""
Shot and scene data models for ViMax pipeline.
"""

from typing import Optional, List, Dict
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

    # Reference images for character consistency
    character_references: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of character name to reference image path"
    )
    primary_reference_image: Optional[str] = Field(
        default=None,
        description="Primary reference image path for this shot (used for IP-Adapter)"
    )


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
