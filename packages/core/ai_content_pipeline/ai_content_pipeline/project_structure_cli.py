"""
CLI command handlers for Project Structure Utilities.

This module provides CLI command handlers for the project structure
functionality. Separated from the core module to maintain file length limits.

File: packages/core/ai_content_pipeline/ai_content_pipeline/project_structure_cli.py
"""

from pathlib import Path
from typing import Any

from .project_structure import (
    init_project,
    organize_project,
    organize_output,
    get_structure_info,
)


def init_project_command(args: Any) -> None:
    """Handle init-project CLI command."""
    root_dir = args.directory
    dry_run = args.dry_run if hasattr(args, 'dry_run') else False

    print(f"{'[DRY RUN] ' if dry_run else ''}Initializing project structure in: {Path(root_dir).resolve()}")
    print()

    result = init_project(root_dir, dry_run=dry_run)

    if result.directories_created > 0:
        print(f"{'Would create' if dry_run else 'Created'} {result.directories_created} directories:")
        for path in result.created_paths[:10]:  # Show first 10
            print(f"  + {path}")
        if len(result.created_paths) > 10:
            print(f"  ... and {len(result.created_paths) - 10} more")

    if result.directories_existed > 0:
        print(f"\n{result.directories_existed} directories already exist")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  ! {error}")

    if result.success:
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Project structure initialized successfully!")
    else:
        print("\nProject initialization completed with errors.")


def organize_project_command(args: Any) -> None:
    """Handle organize-project CLI command."""
    root_dir = args.directory
    source_dir = args.source if hasattr(args, 'source') and args.source else None
    dry_run = args.dry_run if hasattr(args, 'dry_run') else False
    recursive = args.recursive if hasattr(args, 'recursive') else False
    include_output = args.include_output if hasattr(args, 'include_output') else False

    print(f"{'[DRY RUN] ' if dry_run else ''}Organizing project files...")
    if source_dir:
        print(f"  Source: {Path(source_dir).resolve()}")
    print(f"  Root: {Path(root_dir).resolve()}")
    if include_output:
        print("  Including output folder organization")
    print()

    # Organize input files
    result = organize_project(root_dir, source_dir, dry_run=dry_run, recursive=recursive)

    if result.files_moved > 0:
        print(f"{'Would move' if dry_run else 'Moved'} {result.files_moved} input files:")
        for source, dest in result.moves[:10]:  # Show first 10
            print(f"  {Path(source).name} -> {dest}")
        if len(result.moves) > 10:
            print(f"  ... and {len(result.moves) - 10} more")

    if result.files_skipped > 0:
        print(f"\nSkipped {result.files_skipped} files (already organized or unknown type)")

    # Organize output files if requested
    if include_output:
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing output files...")
        output_result = organize_output(root_dir, dry_run=dry_run)

        if output_result.files_moved > 0:
            print(f"{'Would move' if dry_run else 'Moved'} {output_result.files_moved} output files:")
            for source, dest in output_result.moves[:10]:
                print(f"  {Path(source).name} -> {Path(dest).name}")
            if len(output_result.moves) > 10:
                print(f"  ... and {len(output_result.moves) - 10} more")

        if output_result.files_skipped > 0:
            print(f"\nSkipped {output_result.files_skipped} output files")

        if output_result.errors:
            result.errors.extend(output_result.errors)
        if not output_result.success:
            result.success = False

    if result.errors:
        print("\nWarnings:")
        for error in result.errors:
            print(f"  ! {error}")

    if result.success:
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organization complete!")
    else:
        print("\nOrganization completed with errors.")


def structure_info_command(args: Any) -> None:
    """Handle structure-info CLI command."""
    root_dir = args.directory

    info = get_structure_info(root_dir)

    print(f"Project Structure Info: {info['root']}")
    print("=" * 50)

    print(f"\nStructure initialized: {'Yes' if info['has_structure'] else 'No'}")

    print("\nDirectories:")
    for dir_name, exists in info['directories'].items():
        status = "exists" if exists else "missing"
        print(f"  {dir_name}: {status}")

    if info['file_counts']:
        print("\nInput file counts:")
        for folder, count in info['file_counts'].items():
            if folder != "output":
                print(f"  {folder}: {count} files")

    if info.get('output_counts'):
        print("\nOutput file counts:")
        output_counts = info['output_counts']
        if output_counts.get('root_files', 0) > 0:
            print(f"  root (unorganized): {output_counts['root_files']} files")
        for folder in ["images", "videos", "audio", "transcripts", "analysis", "pipelines"]:
            if folder in output_counts and output_counts[folder] > 0:
                print(f"  {folder}: {output_counts[folder]} files")
        if info['file_counts'].get('output'):
            print(f"  total: {info['file_counts']['output']} files")
