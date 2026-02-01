"""
Subtitle format converter for word-level timestamps.

Long-term design: Extensible for multiple subtitle formats.
Currently supports: SRT
Future support: VTT, ASS, JSON (for video editors)
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class SubtitleConfig:
    """Configuration for subtitle generation.

    Attributes:
        max_words_per_line: Maximum words before forcing new subtitle (default: 8)
        max_chars_per_line: Maximum characters per line (default: 42)
        max_duration: Maximum seconds per subtitle block (default: 4.0)
        min_gap_for_split: Silence gap in seconds that forces new subtitle (default: 0.5)
        include_speaker_labels: Prefix subtitles with speaker ID (default: False)
    """
    max_words_per_line: int = 8
    max_chars_per_line: int = 42
    max_duration: float = 4.0
    min_gap_for_split: float = 0.5
    include_speaker_labels: bool = False


def words_to_srt(
    words: List[Dict[str, Any]],
    config: Optional[SubtitleConfig] = None
) -> str:
    """
    Convert word-level timestamps to SRT subtitle format.

    Args:
        words: List of word objects from Scribe v2 API response.
               Each word has: text, start, end, type, speaker_id
        config: Subtitle generation settings (uses defaults if None)

    Returns:
        SRT formatted string ready to write to file

    Example:
        >>> words = [{"text": "Hello", "start": 0.0, "end": 0.5, "type": "word"}]
        >>> srt = words_to_srt(words)
        >>> print(srt)
        1
        00:00:00,000 --> 00:00:00,500
        Hello
    """
    config = config or SubtitleConfig()

    if not words:
        return ""

    segments = _segment_words(words, config)
    return _format_srt(segments)


def _segment_words(
    words: List[Dict[str, Any]],
    config: SubtitleConfig
) -> List[Dict[str, Any]]:
    """
    Group words into subtitle segments based on config rules.

    Segmentation rules (in priority order):
    1. Gap > min_gap_for_split -> new segment
    2. Word count >= max_words_per_line -> new segment
    3. Character count > max_chars_per_line -> new segment
    4. Duration > max_duration -> new segment
    """
    segments = []
    current_segment = {
        "words": [],
        "start": None,
        "end": None,
        "char_count": 0
    }

    for word in words:
        # Skip non-word elements (spacing, audio_events)
        if word.get("type") != "word":
            continue

        word_text = word.get("text", "")
        word_start = word.get("start", 0)
        word_end = word.get("end", 0)

        # Check if we need to start a new segment
        should_split = False

        if current_segment["words"]:
            # Gap too large (natural pause)
            if word_start - current_segment["end"] > config.min_gap_for_split:
                should_split = True
            # Too many words
            elif len(current_segment["words"]) >= config.max_words_per_line:
                should_split = True
            # Too many characters
            elif current_segment["char_count"] + len(word_text) + 1 > config.max_chars_per_line:
                should_split = True
            # Duration too long
            elif word_end - current_segment["start"] > config.max_duration:
                should_split = True

        if should_split and current_segment["words"]:
            segments.append(current_segment)
            current_segment = {"words": [], "start": None, "end": None, "char_count": 0}

        # Add word to current segment
        if current_segment["start"] is None:
            current_segment["start"] = word_start
        current_segment["end"] = word_end
        current_segment["words"].append(word_text)
        current_segment["char_count"] += len(word_text) + 1  # +1 for space

    # Don't forget final segment
    if current_segment["words"]:
        segments.append(current_segment)

    return segments


def _format_srt(segments: List[Dict[str, Any]]) -> str:
    """Format segments as SRT string."""
    lines = []
    for i, seg in enumerate(segments, 1):
        start_tc = _format_timecode(seg["start"])
        end_tc = _format_timecode(seg["end"])
        text = " ".join(seg["words"])
        lines.append(f"{i}\n{start_tc} --> {end_tc}\n{text}\n")
    return "\n".join(lines)


def _format_timecode(seconds: float) -> str:
    """
    Convert seconds to SRT timecode format HH:MM:SS,mmm

    Note: SRT uses comma as decimal separator, not period.
    """
    if seconds is None:
        seconds = 0.0
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    millis = int((secs % 1) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(secs):02d},{millis:03d}"
