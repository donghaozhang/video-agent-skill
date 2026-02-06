#!/usr/bin/env python3
"""Validate model registry consistency.

Run: python scripts/validate_registry.py
Exit code 0 = all validations passed.
"""

import sys


def validate():
    """Run all validation checks."""
    errors = []

    from ai_content_pipeline.registry import ModelRegistry
    import ai_content_pipeline.registry_data  # noqa: F401

    all_keys = ModelRegistry.all_keys()

    # 1. Check minimum model count
    if len(all_keys) < 50:
        errors.append(f"Expected 50+ models, found {len(all_keys)}")

    # 2. Every model has required fields
    for key in all_keys:
        m = ModelRegistry.get(key)
        if not m.name:
            errors.append(f"{key}: missing name")
        if not m.endpoint:
            errors.append(f"{key}: missing endpoint")
        if not m.categories:
            errors.append(f"{key}: missing categories")

    # 3. All endpoints have non-empty values
    valid_prefixes = (
        "fal-ai/", "veed/", "xai/", "wan/",
        "replicate/", "elevenlabs/", "google/",
        "openrouter/",
    )
    for key in all_keys:
        m = ModelRegistry.get(key)
        if m.endpoint and not m.endpoint.startswith(valid_prefixes):
            errors.append(f"{key}: endpoint '{m.endpoint}' has unexpected prefix")

    # 4. No duplicate keys
    if len(all_keys) != len(set(all_keys)):
        errors.append("Duplicate model keys detected")

    # 5. Check model classes exist for text-to-video
    try:
        from fal_text_to_video.generator import MODEL_CLASSES as t2v_classes
        for key in ModelRegistry.keys_for_category("text_to_video"):
            if key not in t2v_classes:
                # Some models use the pipeline path directly without a model class
                pipeline_only = {"hailuo_pro", "veo3", "veo3_fast"}
                if key not in pipeline_only:
                    errors.append(f"text_to_video model '{key}' has no class")
    except ImportError:
        errors.append("Could not import fal_text_to_video.generator")

    # 6. Check image-to-video models
    try:
        from fal_image_to_video.generator import FALImageToVideoGenerator
        gen = FALImageToVideoGenerator.__new__(FALImageToVideoGenerator)
        gen.models = FALImageToVideoGenerator._build_models()
        i2v_keys = ModelRegistry.provider_keys_for_category("image_to_video")
        for key in i2v_keys:
            if key not in gen.models:
                errors.append(f"image_to_video model '{key}' has no class")
    except ImportError:
        errors.append("Could not import fal_image_to_video.generator")

    # 7. Check avatar models
    try:
        from fal_avatar import FALAvatarGenerator
        gen = FALAvatarGenerator()
        avatar_keys = ModelRegistry.keys_for_category("avatar")
        for key in avatar_keys:
            if key not in gen.models:
                errors.append(f"avatar model '{key}' has no class")
    except ImportError:
        errors.append("Could not import fal_avatar")

    # 8. Provider constants derive from registry (spot check)
    try:
        from fal_text_to_video.config.constants import SUPPORTED_MODELS
        registry_t2v = ModelRegistry.keys_for_category("text_to_video")
        for key in registry_t2v:
            if key not in SUPPORTED_MODELS:
                errors.append(f"t2v SUPPORTED_MODELS missing '{key}'")
    except ImportError:
        errors.append("Could not import fal_text_to_video.config.constants")

    # Report
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  ERROR: {e}")
        return 1

    print(f"All validations passed! ({len(all_keys)} models registered)")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
