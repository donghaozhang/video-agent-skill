"""
Chain executor for AI Content Pipeline.

Handles the sequential execution of pipeline steps with file management.
This module orchestrates step execution using specialized step executors.
"""

import time
from typing import Any, Dict

from .chain import ContentCreationChain, ChainResult, PipelineStep, StepType
from .report_generator import ReportGenerator
from .step_executors import (
    TextToImageExecutor,
    TextToVideoExecutor,
    ImageUnderstandingExecutor,
    PromptGenerationExecutor,
    ImageToImageExecutor,
    ImageToVideoExecutor,
    AddAudioExecutor,
    UpscaleVideoExecutor,
    GenerateSubtitlesExecutor,
    TextToSpeechExecutor,
    ReplicateMultiTalkExecutor,
    SplitImageExecutor,
    UpscaleImageExecutor,
    ConcatVideosExecutor,
)
from ..models.text_to_image import UnifiedTextToImageGenerator
from ..models.image_understanding import UnifiedImageUnderstandingGenerator
from ..models.prompt_generation import UnifiedPromptGenerator
from ..models.image_to_image import UnifiedImageToImageGenerator
from ..models.image_to_video import UnifiedImageToVideoGenerator
from ..models.text_to_speech import UnifiedTextToSpeechGenerator
from ..models.avatar import ReplicateMultiTalkGenerator
from ..utils.file_manager import FileManager


class ChainExecutor:
    """
    Executes content creation chains step by step.

    Manages file flow between steps and handles errors gracefully.
    Uses specialized step executors for each step type.
    """

    def __init__(self, file_manager: FileManager):
        """
        Initialize chain executor.

        Args:
            file_manager: FileManager instance for handling files
        """
        self.file_manager = file_manager
        self.report_generator = ReportGenerator()

        # Initialize model generators
        text_to_image = UnifiedTextToImageGenerator()
        image_understanding = UnifiedImageUnderstandingGenerator()
        prompt_generation = UnifiedPromptGenerator()
        image_to_image = UnifiedImageToImageGenerator()
        image_to_video = UnifiedImageToVideoGenerator()
        text_to_speech = UnifiedTextToSpeechGenerator()
        replicate_multitalk = ReplicateMultiTalkGenerator(file_manager=file_manager)

        # Initialize step executors
        self._executors = {
            StepType.TEXT_TO_IMAGE: TextToImageExecutor(text_to_image),
            StepType.TEXT_TO_VIDEO: TextToVideoExecutor(),
            StepType.IMAGE_UNDERSTANDING: ImageUnderstandingExecutor(image_understanding),
            StepType.PROMPT_GENERATION: PromptGenerationExecutor(prompt_generation),
            StepType.IMAGE_TO_IMAGE: ImageToImageExecutor(image_to_image),
            StepType.IMAGE_TO_VIDEO: ImageToVideoExecutor(image_to_video),
            StepType.TEXT_TO_SPEECH: TextToSpeechExecutor(text_to_speech),
            StepType.ADD_AUDIO: AddAudioExecutor(),
            StepType.UPSCALE_VIDEO: UpscaleVideoExecutor(),
            StepType.UPSCALE_IMAGE: UpscaleImageExecutor(),
            StepType.SPLIT_IMAGE: SplitImageExecutor(),
            StepType.GENERATE_SUBTITLES: GenerateSubtitlesExecutor(),
            StepType.REPLICATE_MULTITALK: ReplicateMultiTalkExecutor(replicate_multitalk),
            StepType.CONCAT_VIDEOS: ConcatVideosExecutor(),
        }

        # Optional parallel execution support
        self._parallel_extension = None
        self._try_load_parallel_extension()

    def _try_load_parallel_extension(self):
        """Try to load parallel extension if available."""
        try:
            from .parallel_extension import ParallelExtension
            self._parallel_extension = ParallelExtension(self)
            if self._parallel_extension.enabled:
                print("Parallel execution extension loaded and enabled")
            else:
                print("Parallel execution extension loaded but disabled (set PIPELINE_PARALLEL_ENABLED=true to enable)")
        except ImportError:
            print("Parallel execution extension not available")

    def execute(
        self,
        chain: ContentCreationChain,
        input_data: str,
        **kwargs
    ) -> ChainResult:
        """
        Execute a complete content creation chain.

        Args:
            chain: ContentCreationChain to execute
            input_data: Initial input data (text, image path, or video path)
            **kwargs: Additional execution parameters

        Returns:
            ChainResult with execution results
        """
        start_time = time.time()
        step_results = []
        outputs = {}
        total_cost = 0.0
        current_data = input_data
        current_type = chain.get_initial_input_type()
        step_context = {}

        enabled_steps = chain.get_enabled_steps()

        print(f"Starting chain execution: {len(enabled_steps)} steps")

        try:
            for i, step in enumerate(enabled_steps):
                print(f"\nStep {i+1}/{len(enabled_steps)}: {step.step_type.value} ({step.model})")

                # Check if this is a parallel step and extension is available
                if (self._parallel_extension and
                    self._parallel_extension.can_execute_parallel(step)):
                    step_result = self._parallel_extension.execute_parallel_group(
                        step=step,
                        input_data=current_data,
                        input_type=current_type,
                        chain_config=chain.config,
                        step_context=step_context
                    )
                else:
                    step_result = self._execute_step(
                        step=step,
                        input_data=current_data,
                        input_type=current_type,
                        chain_config=chain.config,
                        step_context=step_context,
                        **kwargs
                    )

                step_results.append(step_result)
                total_cost += step_result.get("cost", 0.0)

                if not step_result.get("success", False):
                    return self._handle_failure(
                        chain, input_data, step_results, outputs,
                        total_cost, start_time, i, step_result.get("error", "Unknown error")
                    )

                # Update current data for next step
                self._update_step_context(step, step_result, step_context)
                current_data, current_type = self._get_next_step_input(
                    step, step_result, current_data, current_type
                )

                # Store intermediate output
                step_name = f"step_{i+1}_{step.step_type.value}"
                outputs[step_name] = self._create_step_output(step, step_result)

                # Save intermediate results if enabled
                if chain.save_intermediates:
                    self._save_intermediate_results(
                        chain, input_data, step_results, outputs,
                        total_cost, i, step_result
                    )

                print(f"Step completed in {step_result.get('processing_time', 0):.1f}s")

            # Chain completed successfully
            return self._handle_success(
                chain, input_data, step_results, outputs,
                total_cost, start_time, enabled_steps
            )

        except Exception as e:
            return self._handle_exception(
                chain, input_data, step_results, outputs,
                total_cost, start_time, str(e)
            )

    def _execute_step(
        self,
        step: PipelineStep,
        input_data: Any,
        input_type: str,
        chain_config: Dict[str, Any],
        step_context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a single pipeline step.

        Args:
            step: PipelineStep to execute
            input_data: Input data for the step
            input_type: Type of input data
            chain_config: Chain configuration
            step_context: Context from previous steps
            **kwargs: Additional parameters

        Returns:
            Dictionary with step execution results
        """
        try:
            if step_context is None:
                step_context = {}

            executor = self._executors.get(step.step_type)
            if executor:
                return executor.execute(
                    step=step,
                    input_data=input_data,
                    chain_config=chain_config,
                    step_context=step_context,
                    **kwargs
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported step type: {step.step_type.value}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Step execution failed: {str(e)}"
            }

    def _update_step_context(
        self,
        step: PipelineStep,
        step_result: Dict[str, Any],
        step_context: Dict[str, Any]
    ):
        """Update step context with results from executed step."""
        if step.step_type == StepType.PROMPT_GENERATION:
            step_context["generated_prompt"] = (
                step_result.get("extracted_prompt") or
                step_result.get("output_text")
            )
            print("Stored generated prompt, keeping image data for next step")

    def _get_next_step_input(
        self,
        step: PipelineStep,
        step_result: Dict[str, Any],
        current_data: Any,
        current_type: str
    ) -> tuple:
        """Get input data and type for the next step."""
        if step.step_type == StepType.PROMPT_GENERATION:
            # Keep the image data for the next step
            return current_data, current_type

        # Normal data flow for other steps
        # For split_image and image_to_video, pass the list of paths so next step can process all
        if step.step_type == StepType.SPLIT_IMAGE and step_result.get("output_paths"):
            new_data = step_result.get("output_paths")
        elif step.step_type == StepType.IMAGE_TO_VIDEO and step_result.get("output_paths"):
            # Pass list of video paths for concat_videos step
            new_data = step_result.get("output_paths")
        else:
            new_data = (
                step_result.get("output_path") or
                step_result.get("output_url") or
                step_result.get("output_text")
            )
        new_type = self._get_step_output_type(step.step_type)
        return new_data, new_type

    def _get_step_output_type(self, step_type: StepType) -> str:
        """Get the output type for a step."""
        output_types = {
            StepType.TEXT_TO_IMAGE: "image",
            StepType.TEXT_TO_VIDEO: "video",
            StepType.IMAGE_UNDERSTANDING: "text",
            StepType.PROMPT_GENERATION: "text",
            StepType.IMAGE_TO_IMAGE: "image",
            StepType.IMAGE_TO_VIDEO: "video",
            StepType.TEXT_TO_SPEECH: "audio",
            StepType.ADD_AUDIO: "video",
            StepType.UPSCALE_VIDEO: "video",
            StepType.UPSCALE_IMAGE: "image",
            StepType.SPLIT_IMAGE: "images",
            StepType.GENERATE_SUBTITLES: "video",
            StepType.REPLICATE_MULTITALK: "video",
            StepType.CONCAT_VIDEOS: "video",
        }
        return output_types.get(step_type, "unknown")

    def _create_step_output(
        self,
        step: PipelineStep,
        step_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create output dictionary for a completed step."""
        output = {
            "path": step_result.get("output_path"),
            "url": step_result.get("output_url"),
            "text": step_result.get("output_text"),
            "model": step.model,
            "metadata": step_result.get("metadata", {})
        }

        if step.step_type == StepType.PROMPT_GENERATION:
            output["optimized_prompt"] = step_result.get("extracted_prompt")
            output["full_analysis"] = step_result.get("output_text")

        return output

    def _save_intermediate_results(
        self,
        chain: ContentCreationChain,
        input_data: str,
        step_results: list,
        outputs: dict,
        total_cost: float,
        step_index: int,
        step_result: Dict[str, Any]
    ):
        """Save intermediate results for the current step."""
        step_name = f"step_{step_index+1}_{chain.get_enabled_steps()[step_index].step_type.value}"

        # Download intermediate image if only URL is available
        if step_result.get("output_url") and not step_result.get("output_path"):
            local_path = self.report_generator.download_intermediate_image(
                image_url=step_result["output_url"],
                step_name=step_name,
                config=chain.config
            )
            if local_path:
                step_result["output_path"] = local_path
                outputs[step_name]["path"] = local_path

        intermediate_report = self.report_generator.create_intermediate_report(
            chain=chain,
            input_data=input_data,
            step_results=step_results[:step_index+1],
            outputs=outputs,
            total_cost=total_cost,
            current_step=step_index+1,
            total_steps=len(chain.get_enabled_steps())
        )

        intermediate_path = self.report_generator.save_intermediate_report(
            intermediate_report,
            chain.config,
            step_number=step_index+1
        )
        if intermediate_path:
            print(f"Intermediate results saved: {intermediate_path}")

    def _handle_failure(
        self,
        chain: ContentCreationChain,
        input_data: str,
        step_results: list,
        outputs: dict,
        total_cost: float,
        start_time: float,
        step_index: int,
        error_msg: str
    ) -> ChainResult:
        """Handle step failure and return ChainResult."""
        print(f"Step failed: {error_msg}")
        total_time = time.time() - start_time

        execution_report = self.report_generator.create_execution_report(
            chain=chain,
            input_data=input_data,
            step_results=step_results,
            outputs=outputs,
            total_cost=total_cost,
            total_time=total_time,
            success=False,
            error=f"Step {step_index+1} failed: {error_msg}"
        )

        report_path = self.report_generator.save_execution_report(execution_report, chain.config)
        if report_path:
            print(f"Failure report saved: {report_path}")

        return ChainResult(
            success=False,
            steps_completed=step_index,
            total_steps=len(chain.get_enabled_steps()),
            total_cost=total_cost,
            total_time=total_time,
            outputs=outputs,
            error=f"Step {step_index+1} failed: {error_msg}",
            step_results=step_results
        )

    def _handle_success(
        self,
        chain: ContentCreationChain,
        input_data: str,
        step_results: list,
        outputs: dict,
        total_cost: float,
        start_time: float,
        enabled_steps: list
    ) -> ChainResult:
        """Handle successful chain completion and return ChainResult."""
        total_time = time.time() - start_time

        print(f"\nChain completed successfully!")
        print(f"Total time: {total_time:.1f}s")
        print(f"Total cost: ${total_cost:.3f}")

        execution_report = self.report_generator.create_execution_report(
            chain=chain,
            input_data=input_data,
            step_results=step_results,
            outputs=outputs,
            total_cost=total_cost,
            total_time=total_time,
            success=True
        )

        report_path = self.report_generator.save_execution_report(execution_report, chain.config)
        if report_path:
            print(f"Execution report saved: {report_path}")

        return ChainResult(
            success=True,
            steps_completed=len(enabled_steps),
            total_steps=len(enabled_steps),
            total_cost=total_cost,
            total_time=total_time,
            outputs=outputs,
            step_results=step_results
        )

    def _handle_exception(
        self,
        chain: ContentCreationChain,
        input_data: str,
        step_results: list,
        outputs: dict,
        total_cost: float,
        start_time: float,
        error_msg: str
    ) -> ChainResult:
        """Handle unexpected exception and return ChainResult."""
        print(f"Chain execution failed: {error_msg}")
        total_time = time.time() - start_time

        execution_report = self.report_generator.create_execution_report(
            chain=chain,
            input_data=input_data,
            step_results=step_results,
            outputs=outputs,
            total_cost=total_cost,
            total_time=total_time,
            success=False,
            error=f"Execution error: {error_msg}"
        )

        report_path = self.report_generator.save_execution_report(execution_report, chain.config)
        if report_path:
            print(f"Error report saved: {report_path}")

        return ChainResult(
            success=False,
            steps_completed=len(step_results),
            total_steps=len(chain.get_enabled_steps()),
            total_cost=total_cost,
            total_time=total_time,
            outputs=outputs,
            error=f"Execution error: {error_msg}",
            step_results=step_results
        )
