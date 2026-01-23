"""
Content creation chain classes for AI Content Pipeline
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum


class StepType(Enum):
    """Enumeration of supported pipeline step types."""
    TEXT_TO_IMAGE = "text_to_image"
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_UNDERSTANDING = "image_understanding"
    PROMPT_GENERATION = "prompt_generation"
    IMAGE_TO_IMAGE = "image_to_image"
    IMAGE_TO_VIDEO = "image_to_video"
    TEXT_TO_SPEECH = "text_to_speech"
    ADD_AUDIO = "add_audio"
    UPSCALE_VIDEO = "upscale_video"
    UPSCALE_IMAGE = "upscale_image"
    SPLIT_IMAGE = "split_image"
    GENERATE_SUBTITLES = "generate_subtitles"
    PARALLEL_GROUP = "parallel_group"
    REPLICATE_MULTITALK = "replicate_multitalk"


@dataclass
class PipelineStep:
    """Configuration for a single pipeline step."""
    step_type: StepType
    model: str
    params: Dict[str, Any]
    enabled: bool = True
    retry_count: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineStep':
        """Create PipelineStep from dictionary configuration."""
        return cls(
            step_type=StepType(data["type"]),
            model=data["model"],
            params=data.get("params", {}),
            enabled=data.get("enabled", True),
            retry_count=data.get("retry_count", 0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PipelineStep to dictionary."""
        return {
            "type": self.step_type.value,
            "model": self.model,
            "params": self.params,
            "enabled": self.enabled,
            "retry_count": self.retry_count
        }


@dataclass
class ChainResult:
    """Result of executing a content creation chain."""
    success: bool
    steps_completed: int
    total_steps: int
    total_cost: float
    total_time: float
    outputs: Dict[str, Any]
    error: Optional[str] = None
    step_results: Optional[List[Dict[str, Any]]] = None


class ContentCreationChain:
    """
    Represents a chain of content creation steps.
    
    Manages the configuration and execution flow for creating content
    through multiple AI models in sequence.
    """
    
    def __init__(self, name: str, steps: List[PipelineStep], config: Dict[str, Any] = None):
        """
        Initialize content creation chain.
        
        Args:
            name: Human-readable name for the chain
            steps: List of pipeline steps to execute
            config: Additional configuration options
        """
        self.name = name
        self.steps = steps
        self.config = config or {}
        
        # Default configuration
        self.output_dir = self.config.get("output_dir", "output")
        self.temp_dir = self.config.get("temp_dir", "temp") 
        self.cleanup_temp = self.config.get("cleanup_temp", True)
        self.save_intermediates = self.config.get("save_intermediates", False)
        
        # Pipeline input type - can be "text", "image", "video", or "auto"
        self.input_type = self.config.get("input_type", "auto")
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'ContentCreationChain':
        """Create chain from configuration dictionary."""
        name = config.get("name", "unnamed_chain")
        steps = [PipelineStep.from_dict(step_data) for step_data in config["steps"]]
        chain_config = {k: v for k, v in config.items() if k not in ["name", "steps"]}
        
        return cls(name, steps, chain_config)
    
    def to_config(self) -> Dict[str, Any]:
        """Convert chain to configuration dictionary."""
        return {
            "name": self.name,
            "steps": [step.to_dict() for step in self.steps],
            **self.config
        }
    
    def validate(self) -> List[str]:
        """
        Validate the chain configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.steps:
            errors.append("Chain must have at least one step")
            return errors
        
        # Determine initial input type
        initial_input_type = self._determine_initial_input_type()
        
        # Track the actual current data type (for PROMPT_GENERATION pass-through)
        actual_data_type = initial_input_type
        
        for i, step in enumerate(self.steps):
            step_input = self._get_step_input_type(step.step_type)
            step_output = self._get_step_output_type(step.step_type)
            
            if i == 0:
                # First step must accept the initial input type
                if step_input != initial_input_type and step_input != "any":
                    errors.append(f"First step expects {step_input} input, but pipeline starts with {initial_input_type}")
            else:
                # Check if this step can accept the actual data type available
                if step_input != actual_data_type and step_input != "any":
                    errors.append(
                        f"Step {i+1} expects {step_input} but available data is {actual_data_type}"
                    )
            
            # PROMPT_GENERATION is special - it doesn't change the actual data type
            # It just adds metadata (the generated prompt) to the context
            if step.step_type == StepType.PROMPT_GENERATION:
                # Keep the actual_data_type unchanged
                pass
            else:
                # Normal steps change the data type
                actual_data_type = step_output
        
        return errors
    
    def _determine_initial_input_type(self) -> str:
        """
        Determine the initial input type for the pipeline.
        
        Returns:
            Initial input type ("text", "image", "video")
        """
        if self.input_type == "auto":
            # Auto-detect based on the first step
            if not self.steps:
                return "text"  # Default fallback
            
            first_step_input = self._get_step_input_type(self.steps[0].step_type)
            return first_step_input
        else:
            # Use explicitly configured input type
            return self.input_type
    
    def _get_step_input_type(self, step_type: StepType) -> str:
        """Get the input type for a step."""
        input_types = {
            StepType.TEXT_TO_IMAGE: "text",
            StepType.TEXT_TO_VIDEO: "text",
            StepType.IMAGE_UNDERSTANDING: "image",
            StepType.PROMPT_GENERATION: "image",
            StepType.IMAGE_TO_IMAGE: "image",
            StepType.IMAGE_TO_VIDEO: "image",
            StepType.TEXT_TO_SPEECH: "text",
            StepType.ADD_AUDIO: "video",
            StepType.UPSCALE_VIDEO: "video",
            StepType.UPSCALE_IMAGE: "image",
            StepType.SPLIT_IMAGE: "image",
            StepType.GENERATE_SUBTITLES: "video",
            StepType.PARALLEL_GROUP: "any"
        }
        return input_types.get(step_type, "unknown")
    
    def _get_step_output_type(self, step_type: StepType) -> str:
        """Get the output type for a step."""
        output_types = {
            StepType.TEXT_TO_IMAGE: "image",
            StepType.TEXT_TO_VIDEO: "video",
            StepType.IMAGE_UNDERSTANDING: "text",
            StepType.PROMPT_GENERATION: "text",
            StepType.IMAGE_TO_IMAGE: "image",
            StepType.IMAGE_TO_VIDEO: "video",
            StepType.TEXT_TO_SPEECH: "audio",
            StepType.ADD_AUDIO: "video",
            StepType.UPSCALE_VIDEO: "video",
            StepType.UPSCALE_IMAGE: "image",
            StepType.SPLIT_IMAGE: "images",  # Multiple images output
            StepType.GENERATE_SUBTITLES: "video",
            StepType.PARALLEL_GROUP: "parallel_result"
        }
        return output_types.get(step_type, "unknown")
    
    def estimate_cost(self) -> float:
        """Estimate total cost for executing the chain."""
        from ..config.constants import COST_ESTIMATES
        
        total_cost = 0.0
        
        for step in self.steps:
            if not step.enabled:
                continue
                
            step_costs = COST_ESTIMATES.get(step.step_type.value, {})
            step_cost = step_costs.get(step.model, 0.0)
            total_cost += step_cost
        
        return total_cost
    
    def estimate_time(self) -> float:
        """Estimate total processing time for the chain."""
        from ..config.constants import PROCESSING_TIME_ESTIMATES
        
        total_time = 0.0
        
        for step in self.steps:
            if not step.enabled:
                continue
                
            step_times = PROCESSING_TIME_ESTIMATES.get(step.step_type.value, {})
            step_time = step_times.get(step.model, 60.0)  # Default 60 seconds
            total_time += step_time
        
        return total_time
    
    def get_enabled_steps(self) -> List[PipelineStep]:
        """Get list of enabled steps."""
        return [step for step in self.steps if step.enabled]
    
    def get_initial_input_type(self) -> str:
        """Get the expected initial input type for this chain."""
        return self._determine_initial_input_type()
    
    def __repr__(self) -> str:
        """String representation of the chain."""
        enabled_count = len(self.get_enabled_steps())
        return f"ContentCreationChain(name='{self.name}', steps={enabled_count}/{len(self.steps)})"