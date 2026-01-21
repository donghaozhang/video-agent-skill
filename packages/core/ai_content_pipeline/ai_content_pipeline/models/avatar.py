"""Avatar generation models for AI Content Pipeline."""

import os
import warnings
from typing import Dict, Any, Optional

from ..utils.file_manager import FileManager
from .base import BaseContentModel, ModelResult


class MultiTalkGenerator(BaseContentModel):
    """FAL-based multi-person conversational video generator.

    Uses the FAL AI Avatar Multi model (fal-ai/ai-avatar/multi) to generate
    realistic conversational videos with lip-sync for one or two speakers.
    """

    def __init__(self, file_manager: Optional[FileManager] = None, **kwargs):
        """Initialize the FAL MultiTalk generator."""
        super().__init__("avatar")
        self.file_manager = file_manager
        self.generator = None
        self._initialize_generator()

    def _initialize_generator(self):
        """Initialize the FAL Avatar generator."""
        try:
            from fal_avatar import FALAvatarGenerator
            self.generator = FALAvatarGenerator()
            print("✅ FAL Avatar Multi generator initialized")
        except ImportError as e:
            print(f"❌ Failed to initialize FAL Avatar: {e}")
            print("💡 Make sure fal-client is installed: pip install fal-client")
        except Exception as e:
            print(f"❌ Error initializing FAL Avatar: {e}")

    def generate(self, input_data: Any = None, model: str = "multitalk", **kwargs) -> ModelResult:
        """Generate a multi-person conversational video using FAL.

        Args:
            image_url: URL of input image containing person(s)
            first_audio_url: URL of Person 1 audio file
            second_audio_url: Optional URL of Person 2 audio file
            prompt: Text description guiding video generation
            num_frames: Frame count (81-129, default 81)
            resolution: Output resolution ("480p" or "720p", default "480p")
            acceleration: Speed mode ("none", "regular", "high", default "regular")
            seed: Random seed for reproducibility
            turbo: Legacy param - maps to acceleration="high"

        Returns:
            ModelResult with video URL and metadata
        """
        self._start_timing()

        if not self.generator:
            return self._create_error_result(model, "FAL Avatar generator not initialized")

        try:
            # Map parameters to FAL format (support both old and new param names)
            image_url = kwargs.get('image_url', kwargs.get('image'))
            first_audio_url = kwargs.get('first_audio_url', kwargs.get('first_audio'))
            second_audio_url = kwargs.get('second_audio_url', kwargs.get('second_audio'))
            prompt = kwargs.get('prompt', 'A natural conversation')

            if not image_url or not first_audio_url:
                return self._create_error_result(
                    model,
                    "Missing required parameters: image_url and first_audio_url"
                )

            # Map legacy 'turbo' param to 'acceleration'
            acceleration = kwargs.get('acceleration', 'regular')
            if kwargs.get('turbo'):
                acceleration = 'high'

            # Generate the video
            print("🔄 Calling FAL AI Avatar Multi API...")
            if second_audio_url:
                print("💬 Generating multi-person conversation video...")
            else:
                print("👤 Generating single-person speaking video...")

            result = self.generator.generate_conversation(
                image_url=image_url,
                first_audio_url=first_audio_url,
                prompt=prompt,
                second_audio_url=second_audio_url,
                num_frames=kwargs.get('num_frames', 81),
                resolution=kwargs.get('resolution', '480p'),
                seed=kwargs.get('seed'),
                acceleration=acceleration,
            )

            if not result.success:
                return self._create_error_result(model, result.error)

            print("🎥 Video generation completed, processing result...")

            # Download video if file manager available
            output_path = None
            if self.file_manager and result.video_url:
                import time
                timestamp = int(time.time())
                filename = f"multitalk_{timestamp}.mp4"
                output_path = self.file_manager.create_output_path(filename)
                print(f"📥 Downloading video to: {output_path}")
                self._download_file(result.video_url, output_path)
                print(f"✅ Video saved locally: {output_path}")
            else:
                print(f"🔗 Video available at: {result.video_url}")

            return self._create_success_result(
                model=model,
                output_path=output_path,
                output_url=result.video_url,
                metadata={
                    'model': 'fal-ai/ai-avatar/multi',
                    'processing_time': result.processing_time,
                    'cost': result.cost,
                    'type': 'conversational_video',
                    'has_second_person': second_audio_url is not None,
                    **result.metadata,
                }
            )

        except Exception as e:
            return self._create_error_result(model, f"FAL MultiTalk generation failed: {str(e)}")

    def _download_file(self, url: str, output_path: str):
        """Download file from URL."""
        try:
            import requests
            response = requests.get(url)
            response.raise_for_status()

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)

        except Exception as e:
            print(f"Warning: Failed to download video: {e}")

    def estimate_cost(self, model: str, **kwargs) -> float:
        """Estimate cost for MultiTalk generation.

        Delegates to the underlying FAL Avatar generator for accurate pricing.

        Args:
            model: Model identifier
            num_frames: Number of frames (default 81)
            resolution: "480p" or "720p" (default "480p")

        Returns:
            Estimated cost in USD
        """
        if self.generator:
            try:
                return self.generator.estimate_cost(
                    model="multitalk",
                    duration=0,  # Not used by multitalk model
                    num_frames=kwargs.get('num_frames', 81),
                    resolution=kwargs.get('resolution', '480p'),
                )
            except Exception:
                pass  # Fall back to default estimate

        # Fallback estimate if generator not available
        return 0.10

    def get_available_models(self) -> list:
        """Get available MultiTalk models."""
        return ["multitalk"]

    def validate_input(self, input_data: Any, model: str, **kwargs) -> bool:
        """Validate input parameters."""
        image_url = kwargs.get('image_url', kwargs.get('image'))
        has_audio = any(kwargs.get(key) for key in [
            'first_audio_url', 'first_audio', 'audio_url', 'audio'
        ])

        return bool(image_url and has_audio)


class ReplicateMultiTalkGenerator(BaseContentModel):
    """DEPRECATED: Replicate MultiTalk generator for multi-person conversational videos.

    This class is deprecated. Use MultiTalkGenerator instead, which uses the
    FAL AI Avatar Multi model (fal-ai/ai-avatar/multi).

    Migration example:
        # Old (deprecated):
        generator = ReplicateMultiTalkGenerator()

        # New (recommended):
        generator = MultiTalkGenerator()
    """

    def __init__(self, file_manager: Optional[FileManager] = None, **kwargs):
        """Initialize the MultiTalk generator."""
        warnings.warn(
            "ReplicateMultiTalkGenerator is deprecated and will be removed in a future version. "
            "Use MultiTalkGenerator instead, which uses FAL AI Avatar Multi. "
            "See: issues/migrate-replicate-to-fal-avatar.md",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__("avatar")
        self.file_manager = file_manager
        self.generator = None
        self._initialize_generator()

    def _initialize_generator(self):
        """Initialize the Replicate MultiTalk generator."""
        try:
            from replicate_multitalk_generator import ReplicateMultiTalkGenerator as MultiTalkGen
            self.generator = MultiTalkGen()
            print("✅ Replicate MultiTalk generator initialized")
        except ImportError as e:
            print(f"❌ Failed to initialize MultiTalk: {e}")
            print("💡 Make sure replicate is installed: pip install replicate")
        except Exception as e:
            print(f"❌ Error initializing MultiTalk: {e}")

    def generate(self, input_data: Any = None, model: str = "multitalk", **kwargs) -> ModelResult:
        """Generate a multi-person conversational video.

        Args:
            image: URL or path to image containing person(s)
            first_audio: URL or path to first audio file
            second_audio: Optional URL or path to second audio file
            prompt: Text description of the scene
            num_frames: Number of frames (25-201, default 81)
            turbo: Enable turbo mode (default True)
            sampling_steps: Enhancement iterations (2-100, default 40)

        Returns:
            ModelResult with video URL and metadata
        """
        self._start_timing()

        if not self.generator:
            return self._create_error_result(model, "MultiTalk generator not initialized")

        try:
            # Map parameters to generator format
            image_url = kwargs.get('image', kwargs.get('image_url'))
            first_audio = kwargs.get('first_audio', kwargs.get('first_audio_url'))
            second_audio = kwargs.get('second_audio', kwargs.get('second_audio_url'))

            if not image_url or not first_audio:
                return self._create_error_result(model, "Missing required parameters: image and first_audio")

            # Generate the video
            print("🔄 Calling Replicate MultiTalk API (this will take several minutes)...")
            if second_audio:
                print("💬 Generating multi-person conversation video...")
                result = self.generator.generate_conversation_video(
                    image_url=image_url,
                    first_audio_url=first_audio,
                    second_audio_url=second_audio,
                    prompt=kwargs.get('prompt', 'A natural conversation'),
                    num_frames=kwargs.get('num_frames', 81),
                    turbo=kwargs.get('turbo', True),
                    sampling_steps=kwargs.get('sampling_steps', 40),
                    seed=kwargs.get('seed')
                )
            else:
                print("👤 Generating single-person speaking video...")
                result = self.generator.generate_single_person_video(
                    image_url=image_url,
                    audio_url=first_audio,
                    prompt=kwargs.get('prompt', 'A person speaking naturally'),
                    num_frames=kwargs.get('num_frames', 81),
                    turbo=kwargs.get('turbo', True),
                    sampling_steps=kwargs.get('sampling_steps', 40),
                    seed=kwargs.get('seed')
                )

            print("🎥 Video generation completed, processing result...")

            # Extract video URL
            video_url = result.get('video', {}).get('url')
            if not video_url:
                return self._create_error_result(model, "No video URL in result")

            # Download video if file manager available
            output_path = None
            if self.file_manager:
                import time
                timestamp = int(time.time())
                filename = f"multitalk_conversation_{timestamp}.mp4"
                output_path = self.file_manager.create_output_path(filename)
                print(f"📥 Downloading video to: {output_path}")
                self._download_file(video_url, output_path)
                print(f"✅ Video saved locally: {output_path}")
            else:
                print(f"🔗 Video available at: {video_url}")

            return self._create_success_result(
                model=model,
                output_path=output_path,
                output_url=video_url,
                metadata={
                    'model': 'replicate/multitalk',
                    'generation_time': result.get('generation_time', 0),
                    'parameters': result.get('parameters', {}),
                    'type': 'conversational_video',
                    'people_count': 2 if second_audio else 1
                }
            )

        except Exception as e:
            return self._create_error_result(model, f"MultiTalk generation failed: {str(e)}")

    def _download_file(self, url: str, output_path: str):
        """Download file from URL."""
        try:
            import requests
            response = requests.get(url)
            response.raise_for_status()

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)

        except Exception as e:
            print(f"Warning: Failed to download video: {e}")

    def estimate_cost(self, model: str, **kwargs) -> float:
        """Estimate cost for MultiTalk generation."""
        return 1.0  # $1.00 average estimate

    def get_available_models(self) -> list:
        """Get available MultiTalk models."""
        return ["multitalk"]

    def validate_input(self, input_data: Any, model: str, **kwargs) -> bool:
        """Validate input parameters."""
        required = ['image']
        has_audio = any(kwargs.get(key) for key in ['first_audio', 'audio', 'first_audio_url', 'audio_url'])

        if not has_audio:
            return False

        return all(kwargs.get(key) for key in required)
