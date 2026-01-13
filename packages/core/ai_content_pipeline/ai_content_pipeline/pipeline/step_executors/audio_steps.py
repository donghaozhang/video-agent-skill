"""
Audio-related step executors for AI Content Pipeline.

Contains executors for text-to-speech and Replicate MultiTalk.
"""

from typing import Any, Dict, Optional

from .base import BaseStepExecutor


class TextToSpeechExecutor(BaseStepExecutor):
    """Executor for text-to-speech generation steps."""

    def __init__(self, generator):
        """
        Initialize executor with generator.

        Args:
            generator: UnifiedTextToSpeechGenerator instance
        """
        self.generator = generator

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute text-to-speech generation."""
        try:
            # Get text to use - either from text_override param or input
            actual_text = step.params.get("text_override", input_data)

            # Get voice and other parameters
            voice = step.params.get("voice", kwargs.get("voice", "rachel"))
            speed = step.params.get("speed", kwargs.get("speed", 1.0))
            stability = step.params.get("stability", kwargs.get("stability", 0.5))
            similarity_boost = step.params.get(
                "similarity_boost",
                kwargs.get("similarity_boost", 0.8)
            )
            style = step.params.get("style", kwargs.get("style", 0.2))
            output_file = step.params.get("output_file", kwargs.get("output_file", None))

            # Generate speech using the TTS generator
            success, result = self.generator.generate(
                prompt=actual_text,
                model=step.model,
                voice=voice,
                speed=speed,
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                output_file=output_file,
                output_dir=chain_config.get("output_dir", "output")
            )

            if success:
                return {
                    "success": True,
                    "output_path": result["output_file"],
                    "output_url": None,
                    "processing_time": result.get("processing_time", 15),
                    "cost": result.get("cost", 0.05),
                    "model": result["model"],
                    "metadata": {
                        "voice_used": result["voice_used"],
                        "text_length": result["text_length"],
                        "settings": result["settings"]
                    },
                    "error": None
                }
            else:
                return self._create_error_result(
                    result.get("error", "TTS generation failed"),
                    step.model
                )

        except Exception as e:
            return self._create_error_result(
                f"TTS execution failed: {str(e)}",
                step.model
            )


class ReplicateMultiTalkExecutor(BaseStepExecutor):
    """Executor for Replicate MultiTalk video generation steps."""

    def __init__(self, generator):
        """
        Initialize executor with generator.

        Args:
            generator: ReplicateMultiTalkGenerator instance
        """
        self.generator = generator

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute Replicate MultiTalk step."""
        print("Starting MultiTalk video generation...")
        print("This may take 5-10 minutes for high-quality conversational video")

        # Merge step params with kwargs
        params = {
            **step.params,
            **kwargs,
        }

        # Show parameters being used
        people_count = 2 if params.get('second_audio') else 1
        print(f"Generating {people_count}-person conversation")
        print(f"Image: {params.get('image', 'N/A')[:60]}...")

        print("Submitting to Replicate MultiTalk API...")
        result = self.generator.generate(**params)

        if result.success:
            print("MultiTalk generation completed successfully!")
        else:
            print(f"MultiTalk generation failed: {result.error}")

        return {
            "success": result.success,
            "output_path": result.output_path,
            "output_url": result.output_url,
            "processing_time": getattr(result, 'processing_time', 0),
            "cost": getattr(result, 'cost_estimate', 0),
            "model": step.model,
            "metadata": result.metadata,
            "error": result.error
        }
