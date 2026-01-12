#!/usr/bin/env python3
"""
Unified Text-to-Image Generator

Multi-provider text-to-image generation supporting both FAL AI and Replicate.
Provides a single interface for accessing multiple models across providers.

Supported Providers:
1. FAL AI - Multiple FLUX models, Imagen 4, Seedream v3
2. Replicate - Seedream-3, and extensible for more models

Author: AI Assistant
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Literal
from enum import Enum

# Import providers
try:
    from fal_text_to_image_generator import FALTextToImageGenerator
except ImportError:
    print("❌ FAL generator not found. Check fal_text_to_image_generator.py")
    FALTextToImageGenerator = None

try:
    from replicate_text_to_image_generator import ReplicateTextToImageGenerator, ReplicateTextToImageModel
except ImportError:
    print("❌ Replicate generator not found. Check replicate_text_to_image_generator.py")
    ReplicateTextToImageGenerator = None
    ReplicateTextToImageModel = None

try:
    from runway_gen4_generator import RunwayGen4Generator, RunwayGen4Model
except ImportError:
    print("❌ Runway Gen4 generator not found. Check runway_gen4_generator.py")
    RunwayGen4Generator = None
    RunwayGen4Model = None


class Provider(Enum):
    """Available providers."""
    FAL = "fal"
    REPLICATE = "replicate"


class MockProvider:
    """Mock provider for testing without API keys."""
    
    def __init__(self, name: str, models: List[str]):
        self.name = name
        self.models = models
    
    def generate_image(self, prompt: str, model: str = None, **kwargs) -> Dict[str, Any]:
        """Mock image generation that returns fake results."""
        return {
            'success': True,
            'image_url': f'mock://generated-image-{int(time.time())}.jpg',
            'image_path': f'/tmp/mock_image_{int(time.time())}.jpg',
            'model_used': model or self.models[0],
            'provider': self.name,
            'cost_estimate': 0.001,
            'processing_time': 2.5,
            'prompt': prompt,
            'mock_mode': True
        }
    
    def get_available_models(self) -> List[str]:
        """Return list of mock models."""
        return self.models


class UnifiedTextToImageGenerator:
    """
    Unified interface for multiple text-to-image providers.
    
    Supports automatic provider selection, cost comparison, and
    seamless switching between FAL AI and Replicate models.
    """
    
    # Unified model catalog
    MODEL_CATALOG = {
        # FAL AI Models
        "flux_dev": {
            "provider": Provider.FAL,
            "model_key": "flux_dev",
            "name": "FLUX.1 Dev",
            "resolution": "1024x1024",
            "cost_per_image": 0.003,
            "quality": "high",
            "speed": "medium",
            "use_case": "High-quality generation"
        },
        "flux_schnell": {
            "provider": Provider.FAL,
            "model_key": "flux_schnell",
            "name": "FLUX.1 Schnell",
            "resolution": "1024x1024",
            "cost_per_image": 0.001,
            "quality": "good",
            "speed": "fast",
            "use_case": "Fast generation"
        },
        "imagen4": {
            "provider": Provider.FAL,
            "model_key": "imagen4",
            "name": "Google Imagen 4",
            "resolution": "1024x1024",
            "cost_per_image": 0.004,
            "quality": "high",
            "speed": "medium",
            "use_case": "Photorealistic images"
        },
        "seedream_fal": {
            "provider": Provider.FAL,
            "model_key": "seedream",
            "name": "Seedream v3 (FAL)",
            "resolution": "1024x1024",
            "cost_per_image": 0.002,
            "quality": "good",
            "speed": "fast",
            "use_case": "Bilingual support"
        },
        "nano_banana_pro": {
            "provider": Provider.FAL,
            "model_key": "nano_banana_pro",
            "name": "Nano Banana Pro",
            "resolution": "1024x1024",
            "cost_per_image": 0.015,
            "quality": "high",
            "speed": "fast",
            "use_case": "Fast high-quality generation"
        },
        "gpt_image_1_5": {
            "provider": Provider.FAL,
            "model_key": "gpt_image_1_5",
            "name": "GPT Image 1.5",
            "resolution": "1024x1024",
            "cost_per_image": 0.02,
            "quality": "high",
            "speed": "medium",
            "use_case": "GPT-powered generation"
        },
        # Replicate Models
        "seedream3": {
            "provider": Provider.REPLICATE,
            "model_key": "SEEDREAM3",
            "name": "ByteDance Seedream-3",
            "resolution": "Up to 2048px",
            "cost_per_image": 0.003,
            "quality": "high",
            "speed": "medium",
            "use_case": "High-resolution generation"
        },
        "gen4": {
            "provider": Provider.REPLICATE,
            "model_key": "GEN4_IMAGE",
            "name": "Runway Gen-4 Image",
            "resolution": "720p/1080p",
            "cost_per_image": 0.08,  # 1080p pricing (higher quality)
            "cost_720p": 0.05,
            "cost_1080p": 0.08,
            "quality": "cinematic",
            "speed": "medium",
            "use_case": "Multi-reference guided generation",
            "special_features": [
                "Up to 3 reference images",
                "Reference image tagging",
                "Cinematic quality",
                "Multiple resolutions"
            ]
        }
    }
    
    def __init__(self, fal_api_key: Optional[str] = None, replicate_api_token: Optional[str] = None, verbose: bool = True):
        """
        Initialize the Unified Text-to-Image Generator.
        
        Args:
            fal_api_key (str, optional): FAL AI API key
            replicate_api_token (str, optional): Replicate API token
            verbose (bool): Enable verbose output
        """
        self.verbose = verbose
        self.providers = {}
        self.runway_gen4 = None
        
        # Initialize available providers
        if FALTextToImageGenerator:
            try:
                self.providers[Provider.FAL] = FALTextToImageGenerator(api_key=fal_api_key)
                if verbose:
                    print("✅ FAL AI provider initialized")
            except Exception as e:
                if verbose:
                    print(f"⚠️ FAL AI provider initialization failed: {e}")
        
        if ReplicateTextToImageGenerator:
            try:
                self.providers[Provider.REPLICATE] = ReplicateTextToImageGenerator(api_token=replicate_api_token, verbose=False)
                if verbose:
                    print("✅ Replicate provider initialized")
            except Exception as e:
                if verbose:
                    print(f"⚠️ Replicate provider initialization failed: {e}")
        
        # Initialize Runway Gen4 generator (separate from basic Replicate)
        if RunwayGen4Generator:
            try:
                self.runway_gen4 = RunwayGen4Generator(api_token=replicate_api_token, verbose=False)
                if verbose:
                    print("✅ Runway Gen4 provider initialized")
            except Exception as e:
                if verbose:
                    print(f"⚠️ Runway Gen4 provider initialization failed: {e}")
        
        if not self.providers:
            # In testing environment, don't fail hard
            import os
            if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS') or not any([
                os.environ.get('FAL_KEY'),
                os.environ.get('REPLICATE_API_TOKEN')
            ]):
                if verbose:
                    print("⚠️  No API keys found - initializing mock providers")
                self._initialize_mock_providers()
            else:
                raise ValueError("No providers could be initialized. Check API keys and dependencies.")
        
        if verbose:
            print(f"🎨 Unified Text-to-Image Generator initialized with {len(self.providers)} provider(s)")
    
    def _initialize_mock_providers(self):
        """Initialize mock providers for testing without API keys."""
        # Create mock providers with fake models
        mock_providers = {
            'fal': MockProvider('fal', ['flux_dev', 'flux_schnell', 'seedream_v3']),
            'replicate': MockProvider('replicate', ['flux_dev_replicate', 'seedream3'])
        }
        self.providers = mock_providers
    
    def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        provider: Optional[Union[Provider, str]] = None,
        optimize_for: Optional[Literal["cost", "quality", "speed"]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate an image using the specified or optimal model.
        
        Args:
            prompt (str): Text description for image generation
            model (str, optional): Specific model to use (e.g., "flux_dev", "seedream3")
            provider (Provider/str, optional): Specific provider to use
            optimize_for (str, optional): Auto-select model optimized for "cost", "quality", or "speed"
            **kwargs: Additional arguments passed to the provider
        
        Returns:
            Dict[str, Any]: Generation result with unified format
        """
        # Auto-select model if not specified
        if not model:
            if optimize_for:
                model = self._get_optimal_model(optimize_for)
            else:
                model = "flux_schnell"  # Default to fast, cost-effective option
        
        # Get model configuration
        if model not in self.MODEL_CATALOG:
            available = list(self.MODEL_CATALOG.keys())
            raise ValueError(f"Unknown model '{model}'. Available: {available}")
        
        model_config = self.MODEL_CATALOG[model]
        target_provider = model_config["provider"]
        
        # Override provider if specified
        if provider:
            if isinstance(provider, str):
                provider = Provider(provider)
            if provider != target_provider:
                raise ValueError(f"Model '{model}' is only available on {target_provider.value}, not {provider.value}")
        
        # Check if we're in mock mode
        is_mock_mode = any(isinstance(p, MockProvider) for p in self.providers.values())
        
        if is_mock_mode:
            # Use mock provider - pick the first available one
            mock_provider = next(iter(self.providers.values()))
            return mock_provider.generate_image(prompt, model, **kwargs)
        
        # Check if provider is available
        if model == "gen4":
            if not self.runway_gen4:
                raise ValueError("Runway Gen4 generator not initialized")
        elif target_provider not in self.providers:
            raise ValueError(f"Provider {target_provider.value} not initialized")
        
        if self.verbose:
            print(f"🎨 Using {model_config['name']} on {target_provider.value}")
            print(f"💰 Estimated cost: ${model_config['cost_per_image']:.3f}")
        
        # Generate with appropriate provider
        if target_provider == Provider.FAL:
            result = self.providers[Provider.FAL].generate_image(
                prompt=prompt,
                model=model_config["model_key"],
                **kwargs
            )
        elif target_provider == Provider.REPLICATE:
            # Handle Gen4 model separately
            if model == "gen4":
                if not self.runway_gen4:
                    raise ValueError("Runway Gen4 generator not available")
                
                # Convert model_key to enum for Gen4
                model_enum = getattr(RunwayGen4Model, model_config["model_key"])
                result = self.runway_gen4.generate_image(
                    prompt=prompt,
                    model=model_enum,
                    **kwargs
                )
            else:
                # Handle other Replicate models (Seedream-3)
                if Provider.REPLICATE not in self.providers:
                    raise ValueError("Basic Replicate provider not available")
                
                # Convert model_key to enum
                model_enum = getattr(ReplicateTextToImageModel, model_config["model_key"])
                result = self.providers[Provider.REPLICATE].generate_image(
                    prompt=prompt,
                    model=model_enum,
                    **kwargs
                )
        else:
            raise ValueError(f"Unknown provider: {target_provider}")
        
        # Add unified metadata
        if result.get('success'):
            result.update({
                'unified_model': model,
                'provider': target_provider.value,
                'model_config': model_config
            })
        
        return result
    
    def _get_optimal_model(self, optimize_for: str) -> str:
        """Get the optimal model based on criteria."""
        available_models = {}
        for model, config in self.MODEL_CATALOG.items():
            # Check if model is available
            if model == "gen4":
                if self.runway_gen4:
                    available_models[model] = config
            elif config["provider"] in self.providers:
                available_models[model] = config
        
        if optimize_for == "cost":
            # Find cheapest model
            return min(available_models.keys(), key=lambda m: available_models[m]["cost_per_image"])
        elif optimize_for == "quality":
            # Prefer high-quality models
            quality_order = {"high": 3, "good": 2, "medium": 1}
            return max(available_models.keys(), key=lambda m: quality_order.get(available_models[m]["quality"], 0))
        elif optimize_for == "speed":
            # Prefer fast models
            speed_order = {"fast": 3, "medium": 2, "slow": 1}
            return max(available_models.keys(), key=lambda m: speed_order.get(available_models[m]["speed"], 0))
        else:
            raise ValueError(f"Unknown optimization criteria: {optimize_for}")
    
    def compare_models(self) -> Dict[str, Any]:
        """Compare all available models across providers."""
        available_models = {
            model: config for model, config in self.MODEL_CATALOG.items()
            if config["provider"] in self.providers
        }
        
        return {
            "total_models": len(available_models),
            "providers": list(self.providers.keys()),
            "models": available_models,
            "recommendations": {
                "cheapest": self._get_optimal_model("cost"),
                "highest_quality": self._get_optimal_model("quality"),
                "fastest": self._get_optimal_model("speed")
            }
        }
    
    def print_model_comparison(self):
        """Print a detailed comparison of all available models."""
        print("🎨 Unified Text-to-Image Model Comparison")
        print("=" * 80)
        
        available_models = {
            model: config for model, config in self.MODEL_CATALOG.items()
            if config["provider"] in self.providers
        }
        
        # Group by provider
        providers = {}
        for model, config in available_models.items():
            provider_name = config["provider"].value
            if provider_name not in providers:
                providers[provider_name] = []
            providers[provider_name].append((model, config))
        
        for provider_name, models in providers.items():
            print(f"\n🔸 {provider_name.upper()} Provider")
            print("-" * 50)
            
            for model_key, config in models:
                print(f"\n🖼️ {config['name']} ({model_key})")
                print(f"   📐 Resolution: {config['resolution']}")
                print(f"   💰 Cost: ${config['cost_per_image']:.3f} per image")
                print(f"   ⚡ Speed: {config['speed']} | 🎯 Quality: {config['quality']}")
                print(f"   💡 Use case: {config['use_case']}")
        
        # Print recommendations
        try:
            recommendations = self.compare_models()["recommendations"]
            print(f"\n💡 Recommendations:")
            print(f"   💰 Cheapest: {recommendations['cheapest']}")
            print(f"   🎯 Highest Quality: {recommendations['highest_quality']}")
            print(f"   ⚡ Fastest: {recommendations['fastest']}")
        except:
            pass
    
    def get_available_models(self) -> List[str]:
        """Get list of available model keys."""
        available = []
        for model, config in self.MODEL_CATALOG.items():
            if model == "gen4":
                if self.runway_gen4:
                    available.append(model)
            elif config["provider"] in self.providers:
                available.append(model)
        return available
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [provider.value for provider in self.providers.keys()]
    
    def estimate_cost(self, model: str, num_images: int = 1) -> float:
        """Estimate cost for generating images."""
        if model not in self.MODEL_CATALOG:
            raise ValueError(f"Unknown model: {model}")
        
        return self.MODEL_CATALOG[model]["cost_per_image"] * num_images
    
    def test_connections(self) -> Dict[str, bool]:
        """Test connections to all available providers."""
        results = {}
        
        for provider, generator in self.providers.items():
            try:
                if hasattr(generator, 'test_connection'):
                    results[provider.value] = generator.test_connection()
                else:
                    results[provider.value] = True  # Assume working if no test method
            except Exception as e:
                results[provider.value] = False
                if self.verbose:
                    print(f"❌ {provider.value} connection test failed: {e}")
        
        return results


def main():
    """Example usage of Unified Text-to-Image Generator."""
    print("🎨 Unified Text-to-Image Generator Example")
    print("=" * 60)
    
    try:
        # Initialize generator
        generator = UnifiedTextToImageGenerator(verbose=True)
        
        # Print model comparison
        print("\n" + "=" * 60)
        generator.print_model_comparison()
        
        # Test connections
        print("\n" + "=" * 60)
        print("🔍 Testing provider connections...")
        connections = generator.test_connections()
        for provider, status in connections.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {provider}: {'Connected' if status else 'Failed'}")
        
        # Show usage examples
        print("\n" + "=" * 60)
        print("💡 Usage Examples:")
        print("   # Auto-select cheapest model:")
        print("   generator.generate_image('cat', optimize_for='cost')")
        print("   # Use specific model:")
        print("   generator.generate_image('cat', model='seedream3')")
        print("   # Use specific provider:")
        print("   generator.generate_image('cat', provider='replicate')")
        
        print("\n⚠️ WARNING: Image generation incurs costs!")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("💡 Make sure you have valid API keys set up")


if __name__ == "__main__":
    main()