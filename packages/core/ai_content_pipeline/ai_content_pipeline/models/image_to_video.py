"""
Unified Image-to-Video Generator for AI Content Pipeline

Integrates multiple image-to-video models with smart selection and cost optimization.
"""

import os
import time
from typing import Dict, Any, Optional, List

from .base import BaseContentModel, ModelResult
from ..config.constants import SUPPORTED_MODELS, COST_ESTIMATES, MODEL_RECOMMENDATIONS


class MockImageToVideoGenerator:
    """Mock image-to-video generator for testing without API keys."""

    def generate_video(self, prompt: str, image_url: str, model: str = "hailuo", **kwargs):
        """Mock generate_video method."""
        return self._mock_result(prompt, model)

    def generate_video_from_local_image(self, prompt: str, image_path: str, model: str = "hailuo", **kwargs):
        """Mock generate_video_from_local_image method."""
        return self._mock_result(prompt, model)

    def _mock_result(self, prompt: str, model: str):
        """Create mock result."""
        return {
            'success': True,
            'video': {'url': f'mock://generated-video-{int(time.time())}.mp4'},
            'local_path': f'/tmp/mock_video_{int(time.time())}.mp4',
            'model': model,
            'cost_estimate': 0.05,
            'processing_time': 5.0,
            'prompt': prompt,
            'mock_mode': True
        }

    def generate_video_from_image(self, prompt: str, image_url: str, **kwargs):
        """Mock video generation that returns fake results."""
        import time
        return {
            'success': True,
            'video_url': f'mock://generated-video-{int(time.time())}.mp4',
            'video_path': f'/tmp/mock_video_{int(time.time())}.mp4',
            'model_used': kwargs.get('model', 'mock_model'),
            'provider': 'fal_mock',
            'cost_estimate': 0.05,
            'processing_time': 5.0,
            'prompt': prompt,
            'mock_mode': True
        }


class UnifiedImageToVideoGenerator(BaseContentModel):
    """
    Unified interface for multiple image-to-video models.
    
    Supports FAL AI models (MiniMax Hailuo-02, Kling Video 2.1) with plans for
    Google Veo integration.
    """
    
    def __init__(self):
        super().__init__("image_to_video")
        self._fal_generator = None
        self._initialize_generators()
    
    def _initialize_generators(self):
        """Initialize available image-to-video generators."""
        try:
            # Try to import the new FAL image-to-video generator package
            from fal_image_to_video import FALImageToVideoGenerator
            self._fal_generator = FALImageToVideoGenerator()
            print("✅ FAL Image-to-Video generator initialized")
        except ImportError as e:
            print(f"⚠️  FAL Image-to-Video generator not available: {e}")
            # Check if we should use mock mode
            import os
            if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS') or not os.environ.get('FAL_KEY'):
                print("⚠️  Initializing mock FAL Image-to-Video generator")
                self._fal_generator = MockImageToVideoGenerator()
        except Exception as e:
            print(f"⚠️  FAL Image-to-Video initialization failed: {e}")
            import os
            if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS') or not os.environ.get('FAL_KEY'):
                print("⚠️  Initializing mock FAL Image-to-Video generator")
                self._fal_generator = MockImageToVideoGenerator()
    
    def generate(self, input_data: Dict[str, Any], model: str = "auto", **kwargs) -> ModelResult:
        """
        Generate video from image using specified model.
        
        Args:
            input_data: Dictionary containing:
                - image_path: Path to input image
                - image_url: URL of input image (alternative to image_path)
                - prompt: Text prompt for video generation
            model: Model to use ("auto" for smart selection)
            **kwargs: Additional generation parameters
            
        Returns:
            ModelResult with generation results
        """
        # Use local variable for thread-safe timing (not self.start_time)
        start_time = time.time()

        try:
            # Validate input
            if not self.validate_input(input_data, model, **kwargs):
                return self._create_error_result(model, "Invalid input parameters", start_time)
            
            # Extract required parameters
            prompt = input_data.get("prompt", "")
            image_url = input_data.get("image_url")
            image_path = input_data.get("image_path")
            output_filename = input_data.get("output_filename")

            # Pass output_filename through kwargs if provided
            if output_filename:
                kwargs["output_filename"] = output_filename
            
            # Convert local image path to URL if needed
            if image_path and not image_url:
                # If it's a local path, convert it to a file URL or upload it
                if image_path.startswith("http"):
                    image_url = image_path
                else:
                    # For local files, we'll pass the path directly to the FAL generator
                    # which should handle local file uploads
                    image_url = image_path
            
            if not image_url and not image_path:
                return self._create_error_result(model, "No image URL or path provided", start_time)
            
            # Auto-select model if needed
            if model == "auto":
                budget = kwargs.get("budget")
                criteria = kwargs.get("criteria", "balanced")
                model = self.recommend_model(criteria, budget)
                print(f"🤖 Auto-selected model: {model}")
            
            # Route to appropriate generator
            # FAL models include all models supported by the FAL generator
            fal_models = [
                "hailuo", "kling", "kling_2_1", "kling_2_6_pro",
                "kling_3_standard", "kling_3_pro",
                "seedance_1_5_pro", "sora_2", "sora_2_pro",
                "veo_3_1_fast", "wan_2_6"
            ]
            if model in fal_models:
                return self._generate_with_fal(prompt, image_url, model, start_time, **kwargs)
            elif model in ["veo3", "veo3_fast", "veo2"]:
                return self._generate_with_veo(prompt, image_url, model, start_time, **kwargs)
            else:
                return self._create_error_result(model, f"Unsupported model: {model}", start_time)

        except Exception as e:
            return self._create_error_result(model, f"Generation failed: {e!s}", start_time)
    
    def _generate_with_fal(self, prompt: str, image_url: str, model: str, start_time: float, **kwargs) -> ModelResult:
        """Generate video using FAL AI models."""
        if not self._fal_generator:
            return self._create_error_result(model, "FAL generator not available", start_time)

        try:
            # Map old model names to new FAL model keys if needed
            fal_model_map = {
                "kling": "kling_2_1",  # Map old name to new
            }
            fal_model = fal_model_map.get(model, model)  # Use model key directly

            # Extract FAL-specific parameters
            output_folder = kwargs.get("output_dir", "output")

            # Get duration from kwargs, let the model handle defaults
            duration = kwargs.get("duration")

            # Filter kwargs to pass model-specific params
            excluded_keys = ["output_dir", "budget", "criteria"]
            model_kwargs = {k: v for k, v in kwargs.items() if k not in excluded_keys}

            # Generate video - use local image method if we have a local path
            if image_url and not image_url.startswith("http"):
                # Local file path - use the local image method
                result = self._fal_generator.generate_video_from_local_image(
                    prompt=prompt,
                    image_path=image_url,  # This is actually a local path
                    model=fal_model,
                    output_dir=output_folder,
                    **model_kwargs
                )
            else:
                # Remote URL - use the URL method
                result = self._fal_generator.generate_video(
                    prompt=prompt,
                    image_url=image_url,
                    model=fal_model,
                    output_dir=output_folder,
                    **model_kwargs
                )
            
            if result and 'video' in result:
                return self._create_success_result(
                    model=model,
                    output_path=result.get("local_path"),
                    output_url=result.get("video", {}).get("url"),
                    start_time=start_time,
                    metadata={
                        "prompt": prompt,
                        "image_url": image_url,
                        "duration": duration,
                        "task_id": result.get("task_id"),
                        "file_size": result.get("video", {}).get("file_size"),
                        "custom_filename": result.get("custom_filename"),
                        "fal_response": result
                    }
                )
            else:
                error_msg = "FAL generation failed" if result else "No result returned"
                return self._create_error_result(model, error_msg, start_time)

        except Exception as e:
            return self._create_error_result(model, f"FAL generation error: {e!s}", start_time)
    
    def _generate_with_veo(self, prompt: str, image_url: str, model: str, start_time: float, **kwargs) -> ModelResult:
        """Generate video using Google Veo (planned)."""
        return self._create_error_result(model, "Google Veo integration not yet implemented", start_time)
    
    def get_available_models(self) -> List[str]:
        """Get list of available image-to-video models."""
        available = []
        
        # Check FAL models
        if self._fal_generator:
            available.extend(["hailuo", "kling"])
        
        # TODO: Check Veo models when implemented
        
        return available
    
    def estimate_cost(self, model: str, **kwargs) -> float:
        """Estimate cost for video generation."""
        costs = COST_ESTIMATES.get("image_to_video", {})
        return costs.get(model, 0.0)
    
    def validate_input(self, input_data: Any, model: str, **kwargs) -> bool:
        """Validate input parameters."""
        if not isinstance(input_data, dict):
            return False
        
        # Check for required fields
        prompt = input_data.get("prompt", "")
        image_url = input_data.get("image_url")
        image_path = input_data.get("image_path")
        
        if not isinstance(prompt, str) or len(prompt.strip()) == 0:
            return False
        
        if not image_url and not image_path:
            return False
        
        if model != "auto" and model not in SUPPORTED_MODELS.get("image_to_video", []):
            return False

        # Duration validation is handled by model-specific validators
        # Different models support different duration formats (e.g., "8s", 5, "10")

        return True
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a specific model."""
        model_info = {
            "hailuo": {
                "name": "MiniMax Hailuo-02",
                "provider": "FAL AI",
                "description": "768p resolution, 6-10 second videos",
                "best_for": "Cost-effective, quick generation",
                "cost_per_video": "$0.08",
                "avg_time": "30-60 seconds",
                "max_duration": "10s",
                "resolution": "768p"
            },
            "kling": {
                "name": "Kling Video 2.1",
                "provider": "FAL AI", 
                "description": "High-quality image-to-video generation",
                "best_for": "Quality, professional results",
                "cost_per_video": "$0.15",
                "avg_time": "45-90 seconds",
                "max_duration": "10s",
                "resolution": "1024p"
            },
            "veo3": {
                "name": "Google Veo 3.0",
                "provider": "Google (via Vertex AI)",
                "description": "Premium quality, enterprise-grade",
                "best_for": "Highest quality, long videos",
                "cost_per_video": "$3.00",
                "avg_time": "2-5 minutes",
                "max_duration": "8s",
                "resolution": "720p"
            },
            "veo2": {
                "name": "Google Veo 2.0",
                "provider": "Google (via Vertex AI)",
                "description": "High-quality video generation",
                "best_for": "Quality, reliability",
                "cost_per_video": "$2.00",
                "avg_time": "2-4 minutes",
                "max_duration": "5s",
                "resolution": "720p"
            }
        }
        
        return model_info.get(model, {})
    
    def compare_models(self, prompt: str, image_url: str, models: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """Compare multiple models for a given prompt and image."""
        if models is None:
            models = self.get_available_models()
        
        comparison = {}
        for model in models:
            info = self.get_model_info(model)
            cost = self.estimate_cost(model)
            
            comparison[model] = {
                **info,
                "estimated_cost": cost,
                "available": model in self.get_available_models()
            }
        
        return comparison
    
    def _create_success_result(
        self,
        model: str,
        output_path: str = None,
        output_url: str = None,
        start_time: float = None,
        metadata: Dict[str, Any] = None
    ) -> ModelResult:
        """Create a successful result (thread-safe with explicit start_time)."""
        processing_time = time.time() - start_time if start_time else 0
        return ModelResult(
            success=True,
            model_used=model,
            processing_time=processing_time,
            cost_estimate=self.estimate_cost(model),
            output_path=output_path,
            output_url=output_url,
            metadata=metadata
        )

    def _create_error_result(self, model: str, error: str, start_time: float = None) -> ModelResult:
        """Create an error result (thread-safe with explicit start_time)."""
        processing_time = time.time() - start_time if start_time else 0
        return ModelResult(
            success=False,
            model_used=model,
            processing_time=processing_time,
            cost_estimate=0.0,
            error=error
        )