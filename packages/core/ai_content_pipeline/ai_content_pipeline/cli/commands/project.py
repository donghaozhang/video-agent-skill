"""
Project structure CLI commands.

Commands: init-project, organize-project, structure-info.
"""

from types import SimpleNamespace

import click


@click.command("init-project")
@click.option("-d", "--directory", default=".", help="Directory to initialize")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show what would be created without making changes")
@click.pass_context
def init_project_cmd(ctx, directory, dry_run):
    """Initialize project with standard directory structure."""
    from ...project_structure_cli import init_project_command

    args = SimpleNamespace(directory=directory, dry_run=dry_run)
    init_project_command(args)


@click.command("organize-project")
@click.option("-d", "--directory", default=".", help="Project root directory")
@click.option("-s", "--source", default=None, help="Source directory to organize from")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show what would be moved without making changes")
@click.option("-r", "--recursive", is_flag=True, default=False,
              help="Recursively scan subdirectories")
@click.option("--include-output", is_flag=True, default=False,
              help="Also organize files in output/ folder into subfolders")
@click.pass_context
def organize_project_cmd(ctx, directory, source, dry_run, recursive, include_output):
    """Organize files into standard project structure."""
    from ...project_structure_cli import organize_project_command

    args = SimpleNamespace(
        directory=directory,
        source=source,
        dry_run=dry_run,
        recursive=recursive,
        include_output=include_output,
    )
    organize_project_command(args)


@click.command("structure-info")
@click.option("-d", "--directory", default=".", help="Project directory")
@click.pass_context
def structure_info_cmd(ctx, directory):
    """Show project structure information."""
    from ...project_structure_cli import structure_info_command

    args = SimpleNamespace(directory=directory)
    structure_info_command(args)


def register_project_commands(group):
    """Register all project commands with the CLI group."""
    group.add_command(init_project_cmd)
    group.add_command(organize_project_cmd)
    group.add_command(structure_info_cmd)
