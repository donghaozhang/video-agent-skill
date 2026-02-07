"""
Main pipeline manager for AI Content Pipeline

Orchestrates the execution of content creation chains with multiple AI models.
"""

import os
import time
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .chain import ContentCreationChain, ChainResult, PipelineStep, StepType
from .executor import ChainExecutor
from ..models.text_to_image import UnifiedTextToImageGenerator
from ..models.image_understanding import UnifiedImageUnderstandingGenerator
from ..models.prompt_generation import UnifiedPromptGenerator
from ..models.image_to_image import UnifiedImageToImageGenerator
from ..utils.file_manager import FileManager
from ..config.constants import SUPPORTED_MODELS, DEFAULT_CHAIN_CONFIG


class AIPipelineManager:
    """
    Main manager for AI content creation pipelines.
    
    Handles chain creation, execution, cost estimation, and result management.
    """
    
    def __init__(self, base_dir: str = None, quiet: bool = False):
        """
        Initialize the pipeline manager.

        Args:
            base_dir: Base directory for pipeline operations
            quiet: Suppress informational output
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.output_dir = self.base_dir / "output"
        self.temp_dir = self.output_dir / "temp"
        self.quiet = quiet

        # Initialize components
        self.file_manager = FileManager(self.base_dir)
        self.executor = ChainExecutor(self.file_manager, quiet=quiet)

        # Initialize model generators
        self.text_to_image = UnifiedTextToImageGenerator()
        self.image_understanding = UnifiedImageUnderstandingGenerator()
        self.prompt_generation = UnifiedPromptGenerator()
        self.image_to_image = UnifiedImageToImageGenerator()

        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)

        if not quiet:
            print(f"✅ AI Pipeline Manager initialized (base: {self.base_dir})")
    
    def create_chain_from_config(self, config_path: str) -> ContentCreationChain:
        """
        Create a content creation chain from configuration file.
        
        Args:
            config_path: Path to YAML or JSON configuration file
            
        Returns:
            ContentCreationChain instance
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Load configuration
        with open(config_file, 'r') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                config = yaml.safe_load(f)
            elif config_file.suffix.lower() == '.json':
                config = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration format: {config_file.suffix}")
        
        return ContentCreationChain.from_config(config)
    
    def create_simple_chain(
        self,
        steps: List[str],
        models: Dict[str, str] = None,
        name: str = "simple_chain"
    ) -> ContentCreationChain:
        """
        Create a simple chain with basic configuration.
        
        Args:
            steps: List of step types (e.g., ["text_to_image", "image_to_video"])
            models: Optional model selection for each step
            name: Name for the chain
            
        Returns:
            ContentCreationChain instance
        """
        models = models or {}
        pipeline_steps = []
        
        for step_type in steps:
            if step_type not in [s.value for s in StepType]:
                raise ValueError(f"Unsupported step type: {step_type}")
            
            # Get default model for step type
            available_models = SUPPORTED_MODELS.get(step_type, [])
            if not available_models:
                raise ValueError(f"No models available for step type: {step_type}")
            
            model = models.get(step_type, available_models[0])
            
            pipeline_steps.append(PipelineStep(
                step_type=StepType(step_type),
                model=model,
                params={}
            ))
        
        return ContentCreationChain(name, pipeline_steps)
    
    def execute_chain(
        self,
        chain: ContentCreationChain,
        input_data: str,
        **kwargs
    ) -> ChainResult:
        """
        Execute a content creation chain.
        
        Args:
            chain: ContentCreationChain to execute
            input_data: Initial input data (text, image path, or video path)
            **kwargs: Additional execution parameters
            
        Returns:
            ChainResult with execution results
        """
        # Validate chain
        errors = chain.validate()
        if errors:
            return ChainResult(
                success=False,
                steps_completed=0,
                total_steps=len(chain.steps),
                total_cost=0.0,
                total_time=0.0,
                outputs={},
                error=f"Chain validation failed: {'; '.join(errors)}"
            )
        
        if not self.quiet:
            print(f"🚀 Executing chain: {chain.name}")
            print(f"📝 Input ({chain.get_initial_input_type()}): {input_data[:100]}{'...' if len(input_data) > 100 else ''}")
        
        # Execute chain
        try:
            return self.executor.execute(chain, input_data, **kwargs)
        except Exception as e:
            return ChainResult(
                success=False,
                steps_completed=0,
                total_steps=len(chain.steps),
                total_cost=0.0,
                total_time=0.0,
                outputs={},
                error=f"Execution failed: {str(e)}"
            )
    
    def quick_create_video(
        self,
        text: str,
        image_model: str = "auto",
        video_model: str = "auto",
        output_dir: str = None
    ) -> ChainResult:
        """
        Quick method to create video from text using recommended models.
        
        Args:
            text: Text prompt for content creation
            image_model: Model for text-to-image ("auto" for smart selection)
            video_model: Model for image-to-video ("auto" for smart selection)
            output_dir: Custom output directory
            
        Returns:
            ChainResult with creation results
        """
        # Create simple text-to-video chain
        chain = self.create_simple_chain(
            steps=["text_to_image", "image_to_video"],
            models={
                "text_to_image": image_model,
                "image_to_video": video_model
            },
            name="quick_video_creation"
        )
        
        # Execute with custom output directory
        kwargs = {}
        if output_dir:
            kwargs["output_dir"] = output_dir
        
        return self.execute_chain(chain, text, **kwargs)
    
    def estimate_chain_cost(self, chain: ContentCreationChain) -> Dict[str, Any]:
        """
        Get detailed cost estimation for a chain.
        
        Args:
            chain: ContentCreationChain to estimate
            
        Returns:
            Dictionary with cost breakdown
        """
        total_cost = 0.0
        step_costs = []
        
        for step in chain.get_enabled_steps():
            cost = self._estimate_step_cost(step)
            total_cost += cost
            
            step_costs.append({
                "step": step.step_type.value,
                "model": step.model,
                "cost": cost
            })
        
        return {
            "total_cost": total_cost,
            "step_costs": step_costs,
            "currency": "USD"
        }
    
    def _estimate_step_cost(self, step: PipelineStep) -> float:
        """Estimate cost for a single step."""
        if step.step_type == StepType.TEXT_TO_IMAGE:
            return self.text_to_image.estimate_cost(step.model)
        # TODO: Add other step types when implemented
        return 0.0
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get all available models by step type."""
        available = {}
        
        # Text-to-image models
        available["text_to_image"] = self.text_to_image.get_available_models()
        
        # Image understanding models
        available["image_understanding"] = self.image_understanding.get_available_models()
        
        # Prompt generation models
        available["prompt_generation"] = self.prompt_generation.get_available_models()
        
        # Image-to-image models
        available["image_to_image"] = self.image_to_image.get_available_models()
        
        # TODO: Add other model types when implemented
        available["image_to_video"] = SUPPORTED_MODELS.get("image_to_video", [])
        available["add_audio"] = SUPPORTED_MODELS.get("add_audio", [])
        available["upscale_video"] = SUPPORTED_MODELS.get("upscale_video", [])
        
        return available
    
    def create_example_configs(self, output_dir: str = None):
        """
        Create example configuration files.
        
        Args:
            output_dir: Directory to create example configs
        """
        output_path = Path(output_dir) if output_dir else self.base_dir / "examples"
        output_path.mkdir(exist_ok=True)
        
        # Simple text-to-image chain
        simple_config = {
            "name": "simple_text_to_image",
            "steps": [
                {
                    "type": "text_to_image",
                    "model": "flux_dev",
                    "params": {
                        "aspect_ratio": "16:9",
                        "style": "cinematic"
                    }
                }
            ],
            "output_dir": "output",
            "cleanup_temp": True
        }
        
        # Full content creation chain
        full_config = {
            "name": "full_content_creation",
            "steps": [
                {
                    "type": "text_to_image",
                    "model": "flux_dev",
                    "params": {
                        "aspect_ratio": "16:9",
                        "style": "cinematic"
                    }
                },
                {
                    "type": "image_to_video",
                    "model": "veo3",
                    "params": {
                        "duration": 8,
                        "motion_level": "medium"
                    }
                },
                {
                    "type": "add_audio",
                    "model": "thinksound",
                    "params": {
                        "prompt": "epic cinematic soundtrack"
                    }
                }
            ],
            "output_dir": "output",
            "temp_dir": "temp",
            "cleanup_temp": True,
            "save_intermediates": False
        }
        
        # Save example configs
        with open(output_path / "simple_chain.yaml", 'w') as f:
            yaml.dump(simple_config, f, default_flow_style=False, indent=2)
        
        with open(output_path / "full_chain.yaml", 'w') as f:
            yaml.dump(full_config, f, default_flow_style=False, indent=2)
        
        if not self.quiet:
            print(f"📄 Example configurations created in: {output_path}")
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        self.file_manager.cleanup_temp_files()
    
    def __repr__(self) -> str:
        """String representation of the manager."""
        available_models = self.get_available_models()
        total_models = sum(len(models) for models in available_models.values())
        return f"AIPipelineManager(base_dir='{self.base_dir}', models={total_models})"