"""
Unified Text-to-Image Generator for AI Content Pipeline

Integrates multiple text-to-image models with smart selection and cost optimization.
"""

import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

from .base import BaseContentModel, ModelResult
from ..config.constants import SUPPORTED_MODELS, COST_ESTIMATES, MODEL_RECOMMENDATIONS


class UnifiedTextToImageGenerator(BaseContentModel):
    """
    Unified interface for multiple text-to-image models.
    
    Supports FAL AI models (FLUX.1, Imagen 4, Seedream v3) with plans for
    OpenAI DALL-E and Stability AI integration.
    """
    
    def __init__(self):
        super().__init__("text_to_image")
        self._fal_generator = None
        self._unified_generator = None
        self._initialize_generators()
    
    def _initialize_generators(self):
        """Initialize available text-to-image generators."""
        try:
            # Try to import unified generator (supports FAL + Replicate)
            fal_path = Path(__file__).parent.parent.parent.parent.parent / "providers" / "fal" / "text-to-image"
            if fal_path.exists():
                sys.path.insert(0, str(fal_path))
                
                # Try unified generator first (supports multiple providers)
                try:
                    from unified_text_to_image_generator import UnifiedTextToImageGenerator
                    self._unified_generator = UnifiedTextToImageGenerator(verbose=False)
                    print("✅ Unified Text-to-Image generator initialized (FAL + Replicate)")
                except ImportError:
                    # Fallback to FAL-only generator
                    from fal_text_to_image_generator import FALTextToImageGenerator
                    self._fal_generator = FALTextToImageGenerator()
                    print("✅ FAL Text-to-Image generator initialized")
            else:
                print(f"⚠️  Text-to-Image directory not found at: {fal_path}")
        except ImportError as e:
            print(f"⚠️  Text-to-Image generators not available: {e}")
    
    def generate(self, prompt: str, model: str = "auto", **kwargs) -> ModelResult:
        """
        Generate image from text using specified model.
        
        Args:
            prompt: Text prompt for image generation
            model: Model to use ("auto" for smart selection)
            **kwargs: Additional generation parameters
            
        Returns:
            ModelResult with generation results
        """
        self._start_timing()
        
        try:
            # Validate input
            if not self.validate_input(prompt, model, **kwargs):
                return self._create_error_result(model, "Invalid input parameters")
            
            # Auto-select model if needed
            if model == "auto":
                budget = kwargs.get("budget")
                criteria = kwargs.get("criteria", "balanced")
                model = self.recommend_model(criteria, budget)
                print(f"🤖 Auto-selected model: {model}")
            
            # Route to appropriate generator
            if self._unified_generator and model in ["flux_dev", "flux_schnell", "imagen4", "seedream_v3", "seedream3", "gen4"]:
                return self._generate_with_unified(prompt, model, **kwargs)
            elif self._fal_generator and model in ["flux_dev", "flux_schnell", "imagen4", "seedream_v3"]:
                return self._generate_with_fal(prompt, model, **kwargs)
            elif model == "dalle3":
                return self._generate_with_openai(prompt, model, **kwargs)
            elif model == "stable_diffusion":
                return self._generate_with_stability(prompt, model, **kwargs)
            else:
                return self._create_error_result(model, f"Unsupported model: {model}")
                
        except Exception as e:
            return self._create_error_result(model, f"Generation failed: {str(e)}")
    
    def _generate_with_unified(self, prompt: str, model: str, **kwargs) -> ModelResult:
        """Generate image using unified generator (supports FAL + Replicate)."""
        if not self._unified_generator:
            return self._create_error_result(model, "Unified generator not available")
        
        try:
            # Extract common parameters
            output_dir = kwargs.get("output_dir", "output")
            
            # Generate image using unified interface
            result = self._unified_generator.generate_image(
                prompt=prompt,
                model=model,
                **{k: v for k, v in kwargs.items() 
                   if k not in ["output_dir", "budget", "criteria"]}
            )
            
            if result.get("success"):
                return self._create_success_result(
                    model=model,
                    output_path=result.get("local_path"),
                    output_url=result.get("image_url"),
                    metadata={
                        "prompt": prompt,
                        "provider": result.get("provider", "unknown"),
                        "model_config": result.get("model_config", {}),
                        "unified_model": result.get("unified_model", model),
                        "cost_usd": result.get("cost_usd", 0)
                    }
                )
            else:
                return self._create_error_result(model, result.get("error", "Generation failed"))
                
        except Exception as e:
            return self._create_error_result(model, f"Unified generation failed: {str(e)}")
    
    def _generate_with_fal(self, prompt: str, model: str, **kwargs) -> ModelResult:
        """Generate image using FAL AI models."""
        if not self._fal_generator:
            return self._create_error_result(model, "FAL generator not available")
        
        try:
            # Map our model names to FAL model names
            fal_model_map = {
                "flux_dev": "flux_dev",
                "flux_schnell": "flux_schnell", 
                "imagen4": "imagen4",
                "seedream_v3": "seedream"
            }
            
            fal_model = fal_model_map.get(model, model)
            
            # Extract FAL-specific parameters
            output_dir = kwargs.get("output_dir", "output")
            aspect_ratio = kwargs.get("aspect_ratio", "16:9")
            
            # Generate image
            result = self._fal_generator.generate_image(
                prompt=prompt,
                model=fal_model,
                output_folder=output_dir,
                aspect_ratio=aspect_ratio,
                **{k: v for k, v in kwargs.items() 
                   if k not in ["output_dir", "aspect_ratio", "budget", "criteria"]}
            )
            
            if result.get("success"):
                return self._create_success_result(
                    model=model,
                    output_path=result.get("local_path"),
                    output_url=result.get("image_url"),
                    metadata={
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio,
                        "fal_response": result.get("response", {})
                    }
                )
            else:
                return self._create_error_result(model, result.get("error", "FAL generation failed"))
                
        except Exception as e:
            return self._create_error_result(model, f"FAL generation error: {str(e)}")
    
    def _generate_with_openai(self, prompt: str, model: str, **kwargs) -> ModelResult:
        """Generate image using OpenAI DALL-E (planned)."""
        return self._create_error_result(model, "OpenAI DALL-E integration not yet implemented")
    
    def _generate_with_stability(self, prompt: str, model: str, **kwargs) -> ModelResult:
        """Generate image using Stability AI (planned)."""
        return self._create_error_result(model, "Stability AI integration not yet implemented")
    
    def get_available_models(self) -> List[str]:
        """Get list of available text-to-image models."""
        available = []
        
        # Check FAL models
        if self._fal_generator:
            available.extend(["flux_dev", "flux_schnell", "imagen4", "seedream_v3"])
        
        # TODO: Check other providers when implemented
        
        return available
    
    def estimate_cost(self, model: str, **kwargs) -> float:
        """Estimate cost for image generation."""
        costs = COST_ESTIMATES.get("text_to_image", {})
        return costs.get(model, 0.0)
    
    def validate_input(self, prompt: str, model: str, **kwargs) -> bool:
        """Validate input parameters."""
        if not isinstance(prompt, str) or len(prompt.strip()) == 0:
            return False
        
        if model != "auto" and model not in SUPPORTED_MODELS.get("text_to_image", []):
            return False
        
        # Validate aspect ratio if provided
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            valid_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]
            if aspect_ratio not in valid_ratios:
                return False
        
        return True
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a specific model."""
        model_info = {
            "flux_dev": {
                "name": "FLUX.1 Dev",
                "provider": "FAL AI",
                "description": "High-quality 12B parameter model",
                "best_for": "Quality, artistic content",
                "cost_per_image": "$0.003",
                "avg_time": "15 seconds"
            },
            "flux_schnell": {
                "name": "FLUX.1 Schnell", 
                "provider": "FAL AI",
                "description": "Fast inference model",
                "best_for": "Speed, prototyping",
                "cost_per_image": "$0.001",
                "avg_time": "5 seconds"
            },
            "imagen4": {
                "name": "Imagen 4 Preview Fast",
                "provider": "Google (via FAL AI)",
                "description": "Google's latest image model",
                "best_for": "Photorealism, text rendering",
                "cost_per_image": "$0.004", 
                "avg_time": "20 seconds"
            },
            "seedream_v3": {
                "name": "Seedream v3",
                "provider": "FAL AI",
                "description": "Bilingual (Chinese/English) model",
                "best_for": "Multilingual prompts, cost-effective",
                "cost_per_image": "$0.002",
                "avg_time": "10 seconds"
            },
            "nano_banana_pro": {
                "name": "Nano Banana Pro",
                "provider": "FAL AI",
                "description": "Fast, high-quality image generation",
                "best_for": "Speed, cost-effective, quality",
                "cost_per_image": "$0.002",
                "avg_time": "5 seconds"
            },
            "gpt_image_1_5": {
                "name": "GPT Image 1.5",
                "provider": "FAL AI",
                "description": "GPT-powered image generation",
                "best_for": "Natural language understanding, creative prompts",
                "cost_per_image": "$0.003",
                "avg_time": "8 seconds"
            }
        }
        
        return model_info.get(model, {})
    
    def compare_models(self, prompt: str, models: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """Compare multiple models for a given prompt."""
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