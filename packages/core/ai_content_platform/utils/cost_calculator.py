"""Cost calculation and management utilities."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from ai_content_platform.core.models import StepType, StepConfig
from ai_content_platform.core.exceptions import CostCalculationError
from ai_content_platform.utils.logger import get_logger


class ServiceProvider(str, Enum):
    """Supported service providers."""
    FAL_AI = "fal_ai"
    ELEVENLABS = "elevenlabs"
    GOOGLE_VERTEX = "google_vertex"
    OPENROUTER = "openrouter"


@dataclass
class CostEstimate:
    """Cost estimation result."""
    service: ServiceProvider
    step_type: StepType
    estimated_cost: float
    currency: str = "USD"
    details: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8  # Estimation confidence (0-1)


@dataclass
class CostSummary:
    """Summary of costs for a pipeline."""
    total_estimated_cost: float
    by_service: Dict[ServiceProvider, float]
    by_step_type: Dict[StepType, float]
    estimates: List[CostEstimate]
    currency: str = "USD"


class CostCalculator:
    """Calculator for estimating and tracking costs."""
    
    # Base cost rates per service and step type (in USD)
    COST_RATES = {
        ServiceProvider.FAL_AI: {
            StepType.TEXT_TO_IMAGE: {
                "imagen-4": 0.005,
                "seedream-v3": 0.003,
                "flux-1-schnell": 0.001,
                "flux-1-dev": 0.002,
                "nano_banana_pro": 0.002,
                "gpt_image_1_5": 0.003,
                "default": 0.003
            },
            StepType.IMAGE_TO_IMAGE: {
                "luma-photon-flash": 0.01,
                "nano_banana_pro_edit": 0.015,
                "gpt_image_1_5_edit": 0.02,
                "default": 0.01
            },
            StepType.TEXT_TO_VIDEO: {
                "minimax-hailuo-02-pro": 0.08,
                "google-veo-3": 4.0,
                "default": 0.08
            },
            StepType.VIDEO_GENERATION: {
                "minimax-hailuo-02": 0.05,
                "kling-video-2-1": 0.07,
                "default": 0.06
            },
            StepType.VIDEO_TO_VIDEO: {
                "thinksound": 0.02,
                "topaz": 0.15,
                "default": 0.08
            },
            StepType.AVATAR_GENERATION: {
                "text-to-speech": 0.02,
                "audio-to-avatar": 0.03,
                "default": 0.025
            }
        },
        ServiceProvider.ELEVENLABS: {
            StepType.TEXT_TO_SPEECH: {
                "default": 0.18  # Per 1000 characters
            }
        },
        ServiceProvider.GOOGLE_VERTEX: {
            StepType.TEXT_TO_VIDEO: {
                "veo-3": 6.0,
                "default": 6.0
            }
        },
        ServiceProvider.OPENROUTER: {
            StepType.TEXT_TO_SPEECH: {
                "default": 0.10  # Approximate cost per request
            }
        }
    }
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._cost_history: List[CostEstimate] = []
    
    def estimate_step_cost(self, step: StepConfig) -> CostEstimate:
        """Estimate cost for a single step.
        
        Args:
            step: Step configuration
            
        Returns:
            Cost estimate
            
        Raises:
            CostCalculationError: If cost calculation fails
        """
        try:
            service = self._determine_service_provider(step)
            cost_data = self.COST_RATES.get(service, {}).get(step.step_type, {})
            
            if not cost_data:
                raise CostCalculationError(
                    f"No cost data available for {service.value} + {step.step_type.value}"
                )
            
            # Get model-specific cost or default
            model = step.parameters.get("model", "default")
            base_cost = cost_data.get(model, cost_data.get("default", 0.0))
            
            # Apply step-specific multipliers
            multiplier = self._calculate_step_multiplier(step)
            estimated_cost = base_cost * multiplier
            
            estimate = CostEstimate(
                service=service,
                step_type=step.step_type,
                estimated_cost=estimated_cost,
                details={
                    "base_cost": base_cost,
                    "multiplier": multiplier,
                    "model": model,
                    "step_name": step.name
                }
            )
            
            self.logger.debug(f"Cost estimate for {step.name}: ${estimated_cost:.4f}")
            return estimate
            
        except Exception as e:
            error_msg = f"Failed to estimate cost for step {step.name}: {str(e)}"
            self.logger.error(error_msg)
            raise CostCalculationError(error_msg) from e
    
    def estimate_pipeline_cost(self, steps: List[StepConfig]) -> CostSummary:
        """Estimate total cost for a pipeline.
        
        Args:
            steps: List of step configurations
            
        Returns:
            Cost summary
            
        Raises:
            CostCalculationError: If pipeline cost calculation fails
        """
        try:
            estimates = []
            by_service: Dict[ServiceProvider, float] = {}
            by_step_type: Dict[StepType, float] = {}
            
            for step in steps:
                estimate = self.estimate_step_cost(step)
                estimates.append(estimate)
                
                # Aggregate by service
                by_service[estimate.service] = (
                    by_service.get(estimate.service, 0.0) + estimate.estimated_cost
                )
                
                # Aggregate by step type
                by_step_type[estimate.step_type] = (
                    by_step_type.get(estimate.step_type, 0.0) + estimate.estimated_cost
                )
            
            total_cost = sum(est.estimated_cost for est in estimates)
            
            summary = CostSummary(
                total_estimated_cost=total_cost,
                by_service=by_service,
                by_step_type=by_step_type,
                estimates=estimates
            )
            
            self.logger.info(f"Total pipeline cost estimate: ${total_cost:.4f}")
            return summary
            
        except Exception as e:
            error_msg = f"Failed to estimate pipeline cost: {str(e)}"
            self.logger.error(error_msg)
            raise CostCalculationError(error_msg) from e
    
    def check_cost_limit(
        self, 
        estimated_cost: float, 
        max_cost: Optional[float] = None
    ) -> bool:
        """Check if estimated cost is within limits.
        
        Args:
            estimated_cost: Estimated cost to check
            max_cost: Maximum allowed cost (optional)
            
        Returns:
            True if within limits
            
        Raises:
            CostCalculationError: If cost exceeds limits
        """
        if max_cost is not None and estimated_cost > max_cost:
            error_msg = (
                f"Estimated cost ${estimated_cost:.4f} "
                f"exceeds maximum allowed cost ${max_cost:.4f}"
            )
            self.logger.error(error_msg)
            raise CostCalculationError(error_msg)
        
        return True
    
    def track_actual_cost(self, step_name: str, actual_cost: float) -> None:
        """Track actual cost for comparison with estimates.
        
        Args:
            step_name: Name of the executed step
            actual_cost: Actual cost incurred
        """
        self.logger.cost(actual_cost)
        self.logger.info(f"Actual cost for {step_name}: ${actual_cost:.4f}")
    
    def get_cost_report(self) -> Dict[str, Any]:
        """Get comprehensive cost report.
        
        Returns:
            Cost report with estimates and actuals
        """
        return {
            "cost_history": [
                {
                    "service": est.service.value,
                    "step_type": est.step_type.value,
                    "estimated_cost": est.estimated_cost,
                    "currency": est.currency,
                    "confidence": est.confidence,
                    "details": est.details
                }
                for est in self._cost_history
            ],
            "total_estimates": len(self._cost_history),
            "total_estimated_cost": sum(est.estimated_cost for est in self._cost_history)
        }
    
    def _determine_service_provider(self, step: StepConfig) -> ServiceProvider:
        """Determine service provider based on step configuration."""
        # Logic to determine provider based on step type and parameters
        if step.step_type == StepType.TEXT_TO_SPEECH:
            if step.parameters.get("provider") == "openrouter":
                return ServiceProvider.OPENROUTER
            return ServiceProvider.ELEVENLABS
        
        elif step.step_type in [
            StepType.TEXT_TO_IMAGE,
            StepType.IMAGE_TO_IMAGE,
            StepType.VIDEO_GENERATION,
            StepType.VIDEO_TO_VIDEO,
            StepType.AVATAR_GENERATION
        ]:
            return ServiceProvider.FAL_AI
        
        elif step.step_type == StepType.TEXT_TO_VIDEO:
            model = step.parameters.get("model", "")
            if "veo" in model.lower():
                return ServiceProvider.GOOGLE_VERTEX
            return ServiceProvider.FAL_AI
        
        # Default to FAL AI for unknown types
        return ServiceProvider.FAL_AI
    
    def _calculate_step_multiplier(self, step: StepConfig) -> float:
        """Calculate cost multiplier based on step parameters."""
        multiplier = 1.0
        
        # Text-to-speech multiplier based on text length
        if step.step_type == StepType.TEXT_TO_SPEECH:
            text = step.parameters.get("text", "")
            if text:
                # Approximate cost per 1000 characters
                char_count = len(text)
                multiplier = max(1.0, char_count / 1000)
        
        # Image generation multiplier based on resolution/quality
        elif step.step_type in [StepType.TEXT_TO_IMAGE, StepType.IMAGE_TO_IMAGE]:
            # Higher resolution = higher cost
            width = step.parameters.get("width", 1024)
            height = step.parameters.get("height", 1024)
            base_pixels = 1024 * 1024
            actual_pixels = width * height
            multiplier = actual_pixels / base_pixels
        
        # Video generation multiplier based on duration
        elif step.step_type in [StepType.TEXT_TO_VIDEO, StepType.VIDEO_GENERATION]:
            duration = step.parameters.get("duration", 5)  # Default 5 seconds
            base_duration = 5
            multiplier = duration / base_duration
        
        return max(0.1, multiplier)  # Minimum multiplier of 0.1