"""
Analyzer Factory for creating media analyzers.

Provides a single point of configuration for selecting between
different analyzer implementations (Gemini, FAL, etc.).

Usage:
    # Get default analyzer (controlled by MEDIA_ANALYZER_PROVIDER env var)
    analyzer = get_analyzer()

    # Get specific provider
    gemini = get_analyzer(provider='gemini')
    fal = get_analyzer(provider='fal', model='google/gemini-2.5-flash')

    # Switch provider via environment variable
    export MEDIA_ANALYZER_PROVIDER=fal
    export FAL_DEFAULT_MODEL=google/gemini-2.5-flash
"""

import os
from typing import Optional, List

from .analyzer_protocol import MediaAnalyzerProtocol


# Provider selection via environment variable
# Options: 'gemini' (default), 'fal'
DEFAULT_PROVIDER = os.getenv('MEDIA_ANALYZER_PROVIDER', 'gemini')

# Default model for FAL provider
DEFAULT_FAL_MODEL = os.getenv('FAL_DEFAULT_MODEL', 'google/gemini-2.5-flash')


class AnalyzerFactory:
    """Factory for creating media analyzers.

    This factory provides a centralized way to create analyzer instances,
    allowing easy switching between providers (Gemini, FAL) without
    modifying consumer code.

    Example:
        >>> analyzer = AnalyzerFactory.create()  # Uses default provider
        >>> analyzer = AnalyzerFactory.create(provider='fal', model='google/gemini-3')
    """

    @classmethod
    def create(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> MediaAnalyzerProtocol:
        """Create an analyzer instance.

        Args:
            provider: Provider name ('gemini', 'fal').
                     Defaults to MEDIA_ANALYZER_PROVIDER env var or 'gemini'
            model: Model to use (only applicable for FAL provider)
            **kwargs: Additional arguments passed to provider constructor

        Returns:
            MediaAnalyzerProtocol implementation

        Raises:
            ValueError: If provider is unknown
            ImportError: If provider dependencies are not installed
        """
        provider = provider or DEFAULT_PROVIDER

        if provider == 'gemini':
            from .gemini_analyzer import GeminiVideoAnalyzer
            return GeminiVideoAnalyzer(**kwargs)

        elif provider == 'fal':
            from .fal_video_analyzer import FalVideoAnalyzer
            model = model or DEFAULT_FAL_MODEL
            return FalVideoAnalyzer(model=model, **kwargs)

        else:
            available = cls.list_providers()
            raise ValueError(
                f"Unknown provider: '{provider}'. "
                f"Available providers: {available}"
            )

    @classmethod
    def get_default_provider(cls) -> str:
        """Get the default provider name.

        Returns:
            Current default provider name
        """
        return DEFAULT_PROVIDER

    @classmethod
    def list_providers(cls) -> List[str]:
        """List available providers.

        Returns:
            List of available provider names
        """
        providers = ['gemini']

        try:
            from .fal_video_analyzer import FAL_AVAILABLE
            if FAL_AVAILABLE:
                providers.append('fal')
        except ImportError:
            pass

        return providers

    @classmethod
    def is_provider_available(cls, provider: str) -> bool:
        """Check if a specific provider is available.

        Args:
            provider: Provider name to check

        Returns:
            True if provider is available, False otherwise
        """
        if provider == 'gemini':
            try:
                from .gemini_analyzer import GEMINI_AVAILABLE
                return GEMINI_AVAILABLE
            except ImportError:
                return False

        elif provider == 'fal':
            try:
                from .fal_video_analyzer import FAL_AVAILABLE
                return FAL_AVAILABLE
            except ImportError:
                return False

        return False

    @classmethod
    def get_provider_requirements(cls, provider: str) -> dict:
        """Get requirements status for a provider.

        Args:
            provider: Provider name

        Returns:
            Dict with 'available' bool and 'message' string
        """
        if provider == 'gemini':
            try:
                from .gemini_analyzer import check_gemini_requirements
                available, message = check_gemini_requirements()
                return {'available': available, 'message': message}
            except ImportError:
                return {
                    'available': False,
                    'message': 'Gemini SDK not installed. Run: pip install google-generativeai'
                }

        elif provider == 'fal':
            try:
                from .fal_video_analyzer import check_fal_requirements
                available, message = check_fal_requirements()
                return {'available': available, 'message': message}
            except ImportError:
                return {
                    'available': False,
                    'message': 'FAL client not installed. Run: pip install fal-client'
                }

        return {'available': False, 'message': f'Unknown provider: {provider}'}


def get_analyzer(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> MediaAnalyzerProtocol:
    """Convenience function to get an analyzer.

    This is the primary entry point for getting an analyzer instance.
    Provider selection is controlled by:
    1. The 'provider' parameter (highest priority)
    2. MEDIA_ANALYZER_PROVIDER environment variable
    3. Default: 'gemini'

    Args:
        provider: 'gemini' or 'fal'
        model: Model for FAL (e.g., 'google/gemini-2.5-flash')
        **kwargs: Additional provider-specific arguments

    Returns:
        Configured analyzer instance

    Example:
        >>> # Get default analyzer
        >>> analyzer = get_analyzer()

        >>> # Get FAL analyzer with specific model
        >>> analyzer = get_analyzer(provider='fal', model='google/gemini-2.5-flash')

        >>> # Analyze video
        >>> result = analyzer.describe_video('https://example.com/video.mp4')
    """
    return AnalyzerFactory.create(provider=provider, model=model, **kwargs)


def print_provider_status():
    """Print status of all available providers."""
    print("🔌 Media Analyzer Providers")
    print("=" * 40)
    print(f"📌 Default provider: {DEFAULT_PROVIDER}")
    print()

    for provider in ['gemini', 'fal']:
        status = AnalyzerFactory.get_provider_requirements(provider)
        icon = "✅" if status['available'] else "❌"
        print(f"{icon} {provider.upper()}: {status['message']}")

    print()
    print("💡 Switch provider with: export MEDIA_ANALYZER_PROVIDER=fal")
