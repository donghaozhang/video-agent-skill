"""
FAL OpenRouter Video Analyzer.

Implements MediaAnalyzerProtocol using FAL's OpenRouter API.
Supports Gemini 2.5 and Gemini 3 model variants.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .analyzer_protocol import MediaAnalyzerProtocol

try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False


class FalVideoAnalyzer(MediaAnalyzerProtocol):
    """FAL OpenRouter video, audio, and image analyzer.

    Uses FAL's OpenRouter API to access multiple Vision Language Models
    for media analysis. Supports Gemini 2.5 and Gemini 3 model variants.

    Note:
        FAL requires media to be accessible via URL. Local files must be
        uploaded to cloud storage first.

    Example:
        >>> analyzer = FalVideoAnalyzer(model='google/gemini-2.5-flash')
        >>> result = analyzer.describe_video('https://example.com/video.mp4')
        >>> print(result['description'])
    """

    SUPPORTED_MODELS = [
        "google/gemini-3-pro-preview",
        "google/gemini-3-flash-preview",
        "google/gemini-2.5-pro",
        "google/gemini-2.5-flash",
        "google/gemini-2.5-flash-lite",
        "google/gemini-2.0-flash-001",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "google/gemini-2.5-flash"
    ):
        """Initialize FAL analyzer.

        Args:
            api_key: FAL API key (defaults to FAL_KEY env var)
            model: Model to use for analysis (default: google/gemini-2.5-flash)

        Raises:
            ImportError: If fal-client is not installed
            ValueError: If FAL_KEY is not set
        """
        if not FAL_AVAILABLE:
            raise ImportError(
                "FAL client not installed. Run: pip install fal-client"
            )

        self.api_key = api_key or os.getenv('FAL_KEY')
        if not self.api_key:
            raise ValueError(
                "FAL API key required. Set FAL_KEY environment variable"
            )

        os.environ['FAL_KEY'] = self.api_key
        self.model = model

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "fal"

    @property
    def supported_input_types(self) -> List[str]:
        """Return supported input types."""
        return ["url"]  # FAL only supports URLs

    def _get_url(self, source: Union[Path, str]) -> str:
        """Convert source to URL, raising error if local file.

        Args:
            source: Path or URL string

        Returns:
            URL string

        Raises:
            ValueError: If source is a local file path
        """
        if isinstance(source, Path):
            raise ValueError(
                f"FAL requires video URLs, not local files. "
                f"Upload {source} to cloud storage first."
            )
        if isinstance(source, str) and not source.startswith(('http://', 'https://')):
            raise ValueError(
                f"FAL requires video URLs, not local files. "
                f"Upload {source} to cloud storage first."
            )
        return source

    # Models that require reasoning mode
    REASONING_MODELS = [
        "google/gemini-2.5-pro",
        "google/gemini-3-pro-preview",
    ]

    def _analyze(
        self,
        video_url: str,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Core analysis method using FAL OpenRouter.

        Args:
            video_url: URL to the video
            prompt: Analysis prompt
            system_prompt: Optional system context

        Returns:
            Dict with output, usage, and model info

        Raises:
            RuntimeError: If FAL API call fails
        """
        input_params = {
            "video_url": video_url,
            "prompt": prompt,
            "model": self.model,
        }

        if system_prompt:
            input_params["system_prompt"] = system_prompt

        # Enable reasoning for models that require it
        if self.model in self.REASONING_MODELS:
            input_params["reasoning"] = True

        try:
            result = fal_client.subscribe(
                "openrouter/router/video/enterprise",
                arguments=input_params
            )
        except Exception as e:
            raise RuntimeError(
                f"FAL API call failed for model '{self.model}': {e}"
            ) from e

        return {
            "output": result.get("output", ""),
            "usage": result.get("usage", {}),
            "model": self.model,
            "provider": "fal"
        }

    # =========================================================================
    # Video Analysis Methods
    # =========================================================================

    def describe_video(
        self,
        source: Union[Path, str],
        detailed: bool = False
    ) -> Dict[str, Any]:
        """Generate video description and summary."""
        url = self._get_url(source)

        if detailed:
            prompt = """Analyze this video in detail and provide:
1. Overall summary and main topic
2. Key scenes and their timestamps
3. Visual elements (objects, people, settings, actions)
4. Audio content (speech, music, sounds)
5. Mood and tone
6. Technical observations (quality, style, etc.)

Provide structured analysis with clear sections."""
        else:
            prompt = """Provide a concise description of this video including:
- Main content and topic
- Key visual elements
- Brief summary of what happens
- Duration and pacing"""

        print(f"🤖 Generating video description via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'description': result['output'],
            'detailed': detailed,
            'analysis_type': 'description',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def transcribe_video(
        self,
        source: Union[Path, str],
        include_timestamps: bool = True
    ) -> Dict[str, Any]:
        """Transcribe audio content from video."""
        url = self._get_url(source)

        if include_timestamps:
            prompt = """Transcribe all spoken content in this video. Include:
1. Complete transcription of all speech
2. Speaker identification if multiple speakers
3. Approximate timestamps for each segment
4. Note any non-speech audio (music, sound effects, silence)

Format as a clean, readable transcript with timestamps."""
        else:
            prompt = """Provide a complete transcription of all spoken content.
Focus on accuracy and readability. Include speaker changes if multiple people speak."""

        print(f"🎤 Transcribing video via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'transcription': result['output'],
            'include_timestamps': include_timestamps,
            'analysis_type': 'transcription',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def analyze_scenes(self, source: Union[Path, str]) -> Dict[str, Any]:
        """Analyze video scenes and create timeline breakdown."""
        url = self._get_url(source)

        prompt = """Analyze this video and break it down into distinct scenes. For each scene:
1. Start and end timestamps (approximate)
2. Scene description and main content
3. Key visual elements and actions
4. Audio content (speech, music, effects)
5. Scene transitions and cuts

Create a detailed timeline of the video content."""

        print(f"🎬 Analyzing scenes via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'scene_analysis': result['output'],
            'analysis_type': 'scenes',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def answer_questions(
        self,
        source: Union[Path, str],
        questions: List[str]
    ) -> Dict[str, Any]:
        """Answer specific questions about the video."""
        url = self._get_url(source)

        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
        prompt = f"""Analyze this video and answer the following questions:

{questions_text}

Provide detailed, accurate answers based on what you observe."""

        print(f"❓ Answering questions via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'questions': questions,
            'answers': result['output'],
            'analysis_type': 'qa',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def extract_key_info(self, source: Union[Path, str]) -> Dict[str, Any]:
        """Extract key information and insights from video."""
        url = self._get_url(source)

        prompt = """Extract key information from this video including:
1. Main topics and themes
2. Important facts or data mentioned
3. Key people, places, or objects
4. Notable quotes or statements
5. Action items or conclusions
6. Timestamps for important moments

Provide structured, actionable information."""

        print(f"🔍 Extracting key info via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'key_info': result['output'],
            'analysis_type': 'extraction',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    # =========================================================================
    # Audio Analysis Methods
    # =========================================================================

    def describe_audio(
        self,
        source: Union[Path, str],
        detailed: bool = False
    ) -> Dict[str, Any]:
        """Generate audio description and summary."""
        url = self._get_url(source)

        if detailed:
            prompt = """Analyze this audio in detail:
1. Content type (speech, music, podcast, etc.)
2. Speech content and transcription
3. Music analysis (genre, instruments, mood)
4. Sound effects and environmental audio
5. Audio quality and characteristics
6. Notable segments with timestamps"""
        else:
            prompt = """Describe this audio content:
- Type of audio (speech, music, etc.)
- Main characteristics
- Brief summary"""

        print(f"🎵 Describing audio via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'description': result['output'],
            'detailed': detailed,
            'analysis_type': 'description',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def transcribe_audio(
        self,
        source: Union[Path, str],
        include_timestamps: bool = True,
        speaker_identification: bool = True
    ) -> Dict[str, Any]:
        """Transcribe spoken content from audio."""
        url = self._get_url(source)

        prompt_parts = ["Transcribe all spoken content in this audio."]
        if include_timestamps:
            prompt_parts.append("Include timestamps for each segment.")
        if speaker_identification:
            prompt_parts.append("Identify different speakers.")
        prompt_parts.append("Format as a clean, readable transcript.")

        prompt = " ".join(prompt_parts)

        print(f"🎤 Transcribing audio via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'transcription': result['output'],
            'include_timestamps': include_timestamps,
            'speaker_identification': speaker_identification,
            'analysis_type': 'transcription',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def analyze_audio_content(self, source: Union[Path, str]) -> Dict[str, Any]:
        """Analyze audio content for type, genre, mood, etc."""
        url = self._get_url(source)

        prompt = """Analyze the content and characteristics of this audio:
1. Content type (speech, music, podcast, etc.)
2. If music: genre, style, instruments, tempo, mood
3. If speech: language, accent, speaking style, emotion
4. Audio quality and production characteristics
5. Overall mood and atmosphere"""

        print(f"🎵 Analyzing audio content via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'content_analysis': result['output'],
            'analysis_type': 'content_analysis',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def detect_audio_events(self, source: Union[Path, str]) -> Dict[str, Any]:
        """Detect and analyze specific events in audio."""
        url = self._get_url(source)

        prompt = """Detect and analyze events in this audio:
1. Speech segments with speaker changes
2. Music segments and style changes
3. Sound effects and environmental sounds
4. Silence or quiet periods
5. Notable audio events with timestamps

Create a detailed timeline of audio events."""

        print(f"🔍 Detecting audio events via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'event_detection': result['output'],
            'analysis_type': 'event_detection',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    # =========================================================================
    # Image Analysis Methods
    # =========================================================================

    def describe_image(
        self,
        source: Union[Path, str],
        detailed: bool = False
    ) -> Dict[str, Any]:
        """Generate image description and summary."""
        url = self._get_url(source)

        if detailed:
            prompt = """Analyze this image in detail:
1. Overall description and main subject
2. Objects, people, and animals
3. Setting and environment
4. Colors, lighting, and composition
5. Style and mood
6. Any text visible
7. Notable details"""
        else:
            prompt = """Describe this image:
- Main subject and content
- Key visual elements
- Setting or location
- Overall impression"""

        print(f"🖼️ Describing image via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'description': result['output'],
            'detailed': detailed,
            'analysis_type': 'description',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def classify_image(self, source: Union[Path, str]) -> Dict[str, Any]:
        """Classify image content and categorize."""
        url = self._get_url(source)

        prompt = """Classify and categorize this image:
1. Primary category (portrait, landscape, object, etc.)
2. Content type (photograph, artwork, diagram, etc.)
3. Subject classification (people, animals, nature, etc.)
4. Style or genre
5. Purpose or context"""

        print(f"🏷️ Classifying image via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'classification': result['output'],
            'analysis_type': 'classification',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def detect_objects(
        self,
        source: Union[Path, str],
        detailed: bool = False
    ) -> Dict[str, Any]:
        """Detect and identify objects in the image."""
        url = self._get_url(source)

        if detailed:
            prompt = """Detect all objects in this image:
1. List all identifiable objects with locations
2. Count quantities
3. Describe object relationships
4. Note characteristics, colors, conditions
5. Identify any text or labels
6. Describe spatial arrangement"""
        else:
            prompt = """Identify main objects in this image:
- List primary objects
- Note their locations
- Include approximate counts"""

        print(f"🔍 Detecting objects via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'object_detection': result['output'],
            'detailed': detailed,
            'analysis_type': 'object_detection',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def extract_text_from_image(self, source: Union[Path, str]) -> Dict[str, Any]:
        """Extract and transcribe text from image (OCR)."""
        url = self._get_url(source)

        prompt = """Extract all text visible in this image:
1. Transcribe all readable text
2. Preserve formatting and layout
3. Note text locations
4. Identify text styles (headlines, body, etc.)
5. Note any unclear text"""

        print(f"📝 Extracting text via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'extracted_text': result['output'],
            'analysis_type': 'text_extraction',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }

    def analyze_image_composition(self, source: Union[Path, str]) -> Dict[str, Any]:
        """Analyze image composition, style, and technical aspects."""
        url = self._get_url(source)

        prompt = """Analyze the composition and technical aspects:
1. Composition techniques (rule of thirds, symmetry, etc.)
2. Lighting analysis
3. Color palette and harmony
4. Depth of field and focus
5. Perspective and viewpoint
6. Visual balance
7. Style and artistic elements"""

        print(f"🎨 Analyzing composition via FAL ({self.model})...")
        result = self._analyze(url, prompt)

        return {
            'composition_analysis': result['output'],
            'analysis_type': 'composition',
            'usage': result['usage'],
            'provider': 'fal',
            'model': self.model
        }


def check_fal_requirements() -> tuple:
    """Check if FAL requirements are met.

    Returns:
        Tuple of (is_available: bool, message: str)
    """
    if not FAL_AVAILABLE:
        return False, "FAL client not installed. Run: pip install fal-client"

    api_key = os.getenv('FAL_KEY')
    if not api_key:
        return False, "FAL_KEY environment variable not set"

    return True, "FAL API ready"
