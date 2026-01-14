"""
Base step executor for AI Content Pipeline.

Provides the common interface and utilities for all step executors.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class StepResult:
    """Result of executing a single step."""
    success: bool
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    output_text: Optional[str] = None
    processing_time: float = 0.0
    cost: float = 0.0
    model: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    extracted_prompt: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backwards compatibility."""
        return {
            "success": self.success,
            "output_path": self.output_path,
            "output_url": self.output_url,
            "output_text": self.output_text,
            "processing_time": self.processing_time,
            "cost": self.cost,
            "model": self.model,
            "metadata": self.metadata or {},
            "error": self.error,
            "extracted_prompt": self.extracted_prompt,
        }


class BaseStepExecutor(ABC):
    """
    Abstract base class for step executors.

    Each step type should have its own executor that inherits from this class.
    """

    @abstractmethod
    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the step and return results.

        Args:
            step: PipelineStep configuration
            input_data: Input data for the step
            chain_config: Chain configuration
            step_context: Context from previous steps
            **kwargs: Additional parameters

        Returns:
            Dictionary with execution results
        """
        pass

    def _merge_params(
        self,
        step_params: Dict[str, Any],
        chain_config: Dict[str, Any],
        kwargs: Dict[str, Any],
        exclude_keys: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Merge step params with chain config and kwargs.

        Args:
            step_params: Parameters from the step configuration
            chain_config: Chain configuration
            kwargs: Additional keyword arguments
            exclude_keys: Keys to exclude from merging

        Returns:
            Merged parameters dictionary
        """
        exclude = set(exclude_keys or [])
        params = {
            **{k: v for k, v in step_params.items() if k not in exclude},
            **{k: v for k, v in kwargs.items() if k not in exclude},
            "output_dir": chain_config.get("output_dir", "output")
        }
        return params

    def _create_error_result(self, error: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Create a standardized error result."""
        return {
            "success": False,
            "output_path": None,
            "output_url": None,
            "output_text": None,
            "processing_time": 0.0,
            "cost": 0.0,
            "model": model,
            "metadata": {},
            "error": error
        }
