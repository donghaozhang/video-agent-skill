"""Core data models for the AI Content Platform."""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class StepType(str, Enum):
    """Available step types in the pipeline."""
    TEXT_TO_SPEECH = "text_to_speech"
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_IMAGE = "image_to_image"
    TEXT_TO_VIDEO = "text_to_video"
    VIDEO_GENERATION = "video_generation"
    VIDEO_TO_VIDEO = "video_to_video"
    AVATAR_GENERATION = "avatar_generation"
    PARALLEL_GROUP = "parallel_group"
    IMAGE_UNDERSTANDING = "image_understanding"
    PROMPT_GENERATION = "prompt_generation"


class MergeStrategy(str, Enum):
    """Merge strategies for parallel execution."""
    COLLECT_ALL = "collect_all"
    FIRST_SUCCESS = "first_success"
    BEST_QUALITY = "best_quality"


class StepConfig(BaseModel):
    """Configuration for a single pipeline step."""
    step_type: StepType
    config: Dict[str, Any] = Field(default_factory=dict)
    output_filename: Optional[str] = None
    enabled: bool = True
    timeout: Optional[int] = None
    retry_count: int = 0


class ParallelConfig(BaseModel):
    """Configuration for parallel execution."""
    merge_strategy: MergeStrategy = MergeStrategy.COLLECT_ALL
    max_workers: Optional[int] = None
    timeout: Optional[int] = None


class ParallelStepConfig(BaseModel):
    """Configuration for parallel step group."""
    step_type: StepType = StepType.PARALLEL_GROUP
    parallel_config: ParallelConfig
    steps: List[StepConfig]
    output_directory: Optional[str] = None


class PipelineConfig(BaseModel):
    """Main pipeline configuration."""
    pipeline_name: str
    description: Optional[str] = None
    output_directory: str = "output"
    steps: List[Union[StepConfig, ParallelStepConfig]]
    global_config: Dict[str, Any] = Field(default_factory=dict)


class StepResult(BaseModel):
    """Result of a pipeline step execution."""
    step_id: str
    step_type: StepType
    success: bool
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    cost: Optional[float] = None


class PipelineResult(BaseModel):
    """Result of pipeline execution."""
    pipeline_name: str
    success: bool
    total_steps: int
    successful_steps: int
    failed_steps: int
    total_execution_time: float
    total_cost: float = 0.0
    step_results: List[StepResult]
    output_directory: str