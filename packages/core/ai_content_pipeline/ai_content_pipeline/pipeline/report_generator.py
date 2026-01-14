"""
Report generator for AI Content Pipeline.

Handles creation and saving of execution reports and intermediate results.
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

from .chain import ContentCreationChain, StepType


class ReportGenerator:
    """
    Generates and saves execution reports for pipeline runs.

    Handles both final execution reports and intermediate progress reports.
    """

    def create_execution_report(
        self,
        chain: ContentCreationChain,
        input_data: str,
        step_results: List[Dict[str, Any]],
        outputs: Dict[str, Any],
        total_cost: float,
        total_time: float,
        success: bool,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create detailed execution report with all step information.

        Args:
            chain: The content creation chain
            input_data: Initial input data
            step_results: List of step execution results
            outputs: Dictionary of outputs by step
            total_cost: Total cost in USD
            total_time: Total processing time in seconds
            success: Whether execution was successful
            error: Error message if failed

        Returns:
            Dictionary containing the full execution report
        """
        enabled_steps = chain.get_enabled_steps()

        # Create step details with status and download links
        step_details = []
        for i, step_result in enumerate(step_results):
            # Safety check for index bounds
            if i >= len(enabled_steps):
                break
            step = enabled_steps[i]

            step_detail = {
                "step_number": i + 1,
                "step_name": f"step_{i+1}_{step.step_type.value}",
                "step_type": step.step_type.value,
                "model": step.model,
                "status": "success" if step_result.get("success", False) else "failed",
                "processing_time": step_result.get("processing_time", 0),
                "cost": step_result.get("cost", 0),
                "output_files": {},
                "download_links": {},
                "metadata": step_result.get("metadata", {}),
                "error": step_result.get("error") if not step_result.get("success", False) else None
            }

            # Add output file information
            if step_result.get("output_path"):
                step_detail["output_files"]["local_path"] = step_result["output_path"]

            if step_result.get("output_url"):
                step_detail["download_links"]["direct_url"] = step_result["output_url"]

            # Add step-specific details
            # Helper to safely get previous step's output URL
            prev_output_url = step_results[i-1].get("output_url") if i > 0 else None

            if step.step_type == StepType.TEXT_TO_IMAGE:
                step_detail["input_prompt"] = input_data
                step_detail["generation_params"] = step.params
            elif step.step_type == StepType.PROMPT_GENERATION:
                step_detail["optimized_prompt"] = step_result.get("extracted_prompt")
                step_detail["full_analysis"] = step_result.get("output_text")
                step_detail["generation_params"] = step.params
                step_detail["input_image_url"] = prev_output_url
            elif step.step_type == StepType.IMAGE_TO_VIDEO:
                step_detail["input_image_url"] = prev_output_url
                step_detail["video_params"] = step.params

            step_details.append(step_detail)

        # Get final outputs for easy access
        final_outputs = {}
        download_links = {}

        for step_name, output in outputs.items():
            if output.get("path"):
                final_outputs[step_name] = output["path"]
            if output.get("url"):
                download_links[step_name] = output["url"]

        # Create comprehensive report
        report = {
            "execution_summary": {
                "chain_name": chain.name,
                "execution_id": f"exec_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "status": "success" if success else "failed",
                "input_data": input_data,
                "input_type": chain.get_initial_input_type(),
                "total_steps": len(enabled_steps),
                "completed_steps": len([s for s in step_results if s.get("success", False)]),
                "total_cost_usd": round(total_cost, 4),
                "total_processing_time_seconds": round(total_time, 2),
                "error": error
            },
            "step_execution_details": step_details,
            "final_outputs": {
                "local_files": final_outputs,
                "download_links": download_links
            },
            "cost_breakdown": {
                "by_step": [
                    {
                        "step": f"{i+1}_{step.step_type.value}",
                        "model": step.model,
                        "cost_usd": step_result.get("cost", 0)
                    }
                    for i, (step, step_result) in enumerate(zip(enabled_steps, step_results))
                ],
                "total_cost_usd": round(total_cost, 4)
            },
            "performance_metrics": {
                "by_step": [
                    {
                        "step": f"{i+1}_{step.step_type.value}",
                        "processing_time_seconds": step_result.get("processing_time", 0),
                        "status": "success" if step_result.get("success", False) else "failed"
                    }
                    for i, (step, step_result) in enumerate(zip(enabled_steps, step_results))
                ],
                "total_time_seconds": round(total_time, 2),
                "average_time_per_step": round(total_time / len(step_results) if step_results else 0, 2)
            },
            "metadata": {
                "chain_config": chain.to_config(),
                "pipeline_version": "1.0.0",
                "models_used": [step.model for step in enabled_steps]
            }
        }

        return report

    def save_execution_report(
        self,
        report: Dict[str, Any],
        chain_config: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save execution report to JSON file.

        Args:
            report: The execution report dictionary
            chain_config: Chain configuration containing output_dir

        Returns:
            Path to saved report file, or None if failed
        """
        try:
            # Create reports directory
            output_dir = Path(chain_config.get("output_dir", "output"))
            reports_dir = output_dir / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            # Generate report filename
            execution_id = report["execution_summary"]["execution_id"]
            chain_name = report["execution_summary"]["chain_name"]
            filename = f"{chain_name}_{execution_id}_report.json"
            report_path = reports_dir / filename

            # Save report
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            return str(report_path)

        except Exception as e:
            print(f"Failed to save execution report: {e}")
            return None

    def create_intermediate_report(
        self,
        chain: ContentCreationChain,
        input_data: str,
        step_results: List[Dict[str, Any]],
        outputs: Dict[str, Any],
        total_cost: float,
        current_step: int,
        total_steps: int
    ) -> Dict[str, Any]:
        """
        Create an intermediate execution report.

        Args:
            chain: The content creation chain
            input_data: Initial input data
            step_results: List of completed step results
            outputs: Dictionary of outputs by step
            total_cost: Running total cost
            current_step: Current step number
            total_steps: Total number of steps

        Returns:
            Dictionary containing the intermediate report
        """
        execution_id = f"intermediate_{int(time.time())}"
        enabled_steps = chain.get_enabled_steps()

        return {
            "report_type": "intermediate",
            "execution_summary": {
                "chain_name": chain.name,
                "execution_id": execution_id,
                "timestamp": datetime.now().isoformat(),
                "status": "in_progress",
                "input_data": input_data,
                "input_type": chain.get_initial_input_type(),
                "total_steps": total_steps,
                "completed_steps": current_step,
                "total_cost_usd": total_cost,
                "current_step": current_step
            },
            "completed_steps": [
                {
                    "step_number": i + 1,
                    "step_type": enabled_steps[i].step_type.value,
                    "model": enabled_steps[i].model,
                    "status": "completed" if result.get("success") else "failed",
                    "cost": result.get("cost", 0),
                    "output": {
                        "path": result.get("output_path"),
                        "url": result.get("output_url"),
                        "text": result.get("output_text"),
                        # Add prompt generation specific fields
                        **({"optimized_prompt": result.get("extracted_prompt"),
                            "full_analysis": result.get("output_text")}
                           if enabled_steps[i].step_type == StepType.PROMPT_GENERATION else {})
                    }
                }
                for i, result in enumerate(step_results)
            ],
            "intermediate_outputs": outputs,
            "metadata": {
                "chain_config": chain.to_config(),
                "save_intermediates": chain.save_intermediates
            }
        }

    def save_intermediate_report(
        self,
        report: Dict[str, Any],
        config: Dict[str, Any],
        step_number: int
    ) -> Optional[str]:
        """
        Save intermediate report to file.

        Args:
            report: The intermediate report dictionary
            config: Chain configuration containing output_dir
            step_number: Current step number

        Returns:
            Path to saved report file, or None if failed
        """
        try:
            # Create reports directory
            output_dir = Path(config.get("output_dir", "output"))
            reports_dir = output_dir / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with step number
            chain_name = report["execution_summary"]["chain_name"]
            timestamp = int(time.time())
            filename = f"{chain_name}_step{step_number}_intermediate_{timestamp}.json"
            filepath = reports_dir / filename

            # Save report
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            return str(filepath)
        except Exception as e:
            print(f"Failed to save intermediate report: {str(e)}")
            return None

    def download_intermediate_image(
        self,
        image_url: str,
        step_name: str,
        config: Dict[str, Any]
    ) -> Optional[str]:
        """
        Download intermediate image for save_intermediates functionality.

        Args:
            image_url: URL of the image to download
            step_name: Name of the step (e.g., "step_1_text_to_image")
            config: Chain configuration containing output_dir

        Returns:
            Local file path if successful, None if failed
        """
        try:
            # Create intermediates directory
            output_dir = Path(config.get("output_dir", "output"))
            intermediates_dir = output_dir / "intermediates"
            intermediates_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename - extract extension from URL path (strip query params)
            timestamp = int(time.time())
            url_path = image_url.split("?")[0]  # Remove query parameters
            file_extension = Path(url_path).suffix or ".png"
            # Sanitize extension to only allow known image types
            allowed_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
            if file_extension.lower() not in allowed_extensions:
                file_extension = ".png"
            filename = f"{step_name}_{timestamp}{file_extension}"
            filepath = intermediates_dir / filename

            # Download image
            print(f"Downloading intermediate image: {step_name}")
            response = requests.get(image_url, timeout=30, stream=True)
            response.raise_for_status()

            # Save to file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Intermediate image saved: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"Failed to download intermediate image: {str(e)}")
            return None
