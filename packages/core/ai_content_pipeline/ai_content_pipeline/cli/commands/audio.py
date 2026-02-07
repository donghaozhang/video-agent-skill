"""
Audio/speech CLI commands.

Commands: transcribe, list-speech-models.
"""

from types import SimpleNamespace

import click


@click.command("transcribe")
@click.option("-i", "--input", "input_path", required=True, help="Input audio file path or URL")
@click.option("-o", "--output", "output_dir", default="output", help="Output directory")
@click.option("--language", default=None, help="Language code (e.g., eng, spa, fra). Default: auto-detect")
@click.option("--diarize/--no-diarize", default=True, help="Enable/disable speaker diarization")
@click.option("--tag-events/--no-tag-events", default=True, help="Enable/disable audio event tagging")
@click.option("--keyterms", multiple=True, help="Terms to bias transcription toward (increases cost by 30%%)")
@click.option("--save-json", default=None, help="Save detailed metadata as JSON file")
@click.option("--raw-json", default=None, help="Save raw API response with word-level timestamps as JSON")
@click.option("--srt", default=None, help="Generate SRT subtitle file from word timestamps")
@click.option("--srt-max-words", type=int, default=8, help="Max words per subtitle line")
@click.option("--srt-max-duration", type=float, default=4.0, help="Max seconds per subtitle")
@click.pass_context
def transcribe_cmd(ctx, input_path, output_dir, language, diarize, tag_events,
                   keyterms, save_json, raw_json, srt, srt_max_words, srt_max_duration):
    """Transcribe audio using ElevenLabs Scribe v2."""
    from ...speech_to_text import transcribe_command

    args = SimpleNamespace(
        input=input_path,
        output=output_dir,
        language=language,
        diarize=diarize,
        tag_events=tag_events,
        keyterms=list(keyterms) if keyterms else None,
        save_json=save_json,
        raw_json=raw_json,
        srt=srt,
        srt_max_words=srt_max_words,
        srt_max_duration=srt_max_duration,
    )
    transcribe_command(args)


@click.command("list-speech-models")
def list_speech_models_cmd():
    """List available speech-to-text models."""
    from ...speech_to_text import list_speech_models
    list_speech_models()


def register_audio_commands(group):
    """Register all audio commands with the CLI group."""
    group.add_command(transcribe_cmd)
    group.add_command(list_speech_models_cmd)
