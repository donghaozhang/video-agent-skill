"""
Root Click CLI group for AI Content Pipeline.

Provides the top-level ``aicp`` command group with global options
(--json, --quiet, --debug, --base-dir, --config-dir, --cache-dir,
--state-dir) and threads a CLIOutput instance through Click's context.

All commands are registered at import time so that
``from ai_content_pipeline.cli.click_app import cli`` always
returns a fully-populated group.
"""

import os
import click

from .output import CLIOutput


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="""
Examples:
  aicp list-models
  aicp generate-image --text "epic space battle" --model flux_dev
  aicp create-video --text "serene mountain lake"
  aicp run-chain --config my_chain.yaml --input "cyberpunk city"
  aicp generate-avatar --image-url "https://..." --audio-url "https://..."
  aicp analyze-video -i video.mp4
  aicp vimax idea2video --idea "A samurai's journey at sunrise"
""",
)
@click.option("--json", "json_mode", is_flag=True, default=False,
              help="Emit machine-readable JSON output to stdout")
@click.option("--quiet", "-q", is_flag=True, default=False,
              help="Suppress non-essential output (errors still go to stderr)")
@click.option("--debug", is_flag=True, default=False,
              help="Enable debug output")
@click.option("--base-dir", default=".", show_default=True,
              help="Base directory for operations")
@click.option("--config-dir", default=None,
              help="Override config directory (default: XDG_CONFIG_HOME/video-ai-studio)")
@click.option("--cache-dir", default=None,
              help="Override cache directory (default: XDG_CACHE_HOME/video-ai-studio)")
@click.option("--state-dir", default=None,
              help="Override state directory (default: XDG_STATE_HOME/video-ai-studio)")
@click.pass_context
def cli(ctx, json_mode, quiet, debug, base_dir, config_dir, cache_dir, state_dir):
    """AI Content Pipeline - Unified content creation with multiple AI models."""
    ctx.ensure_object(dict)

    # Apply XDG directory overrides before any path resolution
    if config_dir:
        os.environ["XDG_CONFIG_HOME"] = config_dir
    if cache_dir:
        os.environ["XDG_CACHE_HOME"] = cache_dir
    if state_dir:
        os.environ["XDG_STATE_HOME"] = state_dir

    # Store shared state for subcommands
    ctx.obj["output"] = CLIOutput(json_mode=json_mode, quiet=quiet, debug=debug)
    ctx.obj["base_dir"] = base_dir
    ctx.obj["json_mode"] = json_mode
    ctx.obj["quiet"] = quiet
    ctx.obj["debug"] = debug

    # Show help if no subcommand was given
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ---------------------------------------------------------------------------
# Register all commands at import time
# ---------------------------------------------------------------------------
from .commands import register_all_commands  # noqa: E402

register_all_commands(cli)

# Register vimax as a native subgroup (optional dependency)
try:
    from ai_content_platform.vimax.cli.commands import vimax

    cli.add_command(vimax)
except ImportError:
    pass
