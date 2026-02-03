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
