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
