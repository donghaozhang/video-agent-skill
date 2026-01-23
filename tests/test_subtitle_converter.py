"""
Unit tests for subtitle_converter module.

Tests word-level timestamp to SRT conversion.
"""

import pytest
import sys
from pathlib import Path

# Add package path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages/core/ai_content_pipeline"))

from ai_content_pipeline.subtitle_converter import (
    words_to_srt,
    SubtitleConfig,
    _format_timecode,
    _segment_words,
)


class TestFormatTimecode:
    """Tests for timecode formatting."""

    def test_zero_seconds(self):
        """Zero formats correctly."""
        assert _format_timecode(0) == "00:00:00,000"

    def test_simple_seconds(self):
        """Simple seconds format correctly."""
        assert _format_timecode(1.5) == "00:00:01,500"

    def test_minutes(self):
        """Minutes format correctly."""
        assert _format_timecode(65.123) == "00:01:05,123"

    def test_hours(self):
        """Hours format correctly."""
        assert _format_timecode(3661.5) == "01:01:01,500"

    def test_none_returns_zero(self):
        """None input returns zero timecode."""
        assert _format_timecode(None) == "00:00:00,000"


class TestWordsToSrt:
    """Tests for SRT generation."""

    def test_empty_words_returns_empty(self):
        """Empty input returns empty string."""
        assert words_to_srt([]) == ""

    def test_basic_conversion(self):
        """Basic words convert to valid SRT format."""
        words = [
            {"text": "Hello", "start": 0.0, "end": 0.5, "type": "word"},
            {"text": "world", "start": 0.6, "end": 1.0, "type": "word"},
        ]
        srt = words_to_srt(words)

        assert "1\n" in srt
        assert "00:00:00,000 --> " in srt
        assert "Hello world" in srt

    def test_skips_spacing_elements(self):
        """Only processes type='word' elements."""
        words = [
            {"text": "Hello", "start": 0.0, "end": 0.5, "type": "word"},
            {"text": " ", "start": 0.5, "end": 0.6, "type": "spacing"},
            {"text": "world", "start": 0.6, "end": 1.0, "type": "word"},
        ]
        srt = words_to_srt(words)

        # Should not contain the raw spacing text
        lines = srt.split("\n")
        text_line = [l for l in lines if "Hello" in l][0]
        assert text_line == "Hello world"

    def test_respects_max_words(self):
        """Splits at max_words_per_line boundary."""
        words = [
            {"text": f"word{i}", "start": i * 0.5, "end": i * 0.5 + 0.4, "type": "word"}
            for i in range(10)
        ]
        config = SubtitleConfig(max_words_per_line=4)
        srt = words_to_srt(words, config)

        # Should have at least 3 subtitle blocks (10 words / 4 = 2.5 -> 3)
        subtitle_count = srt.count("\n\n") + 1
        assert subtitle_count >= 3

    def test_respects_gap_threshold(self):
        """New subtitle on silence gap > min_gap_for_split."""
        words = [
            {"text": "Before", "start": 0.0, "end": 0.5, "type": "word"},
            {"text": "After", "start": 2.0, "end": 2.5, "type": "word"},  # 1.5s gap
        ]
        config = SubtitleConfig(min_gap_for_split=0.5)
        srt = words_to_srt(words, config)

        # Should have 2 separate subtitle blocks
        assert "1\n" in srt
        assert "2\n" in srt

    def test_respects_max_duration(self):
        """Splits when duration exceeds max_duration."""
        words = [
            {"text": "word1", "start": 0.0, "end": 0.5, "type": "word"},
            {"text": "word2", "start": 0.6, "end": 1.0, "type": "word"},
            {"text": "word3", "start": 1.1, "end": 1.5, "type": "word"},
            {"text": "word4", "start": 1.6, "end": 2.0, "type": "word"},
            {"text": "word5", "start": 2.1, "end": 2.5, "type": "word"},
        ]
        config = SubtitleConfig(max_duration=1.5, max_words_per_line=10)
        srt = words_to_srt(words, config)

        # Should split due to duration
        assert "2\n" in srt


class TestSubtitleConfig:
    """Tests for SubtitleConfig defaults."""

    def test_default_values(self):
        """Config has sensible defaults."""
        config = SubtitleConfig()
        assert config.max_words_per_line == 8
        assert config.max_chars_per_line == 42
        assert config.max_duration == 4.0
        assert config.min_gap_for_split == 0.5
        assert config.include_speaker_labels is False

    def test_custom_values(self):
        """Config accepts custom values."""
        config = SubtitleConfig(
            max_words_per_line=5,
            max_duration=3.0,
        )
        assert config.max_words_per_line == 5
        assert config.max_duration == 3.0


class TestSegmentWords:
    """Tests for word segmentation logic."""

    def test_single_word(self):
        """Single word creates single segment."""
        words = [{"text": "Hello", "start": 0.0, "end": 0.5, "type": "word"}]
        config = SubtitleConfig()
        segments = _segment_words(words, config)

        assert len(segments) == 1
        assert segments[0]["words"] == ["Hello"]

    def test_skips_audio_events(self):
        """Audio events are skipped."""
        words = [
            {"text": "Hello", "start": 0.0, "end": 0.5, "type": "word"},
            {"text": "[laughter]", "start": 0.6, "end": 0.8, "type": "audio_event"},
            {"text": "world", "start": 0.9, "end": 1.3, "type": "word"},  # Gap < 0.5s
        ]
        config = SubtitleConfig()
        segments = _segment_words(words, config)

        # Should have 1 segment with just the words (audio_event skipped)
        assert len(segments) == 1
        assert "[laughter]" not in segments[0]["words"]
        assert segments[0]["words"] == ["Hello", "world"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
