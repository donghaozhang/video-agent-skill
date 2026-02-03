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
    CharacterPortraitRegistry,
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
    "CharacterPortraitRegistry",
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
