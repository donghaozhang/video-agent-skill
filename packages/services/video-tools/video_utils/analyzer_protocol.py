"""
Abstract protocol for media analyzers.

Defines the interface that all media analyzer implementations must follow.
This enables swapping between Gemini, FAL, or future providers without
changing consumer code.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Union


class MediaAnalyzerProtocol(ABC):
    """Abstract base class for all media analyzers.

    All media analyzer implementations (Gemini, FAL, etc.) must implement
    this protocol to ensure consistent behavior across providers.

    Example:
        >>> analyzer = get_analyzer(provider='gemini')
        >>> result = analyzer.describe_video(Path('video.mp4'))
        >>> print(result['description'])
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'gemini', 'fal')."""
        pass

    @property
    @abstractmethod
    def supported_input_types(self) -> List[str]:
        """Return supported input types: 'file', 'url', or both."""
        pass

    # =========================================================================
    # Video Analysis Methods
    # =========================================================================

    @abstractmethod
    def describe_video(
        self,
        source: Union[Path, str],
        detailed: bool = False
    ) -> Dict[str, Any]:
        """Generate video description and summary.

        Args:
            source: Path to video file or URL
            detailed: Whether to perform detailed analysis

        Returns:
            Dict with 'description' key and analysis results
        """
        pass

    @abstractmethod
    def transcribe_video(
        self,
        source: Union[Path, str],
        include_timestamps: bool = True
    ) -> Dict[str, Any]:
        """Transcribe audio content from video.

        Args:
            source: Path to video file or URL
            include_timestamps: Whether to include timestamps

        Returns:
            Dict with 'transcription' key and results
        """
        pass

    @abstractmethod
    def analyze_scenes(
        self,
        source: Union[Path, str]
    ) -> Dict[str, Any]:
        """Analyze video scenes and create timeline breakdown.

        Args:
            source: Path to video file or URL

        Returns:
            Dict with 'scene_analysis' key and results
        """
        pass

    @abstractmethod
    def answer_questions(
        self,
        source: Union[Path, str],
        questions: List[str]
    ) -> Dict[str, Any]:
        """Answer specific questions about the video.

        Args:
            source: Path to video file or URL
            questions: List of questions to answer

        Returns:
            Dict with 'answers' key and results
        """
        pass

    @abstractmethod
    def extract_key_info(
        self,
        source: Union[Path, str]
    ) -> Dict[str, Any]:
        """Extract key information and insights from video.

        Args:
            source: Path to video file or URL

        Returns:
            Dict with 'key_info' key and results
        """
        pass

    # =========================================================================
    # Audio Analysis Methods
    # =========================================================================

    @abstractmethod
    def describe_audio(
        self,
        source: Union[Path, str],
        detailed: bool = False
    ) -> Dict[str, Any]:
        """Generate audio description and summary.

        Args:
            source: Path to audio file or URL
            detailed: Whether to perform detailed analysis

        Returns:
            Dict with 'description' key and results
        """
        pass

    @abstractmethod
    def transcribe_audio(
        self,
        source: Union[Path, str],
        include_timestamps: bool = True,
        speaker_identification: bool = True
    ) -> Dict[str, Any]:
        """Transcribe spoken content from audio.

        Args:
            source: Path to audio file or URL
            include_timestamps: Whether to include timestamps
            speaker_identification: Whether to identify speakers

        Returns:
            Dict with 'transcription' key and results
        """
        pass

    @abstractmethod
    def analyze_audio_content(
        self,
        source: Union[Path, str]
    ) -> Dict[str, Any]:
        """Analyze audio content for type, genre, mood, etc.

        Args:
            source: Path to audio file or URL

        Returns:
            Dict with 'content_analysis' key and results
        """
        pass

    @abstractmethod
    def detect_audio_events(
        self,
        source: Union[Path, str]
    ) -> Dict[str, Any]:
        """Detect and analyze specific events in audio.

        Args:
            source: Path to audio file or URL

        Returns:
            Dict with 'event_detection' key and results
        """
        pass

    # =========================================================================
    # Image Analysis Methods
    # =========================================================================

    @abstractmethod
    def describe_image(
        self,
        source: Union[Path, str],
        detailed: bool = False
    ) -> Dict[str, Any]:
        """Generate image description and summary.

        Args:
            source: Path to image file or URL
            detailed: Whether to perform detailed analysis

        Returns:
            Dict with 'description' key and results
        """
        pass

    @abstractmethod
    def classify_image(
        self,
        source: Union[Path, str]
    ) -> Dict[str, Any]:
        """Classify image content and categorize.

        Args:
            source: Path to image file or URL

        Returns:
            Dict with 'classification' key and results
        """
        pass

    @abstractmethod
    def detect_objects(
        self,
        source: Union[Path, str],
        detailed: bool = False
    ) -> Dict[str, Any]:
        """Detect and identify objects in the image.

        Args:
            source: Path to image file or URL
            detailed: Whether to perform detailed detection

        Returns:
            Dict with 'object_detection' key and results
        """
        pass

    @abstractmethod
    def extract_text_from_image(
        self,
        source: Union[Path, str]
    ) -> Dict[str, Any]:
        """Extract and transcribe text from image (OCR).

        Args:
            source: Path to image file or URL

        Returns:
            Dict with 'extracted_text' key and results
        """
        pass

    @abstractmethod
    def analyze_image_composition(
        self,
        source: Union[Path, str]
    ) -> Dict[str, Any]:
        """Analyze image composition, style, and technical aspects.

        Args:
            source: Path to image file or URL

        Returns:
            Dict with 'composition_analysis' key and results
        """
        pass

    # =========================================================================
    # Convenience Methods (Optional - can be overridden)
    # =========================================================================

    def answer_audio_questions(
        self,
        source: Union[Path, str],
        questions: List[str]
    ) -> Dict[str, Any]:
        """Answer specific questions about the audio.

        Default implementation delegates to answer_questions.
        Override if provider has specific audio Q&A support.
        """
        return self.answer_questions(source, questions)

    def answer_image_questions(
        self,
        source: Union[Path, str],
        questions: List[str]
    ) -> Dict[str, Any]:
        """Answer specific questions about the image.

        Default implementation delegates to answer_questions.
        Override if provider has specific image Q&A support.
        """
        return self.answer_questions(source, questions)
