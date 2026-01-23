"""
Speech-to-text CLI command implementation.

Provides transcribe command for ElevenLabs Scribe v2 model
to transcribe audio files with speaker diarization.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

from .subtitle_converter import words_to_srt, SubtitleConfig

# Try to import FAL client for file uploads
try:
    import fal_client
    FAL_CLIENT_AVAILABLE = True
except ImportError:
    FAL_CLIENT_AVAILABLE = False

# Try to import speech-to-text generator
try:
    # Add package path for direct import
    import sys as _sys
    _speech_path = Path(__file__).parent.parent.parent.parent / "providers/fal/speech-to-text"
    if str(_speech_path) not in _sys.path:
        _sys.path.insert(0, str(_speech_path))
    from fal_speech_to_text import FALSpeechToTextGenerator
    from fal_speech_to_text.models.base import TranscriptionResult
    FAL_SPEECH_AVAILABLE = True
except ImportError:
    FAL_SPEECH_AVAILABLE = False
    TranscriptionResult = None
    FALSpeechToTextGenerator = None


# Model information
MODEL_INFO = {
    "scribe_v2": {
        "name": "ElevenLabs Scribe v2",
        "provider": "FAL AI",
        "cost_per_minute": 0.008,
        "keyterm_cost_increase": 0.30,
        "features": [
            "99 language support",
            "Word-level timestamps",
            "Speaker diarization",
            "Audio event tagging",
            "Fast inference",
        ],
    }
}

# Default values
DEFAULTS = {
    "model": "scribe_v2",
    "output_dir": "output",
    "diarize": True,
    "tag_events": True,
}


@dataclass
class TranscriptionCLIResult:
    """Result from transcription CLI operation."""
    success: bool
    text: str = ""
    txt_path: Optional[str] = None
    json_path: Optional[str] = None
    speakers: Optional[List[str]] = None
    duration: Optional[float] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    language_detected: Optional[str] = None
    language_probability: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None


def check_dependencies() -> Tuple[bool, str]:
    """
    Check if required dependencies are available.

    Returns:
        Tuple of (success, error_message)
    """
    if not FAL_CLIENT_AVAILABLE:
        return False, "fal-client not installed. Run: pip install fal-client"
    if not FAL_SPEECH_AVAILABLE:
        return False, "fal_speech_to_text module not available. Check package installation."
    if not os.getenv("FAL_KEY"):
        return False, "FAL_KEY environment variable not set"
    return True, ""


def upload_if_local(file_path: str, file_type: str = "audio") -> str:
    """
    Upload local file to FAL if it's a local path, otherwise return as-is.

    Args:
        file_path: Local file path or URL
        file_type: Description for logging ("audio")

    Returns:
        URL (uploaded or original)

    Raises:
        FileNotFoundError: If local file doesn't exist
        ValueError: If upload fails
    """
    if file_path.startswith(("http://", "https://")):
        return file_path

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"{file_type.title()} not found: {file_path}")

    print(f"📤 Uploading {file_type}: {path.name}")
    try:
        url = fal_client.upload_file(str(path))
        print(f"✅ {file_type.title()} uploaded: {url[:60]}...")
        return url
    except Exception as e:
        raise ValueError(f"Failed to upload {file_type}: {e}")


def transcribe(
    audio_path: str,
    output_dir: str = "output",
    model: str = "scribe_v2",
    language_code: Optional[str] = None,
    diarize: bool = True,
    tag_audio_events: bool = True,
    keyterms: Optional[List[str]] = None,
) -> TranscriptionCLIResult:
    """
    Transcribe audio file with full workflow.

    Handles file upload, API call, and output file saving.

    Args:
        audio_path: Audio file path or URL
        output_dir: Output directory for transcription files
        model: Model to use (default: scribe_v2)
        language_code: Language code (e.g., "eng"). None for auto-detect.
        diarize: Enable speaker diarization
        tag_audio_events: Tag audio events (laughter, music, etc.)
        keyterms: List of terms to bias transcription toward

    Returns:
        TranscriptionCLIResult with all operation details
    """
    # Check dependencies
    ok, error = check_dependencies()
    if not ok:
        return TranscriptionCLIResult(success=False, error=error)

    try:
        # Upload file if local
        audio_url = upload_if_local(audio_path, "audio")

        # Call API
        print(f"\n🎤 Starting transcription...")
        print(f"   Model: {model}")
        print(f"   Diarize: {diarize}")
        print(f"   Tag events: {tag_audio_events}")
        if language_code:
            print(f"   Language: {language_code}")
        if keyterms:
            print(f"   Keyterms: {', '.join(keyterms)}")

        generator = FALSpeechToTextGenerator()
        result = generator.transcribe(
            audio_url=audio_url,
            model=model,
            language_code=language_code,
            diarize=diarize,
            tag_audio_events=tag_audio_events,
            keyterms=keyterms,
        )

        if not result.success:
            return TranscriptionCLIResult(
                success=False,
                error=result.error,
                processing_time=result.processing_time,
            )

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        input_name = Path(audio_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{input_name}_transcript_{timestamp}"

        # Save text file
        txt_path = output_path / f"{base_filename}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(result.text)

        return TranscriptionCLIResult(
            success=True,
            text=result.text,
            txt_path=str(txt_path),
            speakers=result.speakers,
            duration=result.duration,
            cost=result.cost,
            processing_time=result.processing_time,
            language_detected=result.language_detected,
            language_probability=result.language_probability,
            metadata={
                "model": model,
                "diarize": diarize,
                "tag_audio_events": tag_audio_events,
                "keyterms": keyterms,
                "words_count": len(result.words) if result.words else 0,
                "audio_events_count": len(result.audio_events) if result.audio_events else 0,
            },
            raw_response=result.raw_response,
        )

    except FileNotFoundError as e:
        return TranscriptionCLIResult(success=False, error=str(e))
    except ValueError as e:
        return TranscriptionCLIResult(success=False, error=str(e))
    except Exception as e:
        return TranscriptionCLIResult(success=False, error=f"Unexpected error: {e}")


def transcribe_command(args) -> None:
    """
    Handle transcribe CLI command.

    Args:
        args: Parsed argparse arguments
    """
    load_dotenv()

    # Print header
    print(f"\n🎤 SPEECH-TO-TEXT TRANSCRIPTION")
    print("=" * 50)
    print(f"📁 Input: {args.input}")
    print(f"📁 Output: {args.output}")
    print(f"🤖 Model: scribe_v2 (ElevenLabs Scribe v2)")
    if args.language:
        print(f"🌐 Language: {args.language}")
    else:
        print(f"🌐 Language: auto-detect")
    print(f"🔊 Diarize: {args.diarize}")
    print(f"🎵 Tag events: {args.tag_events}")
    if args.keyterms:
        print(f"📌 Keyterms: {', '.join(args.keyterms)} (+30% cost)")
    print()

    # Execute transcription
    result = transcribe(
        audio_path=args.input,
        output_dir=args.output,
        language_code=args.language,
        diarize=args.diarize,
        tag_audio_events=args.tag_events,
        keyterms=args.keyterms,
    )

    # Display results
    if result.success:
        print(f"\n✅ Transcription complete!")
        if len(result.text) > 100:
            print(f"📝 Text preview: {result.text[:100]}...")
        else:
            print(f"📝 Text: {result.text}")
        if result.speakers:
            print(f"🎤 Speakers detected: {len(result.speakers)}")
        if result.language_detected:
            print(f"🌐 Language detected: {result.language_detected}")
        if result.duration:
            print(f"⏱️  Duration: {result.duration:.1f}s")
        if result.cost:
            print(f"💰 Cost: ${result.cost:.4f}")
        if result.processing_time:
            print(f"⏱️  Processing: {result.processing_time:.1f}s")
        if result.txt_path:
            print(f"📄 Text file: {result.txt_path}")

        # Save JSON if requested
        if args.save_json:
            json_path = Path(args.output) / args.save_json
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "success": True,
                    "text": result.text,
                    "txt_path": result.txt_path,
                    "speakers": result.speakers,
                    "duration": result.duration,
                    "cost": result.cost,
                    "processing_time": result.processing_time,
                    "language_detected": result.language_detected,
                    "metadata": result.metadata,
                }, f, indent=2)
            print(f"📄 Metadata: {json_path}")

        # Save raw API response if requested (includes word-level timestamps)
        if args.raw_json and result.raw_response:
            raw_json_path = Path(args.output) / args.raw_json
            raw_json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(raw_json_path, 'w', encoding='utf-8') as f:
                json.dump(result.raw_response, f, indent=2)
            print(f"📄 Raw JSON: {raw_json_path}")
        elif args.raw_json and not result.raw_response:
            print("⚠️  Warning: --raw-json specified but raw response data unavailable")

        # Generate SRT subtitles if requested
        if hasattr(args, 'srt') and args.srt and result.raw_response:
            words = result.raw_response.get("words", [])
            if words:
                config = SubtitleConfig(
                    max_words_per_line=getattr(args, 'srt_max_words', 8),
                    max_duration=getattr(args, 'srt_max_duration', 4.0),
                )
                srt_content = words_to_srt(words, config)
                srt_path = Path(args.output) / args.srt
                srt_path.parent.mkdir(parents=True, exist_ok=True)
                srt_path.write_text(srt_content, encoding='utf-8')
                print(f"📄 SRT: {srt_path}")
            else:
                print("⚠️  Warning: --srt specified but no word timestamps available")
        elif hasattr(args, 'srt') and args.srt and not result.raw_response:
            print("⚠️  Warning: --srt specified but raw response data unavailable")
    else:
        print(f"\n❌ Transcription failed!")
        print(f"   Error: {result.error}")
        sys.exit(1)


def list_speech_models() -> None:
    """Print available speech-to-text models."""
    print("\n🎤 Speech-to-Text Models")
    print("=" * 50)

    for model_key, info in MODEL_INFO.items():
        print(f"\n  {model_key}")
        print(f"    Name: {info['name']}")
        print(f"    Provider: {info['provider']}")
        print(f"    Cost: ${info['cost_per_minute']:.3f}/minute")
        print(f"    Keyterms: +{int(info['keyterm_cost_increase'] * 100)}% cost increase")
        print(f"    Features:")
        for feature in info['features']:
            print(f"      • {feature}")

    print("\n  Common Language Codes:")
    print("    eng (English), spa (Spanish), fra (French), deu (German)")
    print("    zho (Chinese), jpn (Japanese), kor (Korean), ara (Arabic)")
    print("    por (Portuguese), rus (Russian), ita (Italian), nld (Dutch)")
    print("\n  Audio Event Types:")
    print("    laughter, applause, music, silence, speech, noise")
