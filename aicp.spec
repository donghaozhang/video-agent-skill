# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for the aicp (AI Content Pipeline) binary.

Build locally:  pyinstaller aicp.spec
Output:         dist/aicp (or dist/aicp.exe on Windows)

This spec file ensures all provider packages and config data are bundled,
even when PyInstaller's static analysis can't discover them.
"""

import sys
from pathlib import Path

block_cipher = None

# Project root (where this spec file lives)
PROJECT_ROOT = Path(SPECPATH)

a = Analysis(
    [str(PROJECT_ROOT / 'aicp_entry.py')],
    pathex=[
        str(PROJECT_ROOT),
        # Package source directories so PyInstaller can discover modules
        # (editable installs are not reliably resolved by PyInstaller)
        str(PROJECT_ROOT / 'packages' / 'core' / 'ai_content_pipeline'),
        str(PROJECT_ROOT / 'packages' / 'core'),
        str(PROJECT_ROOT / 'packages' / 'providers' / 'fal' / 'text-to-video'),
        str(PROJECT_ROOT / 'packages' / 'providers' / 'fal' / 'image-to-video'),
        str(PROJECT_ROOT / 'packages' / 'providers' / 'fal' / 'image-to-image'),
        str(PROJECT_ROOT / 'packages' / 'providers' / 'fal' / 'video-to-video'),
        str(PROJECT_ROOT / 'packages' / 'providers' / 'fal' / 'avatar-generation'),
    ],
    binaries=[],
    datas=[
        # Config YAML files needed at runtime
        (str(PROJECT_ROOT / 'packages' / 'core' / 'ai_content_pipeline' / 'ai_content_pipeline' / 'config'), 'ai_content_pipeline/config'),
    ],
    hiddenimports=[
        # Core pipeline
        'ai_content_pipeline',
        'ai_content_pipeline.__main__',
        'ai_content_pipeline._version',
        'ai_content_pipeline.config',
        'ai_content_pipeline.config.constants',
        'ai_content_pipeline.models',
        'ai_content_pipeline.pipeline',
        'ai_content_pipeline.pipeline.manager',
        'ai_content_pipeline.pipeline.executor',
        'ai_content_pipeline.pipeline.step_executors',
        'ai_content_pipeline.cli',
        'ai_content_pipeline.cli.exit_codes',
        'ai_content_pipeline.cli.interactive',
        'ai_content_pipeline.cli.output',
        'ai_content_pipeline.cli.paths',
        'ai_content_pipeline.cli.stream',
        'ai_content_pipeline.registry',
        'ai_content_pipeline.registry_data',
        'ai_content_pipeline.video_analysis',
        'ai_content_pipeline.motion_transfer',
        'ai_content_pipeline.speech_to_text',
        'ai_content_pipeline.grid_generator',
        'ai_content_pipeline.project_structure_cli',
        # FAL providers
        'fal_text_to_video',
        'fal_text_to_video.config',
        'fal_text_to_video.models',
        'fal_text_to_video.utils',
        'fal_image_to_video',
        'fal_image_to_video.config',
        'fal_image_to_video.models',
        'fal_image_to_video.utils',
        'fal_image_to_image',
        'fal_image_to_image.config',
        'fal_image_to_image.models',
        'fal_image_to_image.utils',
        'fal_video_to_video',
        'fal_video_to_video.config',
        'fal_video_to_video.models',
        'fal_video_to_video.utils',
        'fal_avatar',
        'fal_avatar.config',
        'fal_avatar.models',
        # Platform
        'ai_content_platform',
        # Third-party hidden imports PyInstaller often misses
        'yaml',
        'dotenv',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy optional deps to keep binary small
        'matplotlib',
        'jupyter',
        'notebook',
        'ipython',
        'scipy',
        'numpy',
        'cv2',
        'tkinter',
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='aicp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
