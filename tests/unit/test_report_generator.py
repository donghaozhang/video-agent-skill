"""
Unit tests for report generator module.

Tests the ReportGenerator class for execution and intermediate reports.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.core.ai_content_pipeline.ai_content_pipeline.pipeline.report_generator import (
    ReportGenerator,
)
from packages.core.ai_content_pipeline.ai_content_pipeline.pipeline.chain import (
    ContentCreationChain,
    PipelineStep,
    StepType,
)


class TestReportGenerator:
    """Tests for ReportGenerator class."""

    @pytest.fixture
    def report_generator(self):
        """Create a ReportGenerator instance."""
        return ReportGenerator()

    @pytest.fixture
    def sample_chain(self):
        """Create a sample ContentCreationChain for testing."""
        steps = [
            PipelineStep(
                step_type=StepType.TEXT_TO_IMAGE,
                model="flux_dev",
                params={"width": 1024}
            ),
            PipelineStep(
                step_type=StepType.IMAGE_TO_VIDEO,
                model="veo_3",
                params={"duration": 5}
            ),
        ]
        return ContentCreationChain(
            name="test_chain",
            steps=steps,
            config={"output_dir": "output"}
        )

    @pytest.fixture
    def sample_step_results(self):
        """Create sample step results."""
        return [
            {
                "success": True,
                "output_path": "/path/to/image.png",
                "output_url": "https://example.com/image.png",
                "processing_time": 10.5,
                "cost": 0.05,
                "metadata": {"seed": 12345}
            },
            {
                "success": True,
                "output_path": "/path/to/video.mp4",
                "output_url": "https://example.com/video.mp4",
                "processing_time": 120.0,
                "cost": 0.50,
                "metadata": {}
            },
        ]

    def test_create_execution_report_success(
        self, report_generator, sample_chain, sample_step_results
    ):
        """Test creating a successful execution report."""
        outputs = {
            "step_1_text_to_image": {
                "path": "/path/to/image.png",
                "url": "https://example.com/image.png"
            },
            "step_2_image_to_video": {
                "path": "/path/to/video.mp4",
                "url": "https://example.com/video.mp4"
            },
        }

        report = report_generator.create_execution_report(
            chain=sample_chain,
            input_data="A beautiful sunset",
            step_results=sample_step_results,
            outputs=outputs,
            total_cost=0.55,
            total_time=130.5,
            success=True
        )

        # Verify report structure
        assert "execution_summary" in report
        assert "step_execution_details" in report
        assert "final_outputs" in report
        assert "cost_breakdown" in report
        assert "performance_metrics" in report
        assert "metadata" in report

        # Verify execution summary
        summary = report["execution_summary"]
        assert summary["chain_name"] == "test_chain"
        assert summary["status"] == "success"
        assert summary["total_steps"] == 2
        assert summary["completed_steps"] == 2
        assert summary["total_cost_usd"] == 0.55

    def test_create_execution_report_failure(
        self, report_generator, sample_chain
    ):
        """Test creating a failed execution report."""
        step_results = [
            {
                "success": True,
                "output_path": "/path/to/image.png",
                "processing_time": 10.5,
                "cost": 0.05,
            },
            {
                "success": False,
                "error": "API timeout",
                "processing_time": 30.0,
                "cost": 0,
            },
        ]

        report = report_generator.create_execution_report(
            chain=sample_chain,
            input_data="A prompt",
            step_results=step_results,
            outputs={},
            total_cost=0.05,
            total_time=40.5,
            success=False,
            error="Step 2 failed: API timeout"
        )

        summary = report["execution_summary"]
        assert summary["status"] == "failed"
        assert summary["error"] == "Step 2 failed: API timeout"
        assert summary["completed_steps"] == 1

    def test_create_intermediate_report(
        self, report_generator, sample_chain
    ):
        """Test creating an intermediate progress report."""
        step_results = [
            {
                "success": True,
                "output_path": "/path/to/image.png",
                "cost": 0.05,
            },
        ]

        outputs = {
            "step_1_text_to_image": {
                "path": "/path/to/image.png",
            },
        }

        report = report_generator.create_intermediate_report(
            chain=sample_chain,
            input_data="A prompt",
            step_results=step_results,
            outputs=outputs,
            total_cost=0.05,
            current_step=1,
            total_steps=2
        )

        assert report["report_type"] == "intermediate"
        assert report["execution_summary"]["status"] == "in_progress"
        assert report["execution_summary"]["current_step"] == 1
        assert report["execution_summary"]["total_steps"] == 2
        assert len(report["completed_steps"]) == 1

    def test_save_execution_report(self, report_generator):
        """Test saving execution report to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = {
                "execution_summary": {
                    "execution_id": "exec_123456",
                    "chain_name": "test_chain",
                    "status": "success"
                }
            }

            chain_config = {"output_dir": tmpdir}

            result_path = report_generator.save_execution_report(report, chain_config)

            assert result_path is not None
            assert Path(result_path).exists()

            # Verify content
            with open(result_path) as f:
                saved_report = json.load(f)
            assert saved_report["execution_summary"]["chain_name"] == "test_chain"

    def test_save_execution_report_creates_directory(self, report_generator):
        """Test that save_execution_report creates reports directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = {
                "execution_summary": {
                    "execution_id": "exec_789",
                    "chain_name": "test_chain"
                }
            }

            chain_config = {"output_dir": tmpdir}
            reports_dir = Path(tmpdir) / "reports"

            assert not reports_dir.exists()

            result_path = report_generator.save_execution_report(report, chain_config)

            assert reports_dir.exists()
            assert result_path is not None

    def test_save_intermediate_report(self, report_generator):
        """Test saving intermediate report to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = {
                "report_type": "intermediate",
                "execution_summary": {
                    "chain_name": "test_chain",
                    "current_step": 1
                }
            }

            config = {"output_dir": tmpdir}

            result_path = report_generator.save_intermediate_report(
                report, config, step_number=1
            )

            assert result_path is not None
            assert Path(result_path).exists()
            assert "step1" in result_path
            assert "intermediate" in result_path

    def test_cost_breakdown_calculation(
        self, report_generator, sample_chain, sample_step_results
    ):
        """Test that cost breakdown is correctly calculated."""
        report = report_generator.create_execution_report(
            chain=sample_chain,
            input_data="test",
            step_results=sample_step_results,
            outputs={},
            total_cost=0.55,
            total_time=130.5,
            success=True
        )

        cost_breakdown = report["cost_breakdown"]
        assert cost_breakdown["total_cost_usd"] == 0.55
        assert len(cost_breakdown["by_step"]) == 2
        assert cost_breakdown["by_step"][0]["cost_usd"] == 0.05
        assert cost_breakdown["by_step"][1]["cost_usd"] == 0.50

    def test_performance_metrics_calculation(
        self, report_generator, sample_chain, sample_step_results
    ):
        """Test that performance metrics are correctly calculated."""
        report = report_generator.create_execution_report(
            chain=sample_chain,
            input_data="test",
            step_results=sample_step_results,
            outputs={},
            total_cost=0.55,
            total_time=130.5,
            success=True
        )

        metrics = report["performance_metrics"]
        assert metrics["total_time_seconds"] == 130.5
        assert len(metrics["by_step"]) == 2
        assert metrics["by_step"][0]["processing_time_seconds"] == 10.5
        assert metrics["by_step"][1]["processing_time_seconds"] == 120.0


class TestDownloadIntermediateImage:
    """Tests for download_intermediate_image method."""

    def test_download_creates_directory(self):
        """Test that download creates intermediates directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_generator = ReportGenerator()
            config = {"output_dir": tmpdir}
            intermediates_dir = Path(tmpdir) / "intermediates"

            assert not intermediates_dir.exists()

            # Mock the requests.get to avoid actual HTTP call
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.iter_content.return_value = [b"fake image data"]
                mock_response.raise_for_status = Mock()
                mock_get.return_value = mock_response

                result = report_generator.download_intermediate_image(
                    image_url="https://example.com/image.png",
                    step_name="step_1_text_to_image",
                    config=config,
                    step_number=1
                )

            assert intermediates_dir.exists()

    def test_download_handles_failure(self):
        """Test that download handles network errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_generator = ReportGenerator()
            config = {"output_dir": tmpdir}

            with patch('requests.get') as mock_get:
                mock_get.side_effect = Exception("Network error")

                result = report_generator.download_intermediate_image(
                    image_url="https://example.com/image.png",
                    step_name="step_1_text_to_image",
                    config=config,
                    step_number=1
                )

            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
