"""
Unit tests for parallel image-to-video processing.

Tests the ImageToVideoExecutor's parallel processing capabilities.

File: tests/test_parallel_video_generation.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass
from typing import Optional

# Add package path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages/core/ai_content_pipeline"))


@dataclass
class MockGenerationResult:
    """Mock result from video generation."""
    success: bool
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    processing_time: float = 1.0
    cost_estimate: float = 0.10
    model_used: str = "test_model"
    metadata: dict = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MockStep:
    """Mock pipeline step."""

    def __init__(self, model: str = "test_model", params: dict = None):
        self.model = model
        self.params = params or {}


class TestParallelFlagDetection:
    """Test parallel flag triggers correct processing path."""

    def test_parallel_true_triggers_parallel_processing(self):
        """Verify parallel=true triggers _process_multiple_images_parallel."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        # Mock generator
        mock_generator = Mock()
        mock_generator.generate.return_value = MockGenerationResult(
            success=True,
            output_path="/output/video_1.mp4",
            output_url="https://example.com/video_1.mp4"
        )

        executor = ImageToVideoExecutor(mock_generator)

        # Create step with parallel=true
        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": True, "max_workers": 2}
        )

        # Mock the parallel method to verify it gets called
        with patch.object(executor, '_process_multiple_images_parallel') as mock_parallel:
            mock_parallel.return_value = {"success": True, "output_paths": []}

            executor.execute(
                step=step,
                input_data=["/path/img1.png", "/path/img2.png"],
                chain_config={},
            )

            mock_parallel.assert_called_once()

    def test_parallel_false_uses_sequential(self):
        """Verify parallel=false uses sequential processing."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        mock_generator = Mock()
        mock_generator.generate.return_value = MockGenerationResult(
            success=True,
            output_path="/output/video_1.mp4"
        )

        executor = ImageToVideoExecutor(mock_generator)

        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": False}
        )

        # Mock the sequential method
        with patch.object(executor, '_process_multiple_images') as mock_sequential:
            mock_sequential.return_value = {"success": True, "output_paths": []}

            executor.execute(
                step=step,
                input_data=["/path/img1.png", "/path/img2.png"],
                chain_config={},
            )

            mock_sequential.assert_called_once()

    def test_no_parallel_flag_defaults_to_sequential(self):
        """Verify missing parallel flag defaults to sequential processing."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        mock_generator = Mock()
        mock_generator.generate.return_value = MockGenerationResult(
            success=True,
            output_path="/output/video_1.mp4"
        )

        executor = ImageToVideoExecutor(mock_generator)

        # No parallel flag in params
        step = MockStep(model="kling_2_6_pro", params={})

        with patch.object(executor, '_process_multiple_images') as mock_sequential:
            mock_sequential.return_value = {"success": True, "output_paths": []}

            executor.execute(
                step=step,
                input_data=["/path/img1.png", "/path/img2.png"],
                chain_config={},
            )

            mock_sequential.assert_called_once()


class TestMaxWorkersParameter:
    """Test max_workers configuration."""

    def test_default_max_workers_is_4(self):
        """Verify default max_workers is 4 when not specified."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        mock_generator = Mock()
        mock_generator.generate.return_value = MockGenerationResult(
            success=True,
            output_path="/output/video.mp4",
            output_url="https://example.com/video.mp4"
        )

        executor = ImageToVideoExecutor(mock_generator)

        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": True}  # No max_workers specified
        )

        result = executor._process_multiple_images_parallel(
            step=step,
            image_paths=["/path/img1.png", "/path/img2.png"],
            default_prompt="Test prompt",
            params={}
        )

        # Check metadata shows default max_workers
        assert result["metadata"]["max_workers"] == 4

    def test_custom_max_workers_respected(self):
        """Verify custom max_workers is used."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        mock_generator = Mock()
        mock_generator.generate.return_value = MockGenerationResult(
            success=True,
            output_path="/output/video.mp4",
            output_url="https://example.com/video.mp4"
        )

        executor = ImageToVideoExecutor(mock_generator)

        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": True, "max_workers": 2}
        )

        result = executor._process_multiple_images_parallel(
            step=step,
            image_paths=["/path/img1.png", "/path/img2.png"],
            default_prompt="Test prompt",
            params={}
        )

        assert result["metadata"]["max_workers"] == 2


class TestIndividualPromptsParallel:
    """Test per-image prompts work in parallel mode."""

    def test_individual_prompts_applied_correctly(self):
        """Verify each image gets its correct prompt in parallel mode."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        # Track which prompts are used
        captured_prompts = []

        def mock_generate(input_data, model, **kwargs):
            captured_prompts.append(input_data["prompt"])
            return MockGenerationResult(
                success=True,
                output_path=f"/output/video_{len(captured_prompts)}.mp4",
                output_url=f"https://example.com/video_{len(captured_prompts)}.mp4"
            )

        mock_generator = Mock()
        mock_generator.generate.side_effect = mock_generate

        executor = ImageToVideoExecutor(mock_generator)

        prompts = ["Prompt for image 1", "Prompt for image 2", "Prompt for image 3"]
        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": True, "max_workers": 3, "prompts": prompts}
        )

        executor._process_multiple_images_parallel(
            step=step,
            image_paths=["/path/img1.png", "/path/img2.png", "/path/img3.png"],
            default_prompt="Default prompt",
            params={}
        )

        # All prompts should be captured (order may vary due to parallel execution)
        assert set(captured_prompts) == set(prompts)

    def test_fallback_to_default_prompt(self):
        """Verify default prompt used when prompts array is shorter than images."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        captured_prompts = []

        def mock_generate(input_data, model, **kwargs):
            captured_prompts.append(input_data["prompt"])
            return MockGenerationResult(
                success=True,
                output_path=f"/output/video_{len(captured_prompts)}.mp4",
                output_url=f"https://example.com/video_{len(captured_prompts)}.mp4"
            )

        mock_generator = Mock()
        mock_generator.generate.side_effect = mock_generate

        executor = ImageToVideoExecutor(mock_generator)

        # Only 2 prompts for 4 images
        prompts = ["Prompt 1", "Prompt 2"]
        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": True, "max_workers": 4, "prompts": prompts}
        )

        executor._process_multiple_images_parallel(
            step=step,
            image_paths=["/img1.png", "/img2.png", "/img3.png", "/img4.png"],
            default_prompt="Default prompt",
            params={}
        )

        # Should have 2 specific prompts + 2 default prompts
        assert "Prompt 1" in captured_prompts
        assert "Prompt 2" in captured_prompts
        assert captured_prompts.count("Default prompt") == 2


class TestParallelErrorHandling:
    """Test error handling in parallel mode."""

    def test_single_failure_doesnt_crash_others(self):
        """Verify errors in one thread don't crash others."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        def mock_generate(input_data, model, **kwargs):
            # Fail deterministically on img2 (thread-safe: based on input, not call order)
            if "img2" in input_data.get("image_path", ""):
                return MockGenerationResult(
                    success=False,
                    error="Simulated failure"
                )
            return MockGenerationResult(
                success=True,
                output_path=f"/output/{Path(input_data['image_path']).stem}.mp4",
                output_url=f"https://example.com/{Path(input_data['image_path']).stem}.mp4"
            )

        mock_generator = Mock()
        mock_generator.generate.side_effect = mock_generate

        executor = ImageToVideoExecutor(mock_generator)

        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": True, "max_workers": 3}
        )

        result = executor._process_multiple_images_parallel(
            step=step,
            image_paths=["/img1.png", "/img2.png", "/img3.png"],
            default_prompt="Test",
            params={}
        )

        # Should still succeed overall with 2 out of 3
        assert result["success"] is True
        assert len(result["output_paths"]) == 2
        assert result["error"] is not None
        assert "Image 2" in result["error"]

    def test_exception_in_thread_handled(self):
        """Verify exceptions in threads are caught and reported."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        call_count = [0]

        def mock_generate(input_data, model, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Thread exception")
            return MockGenerationResult(
                success=True,
                output_path=f"/output/video_{call_count[0]}.mp4",
                output_url=f"https://example.com/video_{call_count[0]}.mp4"
            )

        mock_generator = Mock()
        mock_generator.generate.side_effect = mock_generate

        executor = ImageToVideoExecutor(mock_generator)

        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": True, "max_workers": 2}
        )

        result = executor._process_multiple_images_parallel(
            step=step,
            image_paths=["/img1.png", "/img2.png"],
            default_prompt="Test",
            params={}
        )

        # Should still produce one video
        assert result["success"] is True
        assert len(result["output_paths"]) == 1
        assert "Thread exception" in result["error"]


class TestResultOrdering:
    """Test results are collected in correct order."""

    def test_results_maintain_original_order(self):
        """Verify output_paths maintains original image order."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        def mock_generate(input_data, model, **kwargs):
            # Extract image index from path
            img_path = input_data["image_path"]
            idx = img_path.split("_")[-1].replace(".png", "")
            return MockGenerationResult(
                success=True,
                output_path=f"/output/video_{idx}.mp4",
                output_url=f"https://example.com/video_{idx}.mp4"
            )

        mock_generator = Mock()
        mock_generator.generate.side_effect = mock_generate

        executor = ImageToVideoExecutor(mock_generator)

        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": True, "max_workers": 4}
        )

        result = executor._process_multiple_images_parallel(
            step=step,
            image_paths=["/img_1.png", "/img_2.png", "/img_3.png", "/img_4.png"],
            default_prompt="Test",
            params={}
        )

        # Videos should be in order 1, 2, 3, 4
        assert result["output_paths"] == [
            "/output/video_1.mp4",
            "/output/video_2.mp4",
            "/output/video_3.mp4",
            "/output/video_4.mp4"
        ]


class TestParallelMetadata:
    """Test metadata is correctly populated in parallel mode."""

    def test_parallel_metadata_included(self):
        """Verify parallel-specific metadata is in result."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        mock_generator = Mock()
        mock_generator.generate.return_value = MockGenerationResult(
            success=True,
            output_path="/output/video.mp4",
            output_url="https://example.com/video.mp4"
        )

        executor = ImageToVideoExecutor(mock_generator)

        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": True, "max_workers": 3}
        )

        result = executor._process_multiple_images_parallel(
            step=step,
            image_paths=["/img1.png", "/img2.png"],
            default_prompt="Test",
            params={}
        )

        assert result["metadata"]["parallel"] is True
        assert result["metadata"]["max_workers"] == 3
        assert result["metadata"]["total_images"] == 2
        assert result["metadata"]["videos_generated"] == 2

    def test_cost_aggregated_correctly(self):
        """Verify costs from all videos are summed."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import (
            ImageToVideoExecutor
        )

        mock_generator = Mock()
        mock_generator.generate.return_value = MockGenerationResult(
            success=True,
            output_path="/output/video.mp4",
            output_url="https://example.com/video.mp4",
            cost_estimate=0.25
        )

        executor = ImageToVideoExecutor(mock_generator)

        step = MockStep(
            model="kling_2_6_pro",
            params={"parallel": True, "max_workers": 4}
        )

        result = executor._process_multiple_images_parallel(
            step=step,
            image_paths=["/img1.png", "/img2.png", "/img3.png", "/img4.png"],
            default_prompt="Test",
            params={}
        )

        # 4 videos * $0.25 = $1.00
        assert result["cost"] == 1.00


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
