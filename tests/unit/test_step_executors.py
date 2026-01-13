"""
Unit tests for step executors module.

Tests the refactored step executor classes.
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import sys

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.core.ai_content_pipeline.ai_content_pipeline.pipeline.step_executors import (
    BaseStepExecutor,
    StepResult,
    TextToImageExecutor,
    ImageUnderstandingExecutor,
    PromptGenerationExecutor,
    ImageToImageExecutor,
    ImageToVideoExecutor,
    TextToSpeechExecutor,
)
from packages.core.ai_content_pipeline.ai_content_pipeline.pipeline.chain import (
    PipelineStep,
    StepType,
)


class TestStepResult:
    """Tests for StepResult dataclass."""

    def test_step_result_creation(self):
        """Test creating a basic StepResult."""
        result = StepResult(
            success=True,
            output_path="/path/to/output.png",
            cost=0.05
        )
        assert result.success is True
        assert result.output_path == "/path/to/output.png"
        assert result.cost == 0.05

    def test_step_result_to_dict(self):
        """Test converting StepResult to dictionary."""
        result = StepResult(
            success=True,
            output_url="https://example.com/image.png",
            processing_time=5.5,
            cost=0.10,
            model="flux_dev"
        )
        result_dict = result.to_dict()

        assert result_dict["success"] is True
        assert result_dict["output_url"] == "https://example.com/image.png"
        assert result_dict["processing_time"] == 5.5
        assert result_dict["cost"] == 0.10
        assert result_dict["model"] == "flux_dev"

    def test_step_result_defaults(self):
        """Test StepResult default values."""
        result = StepResult(success=False)
        assert result.output_path is None
        assert result.output_url is None
        assert result.processing_time == 0.0
        assert result.cost == 0.0
        assert result.metadata is None


class TestTextToImageExecutor:
    """Tests for TextToImageExecutor."""

    def test_executor_initialization(self):
        """Test TextToImageExecutor can be initialized."""
        mock_generator = Mock()
        executor = TextToImageExecutor(mock_generator)
        assert executor.generator == mock_generator

    def test_executor_execute_success(self):
        """Test successful text-to-image execution."""
        mock_generator = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.output_path = "/path/to/image.png"
        mock_result.output_url = "https://example.com/image.png"
        mock_result.processing_time = 10.5
        mock_result.cost_estimate = 0.05
        mock_result.model_used = "flux_dev"
        mock_result.metadata = {"seed": 12345}
        mock_result.error = None
        mock_generator.generate.return_value = mock_result

        executor = TextToImageExecutor(mock_generator)

        step = PipelineStep(
            step_type=StepType.TEXT_TO_IMAGE,
            model="flux_dev",
            params={"width": 1024, "height": 1024}
        )

        result = executor.execute(
            step=step,
            input_data="A beautiful sunset",
            chain_config={"output_dir": "output"}
        )

        assert result["success"] is True
        assert result["output_path"] == "/path/to/image.png"
        assert result["cost"] == 0.05
        mock_generator.generate.assert_called_once()

    def test_executor_execute_failure(self):
        """Test failed text-to-image execution."""
        mock_generator = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.output_path = None
        mock_result.output_url = None
        mock_result.processing_time = 0
        mock_result.cost_estimate = 0
        mock_result.model_used = "flux_dev"
        mock_result.metadata = {}
        mock_result.error = "API error"
        mock_generator.generate.return_value = mock_result

        executor = TextToImageExecutor(mock_generator)

        step = PipelineStep(
            step_type=StepType.TEXT_TO_IMAGE,
            model="flux_dev",
            params={}
        )

        result = executor.execute(
            step=step,
            input_data="A prompt",
            chain_config={"output_dir": "output"}
        )

        assert result["success"] is False
        assert result["error"] == "API error"


class TestImageUnderstandingExecutor:
    """Tests for ImageUnderstandingExecutor."""

    def test_executor_initialization(self):
        """Test ImageUnderstandingExecutor can be initialized."""
        mock_generator = Mock()
        executor = ImageUnderstandingExecutor(mock_generator)
        assert executor.generator == mock_generator

    def test_executor_with_prompt(self):
        """Test image understanding with custom prompt."""
        mock_generator = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.output_text = "This is a landscape image"
        mock_result.processing_time = 2.0
        mock_result.cost_estimate = 0.01
        mock_result.model_used = "gemini_description"
        mock_result.metadata = {}
        mock_result.error = None
        mock_generator.analyze.return_value = mock_result

        executor = ImageUnderstandingExecutor(mock_generator)

        step = PipelineStep(
            step_type=StepType.IMAGE_UNDERSTANDING,
            model="gemini_description",
            params={"prompt": "Describe this image in detail"}
        )

        result = executor.execute(
            step=step,
            input_data="/path/to/image.jpg",
            chain_config={"output_dir": "output"}
        )

        assert result["success"] is True
        assert result["output_text"] == "This is a landscape image"


class TestPromptGenerationExecutor:
    """Tests for PromptGenerationExecutor."""

    def test_executor_initialization(self):
        """Test PromptGenerationExecutor can be initialized."""
        mock_generator = Mock()
        executor = PromptGenerationExecutor(mock_generator)
        assert executor.generator == mock_generator

    def test_executor_returns_extracted_prompt(self):
        """Test that executor returns extracted_prompt field."""
        mock_generator = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.output_text = "Full analysis text"
        mock_result.extracted_prompt = "Optimized video prompt"
        mock_result.processing_time = 3.0
        mock_result.cost_estimate = 0.02
        mock_result.model_used = "openrouter_prompt"
        mock_result.metadata = {}
        mock_result.error = None
        mock_generator.generate.return_value = mock_result

        executor = PromptGenerationExecutor(mock_generator)

        step = PipelineStep(
            step_type=StepType.PROMPT_GENERATION,
            model="openrouter_prompt",
            params={"video_style": "cinematic"}
        )

        result = executor.execute(
            step=step,
            input_data="/path/to/image.jpg",
            chain_config={"output_dir": "output"}
        )

        assert result["success"] is True
        assert result["extracted_prompt"] == "Optimized video prompt"
        assert result["output_text"] == "Full analysis text"


class TestImageToImageExecutor:
    """Tests for ImageToImageExecutor."""

    def test_executor_initialization(self):
        """Test ImageToImageExecutor can be initialized."""
        mock_generator = Mock()
        executor = ImageToImageExecutor(mock_generator)
        assert executor.generator == mock_generator

    def test_executor_with_default_prompt(self):
        """Test that default prompt is used when not provided."""
        mock_generator = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.output_path = "/path/to/modified.png"
        mock_result.output_url = None
        mock_result.processing_time = 5.0
        mock_result.cost_estimate = 0.03
        mock_result.model_used = "photon_flash"
        mock_result.metadata = {}
        mock_result.error = None
        mock_generator.generate.return_value = mock_result

        executor = ImageToImageExecutor(mock_generator)

        step = PipelineStep(
            step_type=StepType.IMAGE_TO_IMAGE,
            model="photon_flash",
            params={}  # No prompt provided
        )

        result = executor.execute(
            step=step,
            input_data="/path/to/source.jpg",
            chain_config={"output_dir": "output"}
        )

        assert result["success"] is True
        # Verify default prompt was used
        call_args = mock_generator.generate.call_args
        assert call_args.kwargs.get("prompt") == "modify this image" or \
               call_args[1].get("prompt") == "modify this image"


class TestImageToVideoExecutor:
    """Tests for ImageToVideoExecutor."""

    def test_executor_initialization(self):
        """Test ImageToVideoExecutor can be initialized."""
        mock_generator = Mock()
        executor = ImageToVideoExecutor(mock_generator)
        assert executor.generator == mock_generator

    def test_executor_uses_context_prompt(self):
        """Test that executor uses generated_prompt from context."""
        mock_generator = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.output_path = "/path/to/video.mp4"
        mock_result.output_url = "https://example.com/video.mp4"
        mock_result.processing_time = 120.0
        mock_result.cost_estimate = 0.50
        mock_result.model_used = "veo_3"
        mock_result.metadata = {}
        mock_result.error = None
        mock_generator.generate.return_value = mock_result

        executor = ImageToVideoExecutor(mock_generator)

        step = PipelineStep(
            step_type=StepType.IMAGE_TO_VIDEO,
            model="veo_3",
            params={}
        )

        step_context = {"generated_prompt": "Camera slowly pans across a sunset"}

        result = executor.execute(
            step=step,
            input_data="/path/to/image.jpg",
            chain_config={"output_dir": "output"},
            step_context=step_context
        )

        assert result["success"] is True
        # Verify the generated prompt was used
        call_args = mock_generator.generate.call_args
        input_data_arg = call_args.kwargs.get("input_data") or call_args[1].get("input_data")
        assert input_data_arg["prompt"] == "Camera slowly pans across a sunset"


class TestMergeParams:
    """Tests for _merge_params helper method."""

    def test_merge_params_basic(self):
        """Test basic parameter merging."""
        mock_generator = Mock()
        executor = TextToImageExecutor(mock_generator)

        step_params = {"width": 1024, "height": 768}
        chain_config = {"output_dir": "custom_output"}
        kwargs = {"seed": 42}

        result = executor._merge_params(step_params, chain_config, kwargs)

        assert result["width"] == 1024
        assert result["height"] == 768
        assert result["seed"] == 42
        assert result["output_dir"] == "custom_output"

    def test_merge_params_with_exclusions(self):
        """Test parameter merging with excluded keys."""
        mock_generator = Mock()
        executor = ImageUnderstandingExecutor(mock_generator)

        step_params = {"prompt": "describe this", "format": "json"}
        chain_config = {"output_dir": "output"}
        kwargs = {"prompt": "override", "verbose": True}

        result = executor._merge_params(
            step_params, chain_config, kwargs,
            exclude_keys=["prompt"]
        )

        assert "prompt" not in result
        assert result["format"] == "json"
        assert result["verbose"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
