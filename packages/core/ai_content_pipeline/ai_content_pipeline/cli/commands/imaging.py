"""
Imaging CLI commands.

Commands: generate-grid, upscale-image.
"""

from types import SimpleNamespace

import click


@click.command("generate-grid")
@click.option("--prompt-file", "-f", required=True, help="Markdown file with panel descriptions")
@click.option("--grid", "-g", default="3x3", type=click.Choice(["2x2", "3x3"]),
              help="Grid size: 2x2 (4 panels) or 3x3 (9 panels)")
@click.option("--style", "-s", default=None, help="Style override (replaces prompt file style)")
@click.option("--model", "-m", default="nano_banana_pro", help="Model to use")
@click.option("--upscale", type=float, default=None, help="Upscale factor after generation (e.g., 2 for 2x)")
@click.option("-o", "--output", "output_dir", default="output", help="Output directory")
@click.option("--save-json", default=None, help="Save metadata as JSON file")
def generate_grid_cmd(prompt_file, grid, style, model, upscale, output_dir, save_json):
    """Generate 2x2 or 3x3 image grid from prompt file."""
    from ...grid_generator import generate_grid_command

    args = SimpleNamespace(
        prompt_file=prompt_file,
        grid=grid,
        style=style,
        model=model,
        upscale=upscale,
        output=output_dir,
        save_json=save_json,
    )
    generate_grid_command(args)


@click.command("upscale-image")
@click.option("-i", "--input", "input_path", required=True, help="Input image path or URL")
@click.option("--factor", type=float, default=2, help="Upscale factor 1-8")
@click.option("--target", default=None, type=click.Choice(["720p", "1080p", "1440p", "2160p"]),
              help="Target resolution. Overrides --factor")
@click.option("--format", "output_format", default="png", type=click.Choice(["png", "jpg", "webp"]),
              help="Output format")
@click.option("-o", "--output", "output_dir", default="output", help="Output directory")
@click.option("--save-json", default=None, help="Save metadata as JSON file")
def upscale_image_cmd(input_path, factor, target, output_format, output_dir, save_json):
    """Upscale image using SeedVR2."""
    from ...grid_generator import upscale_image_command

    args = SimpleNamespace(
        input=input_path,
        factor=factor,
        target=target,
        format=output_format,
        output=output_dir,
        save_json=save_json,
    )
    upscale_image_command(args)


def register_imaging_commands(group):
    """Register all imaging commands with the CLI group."""
    group.add_command(generate_grid_cmd)
    group.add_command(upscale_image_cmd)
