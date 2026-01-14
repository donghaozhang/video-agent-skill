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
        import time

        print("Starting MultiTalk video generation...")
        print("This may take 5-10 minutes for high-quality conversational video")

        try:
            # Merge step params with kwargs
            params = {
                **step.params,
                **kwargs,
            }

            # Map parameter names to what the generator expects
            # Generator uses: image_url, first_audio_url, second_audio_url
            # Config may use: image, first_audio, second_audio
            image_url = params.get('image_url') or params.get('image') or input_data
            first_audio_url = params.get('first_audio_url') or params.get('first_audio')
            second_audio_url = params.get('second_audio_url') or params.get('second_audio')

            if not image_url:
                return self._create_error_result(
                    "No image provided. Use 'image_url' parameter or provide from previous step.",
                    step.model
                )

            if not first_audio_url:
                return self._create_error_result(
                    "No audio provided. Use 'first_audio_url' parameter.",
                    step.model
                )

            # Show parameters being used
            people_count = 2 if second_audio_url else 1
            print(f"Generating {people_count}-person conversation")
            image_display = str(image_url)[:60] if image_url else 'N/A'
            print(f"Image: {image_display}...")

            # Build generator parameters
            gen_params = {
                'image_url': image_url,
                'first_audio_url': first_audio_url,
                'prompt': params.get('prompt', 'A person speaking naturally'),
                'num_frames': params.get('num_frames', 81),
                'turbo': params.get('turbo', True),
                'sampling_steps': params.get('sampling_steps', 40),
            }

            if second_audio_url:
                gen_params['second_audio_url'] = second_audio_url

            if params.get('seed') is not None:
                gen_params['seed'] = params['seed']

            # Save to output directory if specified
            output_dir = chain_config.get('output_dir', 'output')
            output_path = f"{output_dir}/multitalk_{int(time.time())}.mp4"
            gen_params['output_path'] = output_path

            print("Submitting to Replicate MultiTalk API...")
            start_time = time.time()

            # Call the correct method - returns a dict, not an object
            result = self.generator.generate_conversation_video(**gen_params)

            processing_time = time.time() - start_time

            # Extract from dict response (keys: 'video', 'generation_time', 'parameters')
            video_url = result.get('video', {}).get('url')

            if video_url:
                print("MultiTalk generation completed successfully!")
                return {
                    "success": True,
                    "output_path": output_path if output_path and __import__('os').path.exists(output_path) else None,
                    "output_url": video_url,
                    "processing_time": result.get('generation_time', processing_time),
                    "cost": processing_time * 0.0023,  # Replicate H100 ~$0.0023/sec
                    "model": step.model,
                    "metadata": {
                        "parameters": result.get('parameters', {}),
                        "people_count": people_count,
                    },
                    "error": None
                }
            else:
                return self._create_error_result(
                    "No video URL in MultiTalk response",
                    step.model
                )

        except Exception as e:
            print(f"MultiTalk generation failed: {e}")
            return self._create_error_result(
                f"MultiTalk generation failed: {str(e)}",
                step.model
            )
