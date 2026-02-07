"""
Motion transfer CLI commands.

Commands: transfer-motion, list-motion-models.
"""

from types import SimpleNamespace

import click


@click.command("transfer-motion")
@click.option("-i", "--image", required=True, help="Image file path or URL (character/background source)")
@click.option("-v", "--video", required=True, help="Video file path or URL (motion source)")
@click.option("-o", "--output", "output_dir", default="output", help="Output directory")
@click.option("--orientation", default="video",
              type=click.Choice(["video", "image"]),
              help="Character orientation: video (max 30s) or image (max 10s)")
@click.option("--no-sound", is_flag=True, default=False,
              help="Remove audio from output (default: keep sound)")
@click.option("-p", "--prompt", default=None, help="Optional text description to guide generation")
@click.option("--save-json", default=None, help="Save result metadata as JSON file")
@click.pass_context
def transfer_motion_cmd(ctx, image, video, output_dir, orientation, no_sound, prompt, save_json):
    """Transfer motion from video to image (Kling v2.6)."""
    from ...motion_transfer import transfer_motion_command

    args = SimpleNamespace(
        image=image,
        video=video,
        output=output_dir,
        orientation=orientation,
        no_sound=no_sound,
        prompt=prompt,
        save_json=save_json,
    )
    transfer_motion_command(args)


@click.command("list-motion-models")
def list_motion_models_cmd():
    """List available motion transfer models."""
    from ...motion_transfer import list_motion_models
    list_motion_models()


def register_motion_commands(group):
    """Register all motion commands with the CLI group."""
    group.add_command(transfer_motion_cmd)
    group.add_command(list_motion_models_cmd)
