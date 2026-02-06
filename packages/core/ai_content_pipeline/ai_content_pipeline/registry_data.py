"""
All model definitions for the central registry.

This is the SINGLE SOURCE OF TRUTH for all AI model metadata.
When adding a new model, add ONE ModelDefinition entry here.

Source data migrated from:
- packages/providers/fal/text-to-video/.../config/constants.py (10 models)
- packages/providers/fal/image-to-video/.../config/constants.py (15 models)
- packages/providers/fal/image-to-image/.../config/constants.py (8 models)
- packages/providers/fal/avatar-generation/.../config/constants.py (10 models)
- packages/providers/fal/video-to-video/.../config/constants.py (6 models)
- packages/core/ai_content_pipeline/.../config/constants.py (pipeline-only models)
"""

from .registry import ModelDefinition, ModelRegistry


def register_all_models():
    """Register all models. Called once at import time."""

    # =========================================================================
    # TEXT-TO-VIDEO MODELS (10)
    # Source: packages/providers/fal/text-to-video/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="hailuo_pro",
        name="MiniMax Hailuo-02 Pro",
        provider="MiniMax",
        endpoint="fal-ai/minimax/hailuo-02/pro/text-to-video",
        categories=["text_to_video"],
        description="Cost-effective text-to-video with prompt optimization",
        pricing={"type": "per_video", "cost": 0.08},
        duration_options=["6"],
        aspect_ratios=["16:9"],
        resolutions=["1080p"],
        defaults={"prompt_optimizer": True},
        features=["prompt_optimizer", "1080p", "cost_effective"],
        max_duration=6,
        cost_estimate=0.08,
        processing_time=60,
    ))

    ModelRegistry.register(ModelDefinition(
        key="veo3",
        name="Google Veo 3",
        provider="Google (via FAL)",
        endpoint="fal-ai/veo3",
        categories=["text_to_video"],
        description="Premium quality with audio generation",
        pricing={"type": "per_second", "cost_no_audio": 0.50, "cost_with_audio": 0.75},
        duration_options=["5s", "6s", "7s", "8s"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p"],
        defaults={"duration": "8s", "aspect_ratio": "16:9", "generate_audio": True, "enhance_prompt": True},
        features=["audio_generation", "enhance_prompt", "negative_prompt", "seed_control"],
        max_duration=8,
        cost_estimate=4.00,
        processing_time=300,
    ))

    ModelRegistry.register(ModelDefinition(
        key="veo3_fast",
        name="Google Veo 3 Fast",
        provider="Google (via FAL)",
        endpoint="fal-ai/veo3/fast",
        categories=["text_to_video"],
        description="Fast generation with good quality",
        pricing={"type": "per_second", "cost_no_audio": 0.25, "cost_with_audio": 0.40},
        duration_options=["5s", "6s", "7s", "8s"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p"],
        defaults={"duration": "8s", "aspect_ratio": "16:9", "generate_audio": True},
        features=["audio_generation", "fast_processing", "seed_control"],
        max_duration=8,
        cost_estimate=2.00,
        processing_time=120,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_2_6_pro",
        name="Kling Video v2.6 Pro",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/v2.6/pro/text-to-video",
        categories=["text_to_video"],
        description="Professional text-to-video with audio support",
        pricing={"type": "per_second", "cost_no_audio": 0.07, "cost_with_audio": 0.14},
        duration_options=["5", "10"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p"],
        defaults={
            "duration": "5", "aspect_ratio": "16:9",
            "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5, "generate_audio": True,
        },
        features=["audio_generation", "negative_prompt", "cfg_scale", "multilingual"],
        max_duration=10,
        cost_estimate=0.35,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_3_standard",
        name="Kling Video v3 Standard",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/v3/standard/text-to-video",
        categories=["text_to_video"],
        description="Latest generation with native audio, voice control, and multi-prompt support",
        pricing={"type": "per_second", "cost_no_audio": 0.168, "cost_with_audio": 0.252, "cost_voice_control": 0.308},
        duration_options=[str(d) for d in range(3, 16)],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p"],
        defaults={
            "duration": "5", "aspect_ratio": "16:9",
            "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5, "generate_audio": False,
            "voice_ids": [], "multi_prompt": [], "shot_type": None,
        },
        features=[
            "audio_generation", "voice_control", "multi_prompt", "shot_type",
            "negative_prompt", "cfg_scale", "multilingual",
        ],
        max_duration=12,
        cost_estimate=0.84,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_3_pro",
        name="Kling Video v3 Pro",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/v3/pro/text-to-video",
        categories=["text_to_video"],
        description="Top-tier cinematic visuals with native audio, voice control, and multi-prompt support",
        pricing={"type": "per_second", "cost_no_audio": 0.224, "cost_with_audio": 0.336, "cost_voice_control": 0.392},
        duration_options=[str(d) for d in range(3, 16)],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p"],
        defaults={
            "duration": "5", "aspect_ratio": "16:9",
            "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5, "generate_audio": False,
            "voice_ids": [], "multi_prompt": [], "shot_type": None,
        },
        features=[
            "audio_generation", "voice_control", "multi_prompt", "shot_type",
            "negative_prompt", "cfg_scale", "multilingual", "professional_quality",
        ],
        max_duration=12,
        cost_estimate=1.12,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_o3_pro_t2v",
        name="Kling O3 Pro Text-to-Video",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o3/pro/text-to-video",
        categories=["text_to_video"],
        description="O3 (Omni) model with element-based character/object consistency and @ reference syntax",
        pricing={"type": "per_second", "cost_no_audio": 0.224, "cost_with_audio": 0.28},
        duration_options=["3", "5", "10", "15"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p", "1080p"],
        defaults={
            "duration": "5", "aspect_ratio": "16:9",
            "negative_prompt": None, "cfg_scale": 0.5,
            "generate_audio": True, "elements": [],
            "image_urls": [], "multi_prompt": [], "shot_type": None,
        },
        features=[
            "audio_generation", "elements", "reference_images", "reference_syntax",
            "multi_prompt", "shot_type", "negative_prompt", "cfg_scale", "professional_quality",
        ],
        max_duration=15,
        cost_estimate=1.12,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="sora_2",
        name="Sora 2",
        provider="OpenAI (via FAL)",
        endpoint="fal-ai/sora-2/text-to-video",
        categories=["text_to_video"],
        description="OpenAI's text-to-video model",
        pricing={"type": "per_second", "cost": 0.10},
        duration_options=[4, 8, 12],
        aspect_ratios=["16:9", "9:16"],
        resolutions=["720p"],
        defaults={"duration": 4, "resolution": "720p", "aspect_ratio": "16:9", "delete_video": True},
        features=["aspect_ratio", "long_duration"],
        max_duration=12,
        cost_estimate=0.40,
        processing_time=120,
    ))

    ModelRegistry.register(ModelDefinition(
        key="sora_2_pro",
        name="Sora 2 Pro",
        provider="OpenAI (via FAL)",
        endpoint="fal-ai/sora-2/text-to-video/pro",
        categories=["text_to_video"],
        description="Professional Sora with 1080p support",
        pricing={"type": "per_second", "cost_720p": 0.30, "cost_1080p": 0.50},
        duration_options=[4, 8, 12],
        aspect_ratios=["16:9", "9:16"],
        resolutions=["720p", "1080p"],
        defaults={"duration": 4, "resolution": "1080p", "aspect_ratio": "16:9", "delete_video": True},
        features=["aspect_ratio", "1080p", "long_duration"],
        max_duration=12,
        cost_estimate=2.00,
        processing_time=180,
    ))

    ModelRegistry.register(ModelDefinition(
        key="grok_imagine",
        name="xAI Grok Imagine Video",
        provider="xAI (via FAL)",
        endpoint="xai/grok-imagine-video/text-to-video",
        categories=["text_to_video"],
        description="xAI's text-to-video with native audio generation",
        pricing={"type": "per_second", "base_duration": 6, "base_cost_6s": 0.30, "cost_per_additional_second": 0.05},
        duration_options=list(range(1, 16)),
        aspect_ratios=["16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16"],
        resolutions=["480p", "720p"],
        defaults={"duration": 6, "resolution": "720p", "aspect_ratio": "16:9"},
        features=["audio_generation", "flexible_duration", "multiple_aspect_ratios"],
        max_duration=15,
        cost_estimate=0.30,
        processing_time=60,
    ))

    # =========================================================================
    # IMAGE-TO-VIDEO MODELS (15)
    # Source: packages/providers/fal/image-to-video/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="hailuo",
        name="MiniMax Hailuo-02",
        provider="MiniMax",
        endpoint="fal-ai/minimax/hailuo-02/standard/image-to-video",
        categories=["image_to_video"],
        description="Standard image-to-video with prompt optimization",
        pricing=0.05,
        duration_options=["6", "10"],
        aspect_ratios=[],
        resolutions=["768p"],
        defaults={"duration": "6", "prompt_optimizer": True},
        features=["prompt_optimizer"],
        max_duration=10,
        extended_params=["start_frame"],
        extended_features={
            "start_frame": True, "end_frame": False, "ref_images": False,
            "audio_input": False, "audio_generate": False, "ref_video": False,
        },
        cost_estimate=0.08,
        processing_time=60,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_2_1",
        name="Kling Video v2.1",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/v2.1/standard/image-to-video",
        categories=["image_to_video"],
        description="High-quality generation with negative prompts and frame interpolation",
        pricing=0.05,
        duration_options=["5", "10"],
        aspect_ratios=[],
        resolutions=["720p", "1080p"],
        defaults={"duration": "5", "negative_prompt": "blur, distort, and low quality", "cfg_scale": 0.5},
        features=["negative_prompt", "cfg_scale", "frame_interpolation"],
        max_duration=10,
        extended_params=["start_frame", "end_frame"],
        extended_features={
            "start_frame": True, "end_frame": True, "ref_images": False,
            "audio_input": False, "audio_generate": False, "ref_video": False,
        },
        cost_estimate=0.50,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_2_6_pro_i2v",
        name="Kling Video v2.6 Pro",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/v2.6/pro/image-to-video",
        categories=["image_to_video"],
        provider_key="kling_2_6_pro",
        description="Professional tier with enhanced quality and frame interpolation",
        pricing=0.10,
        duration_options=["5", "10"],
        aspect_ratios=[],
        resolutions=["720p", "1080p"],
        defaults={"duration": "5", "negative_prompt": "blur, distort, and low quality", "cfg_scale": 0.5},
        features=["negative_prompt", "cfg_scale", "professional_quality", "frame_interpolation"],
        max_duration=10,
        extended_params=["start_frame", "end_frame"],
        extended_features={
            "start_frame": True, "end_frame": True, "ref_images": False,
            "audio_input": False, "audio_generate": False, "ref_video": False,
        },
        cost_estimate=1.00,
        processing_time=120,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_3_standard_i2v",
        name="Kling Video v3 Standard",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/v3/standard/image-to-video",
        categories=["image_to_video"],
        provider_key="kling_3_standard",
        description="Latest generation with native audio, voice control, and multi-prompt support",
        pricing={"no_audio": 0.168, "audio": 0.252, "voice_control": 0.308},
        duration_options=["5", "10", "12"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p", "1080p"],
        defaults={
            "duration": "5", "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5, "generate_audio": False,
            "voice_ids": [], "multi_prompt": [], "elements": [],
            "aspect_ratio": "16:9",
        },
        features=[
            "negative_prompt", "cfg_scale", "frame_interpolation",
            "audio_generation", "voice_control", "multi_prompt", "custom_elements",
        ],
        max_duration=12,
        extended_params=["start_frame", "end_frame", "audio_generate", "elements"],
        extended_features={
            "start_frame": True, "end_frame": True, "ref_images": True,
            "audio_input": False, "audio_generate": True, "ref_video": True,
        },
        cost_estimate=0.84,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_3_pro_i2v",
        name="Kling Video v3 Pro",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/v3/pro/image-to-video",
        categories=["image_to_video"],
        provider_key="kling_3_pro",
        description="Top-tier cinematic visuals with native audio, voice control, and multi-prompt support",
        pricing={"no_audio": 0.224, "audio": 0.336, "voice_control": 0.392},
        duration_options=["5", "10", "12"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p", "1080p"],
        defaults={
            "duration": "5", "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5, "generate_audio": False,
            "voice_ids": [], "multi_prompt": [], "elements": [],
            "aspect_ratio": "16:9",
        },
        features=[
            "negative_prompt", "cfg_scale", "professional_quality", "frame_interpolation",
            "audio_generation", "voice_control", "multi_prompt", "custom_elements",
        ],
        max_duration=12,
        extended_params=["start_frame", "end_frame", "audio_generate", "elements"],
        extended_features={
            "start_frame": True, "end_frame": True, "ref_images": True,
            "audio_input": False, "audio_generate": True, "ref_video": True,
        },
        cost_estimate=1.12,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_o3_standard_i2v",
        name="Kling O3 Standard Image-to-Video",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o3/standard/image-to-video",
        categories=["image_to_video"],
        description="O3 (Omni) model with element-based character/object consistency",
        pricing={"no_audio": 0.168, "audio": 0.224},
        duration_options=["3", "5", "10", "15"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p", "1080p"],
        defaults={
            "duration": "5", "generate_audio": True,
            "elements": [], "image_urls": [],
            "aspect_ratio": "16:9", "negative_prompt": None, "cfg_scale": 0.5,
        },
        features=["audio_generation", "elements", "end_frame", "reference_images"],
        max_duration=15,
        extended_params=["start_frame", "end_frame", "audio_generate", "elements", "image_urls"],
        extended_features={
            "start_frame": True, "end_frame": True, "ref_images": True,
            "audio_input": False, "audio_generate": True, "ref_video": False, "elements": True,
        },
        cost_estimate=0.84,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_o3_pro_i2v",
        name="Kling O3 Pro Image-to-Video",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o3/pro/image-to-video",
        categories=["image_to_video"],
        description="Professional O3 (Omni) model with enhanced quality and element consistency",
        pricing={"no_audio": 0.224, "audio": 0.28},
        duration_options=["3", "5", "10", "15"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p", "1080p"],
        defaults={
            "duration": "5", "generate_audio": True,
            "elements": [], "image_urls": [],
            "aspect_ratio": "16:9", "negative_prompt": None, "cfg_scale": 0.5,
        },
        features=["audio_generation", "elements", "end_frame", "reference_images", "professional_quality"],
        max_duration=15,
        extended_params=["start_frame", "end_frame", "audio_generate", "elements", "image_urls"],
        extended_features={
            "start_frame": True, "end_frame": True, "ref_images": True,
            "audio_input": False, "audio_generate": True, "ref_video": False, "elements": True,
        },
        cost_estimate=1.12,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_o3_standard_ref",
        name="Kling O3 Standard Reference-to-Video",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o3/standard/reference-to-video",
        categories=["image_to_video"],
        description="O3 reference model with @ syntax for element-based character generation",
        pricing={"no_audio": 0.084, "audio": 0.112},
        duration_options=["3", "5", "10", "15"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p", "1080p"],
        defaults={
            "duration": "5", "generate_audio": False,
            "elements": [], "image_urls": [],
            "aspect_ratio": "16:9", "multi_prompt": [], "shot_type": None,
        },
        features=["audio_generation", "elements", "reference_images", "reference_syntax", "multi_prompt"],
        max_duration=15,
        extended_params=["start_frame", "audio_generate", "elements", "image_urls"],
        extended_features={
            "start_frame": True, "end_frame": False, "ref_images": True,
            "audio_input": False, "audio_generate": True, "ref_video": False, "elements": True,
        },
        cost_estimate=0.42,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_o3_pro_ref",
        name="Kling O3 Pro Reference-to-Video",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o3/pro/reference-to-video",
        categories=["image_to_video"],
        description="Professional O3 reference model with @ syntax and enhanced quality",
        pricing={"no_audio": 0.224, "audio": 0.28},
        duration_options=["3", "5", "10", "15"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p", "1080p"],
        defaults={
            "duration": "5", "generate_audio": False,
            "elements": [], "image_urls": [],
            "aspect_ratio": "16:9",
        },
        features=[
            "audio_generation", "elements", "end_frame", "reference_images",
            "reference_syntax", "professional_quality",
        ],
        max_duration=15,
        extended_params=["start_frame", "end_frame", "audio_generate", "elements", "image_urls"],
        extended_features={
            "start_frame": True, "end_frame": True, "ref_images": True,
            "audio_input": False, "audio_generate": True, "ref_video": False, "elements": True,
        },
        cost_estimate=1.12,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="seedance_1_5_pro",
        name="ByteDance Seedance v1.5 Pro",
        provider="ByteDance",
        endpoint="fal-ai/bytedance/seedance/v1.5/pro/image-to-video",
        categories=["image_to_video"],
        description="Advanced motion synthesis with seed control",
        pricing=0.08,
        duration_options=["5", "10"],
        aspect_ratios=[],
        resolutions=["720p", "1080p"],
        defaults={"duration": "5", "seed": None},
        features=["seed_control", "motion_quality"],
        max_duration=10,
        extended_params=["start_frame"],
        extended_features={
            "start_frame": True, "end_frame": False, "ref_images": False,
            "audio_input": False, "audio_generate": False, "ref_video": False,
        },
        cost_estimate=0.80,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="sora_2_i2v",
        name="Sora 2",
        provider="OpenAI (via FAL)",
        endpoint="fal-ai/sora-2/image-to-video",
        categories=["image_to_video"],
        provider_key="sora_2",
        description="OpenAI's image-to-video model",
        pricing=0.10,
        duration_options=[4, 8, 12],
        aspect_ratios=["auto", "9:16", "16:9"],
        resolutions=["auto", "720p"],
        defaults={"duration": 4, "resolution": "auto", "aspect_ratio": "auto", "delete_video": True},
        features=["aspect_ratio", "resolution"],
        max_duration=12,
        extended_params=["start_frame"],
        extended_features={
            "start_frame": True, "end_frame": False, "ref_images": False,
            "audio_input": False, "audio_generate": False, "ref_video": False,
        },
        cost_estimate=0.40,
        processing_time=120,
    ))

    ModelRegistry.register(ModelDefinition(
        key="sora_2_pro_i2v",
        name="Sora 2 Pro",
        provider="OpenAI (via FAL)",
        endpoint="fal-ai/sora-2/image-to-video/pro",
        categories=["image_to_video"],
        provider_key="sora_2_pro",
        description="Professional Sora with 1080p support",
        pricing=0.30,
        duration_options=[4, 8, 12],
        aspect_ratios=["auto", "9:16", "16:9"],
        resolutions=["auto", "720p", "1080p"],
        defaults={"duration": 4, "resolution": "auto", "aspect_ratio": "auto", "delete_video": True},
        features=["aspect_ratio", "resolution", "1080p"],
        max_duration=12,
        extended_params=["start_frame"],
        extended_features={
            "start_frame": True, "end_frame": False, "ref_images": False,
            "audio_input": False, "audio_generate": False, "ref_video": False,
        },
        cost_estimate=2.00,
        processing_time=180,
    ))

    ModelRegistry.register(ModelDefinition(
        key="veo_3_1_fast",
        name="Veo 3.1 Fast",
        provider="Google (via FAL)",
        endpoint="fal-ai/veo3.1/fast/image-to-video",
        categories=["image_to_video"],
        description="Fast video generation with optional audio",
        pricing=0.10,
        duration_options=["4s", "6s", "8s"],
        aspect_ratios=["auto", "16:9", "9:16"],
        resolutions=["720p", "1080p"],
        defaults={
            "duration": "8s", "resolution": "720p", "aspect_ratio": "auto",
            "generate_audio": True, "auto_fix": False,
        },
        features=["audio_generation", "auto_fix", "fast_processing"],
        max_duration=8,
        extended_params=["start_frame", "audio_generate"],
        extended_features={
            "start_frame": True, "end_frame": False, "ref_images": False,
            "audio_input": False, "audio_generate": True, "ref_video": False,
        },
        cost_estimate=1.20,
        processing_time=120,
    ))

    ModelRegistry.register(ModelDefinition(
        key="wan_2_6",
        name="Wan v2.6",
        provider="Wan",
        endpoint="wan/v2.6/image-to-video",
        categories=["image_to_video"],
        description="High-quality image-to-video with multi-shot support",
        pricing=0.10,
        duration_options=["5", "10", "15"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p", "1080p"],
        defaults={
            "duration": "5", "resolution": "1080p",
            "negative_prompt": "", "enable_prompt_expansion": True,
            "multi_shots": False, "seed": None, "enable_safety_checker": True,
        },
        features=["prompt_expansion", "multi_shots", "audio_input", "seed_control", "safety_checker"],
        max_duration=15,
        extended_params=["start_frame", "audio_input"],
        extended_features={
            "start_frame": True, "end_frame": False, "ref_images": False,
            "audio_input": True, "audio_generate": False, "ref_video": False,
        },
        cost_estimate=0.50,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="grok_imagine_i2v",
        name="xAI Grok Imagine Video",
        provider="xAI (via FAL)",
        endpoint="xai/grok-imagine-video/image-to-video",
        categories=["image_to_video"],
        provider_key="grok_imagine",
        description="xAI's image-to-video with native audio generation",
        pricing=0.05,
        duration_options=list(range(1, 16)),
        aspect_ratios=["auto", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16"],
        resolutions=["480p", "720p"],
        defaults={"duration": 6, "resolution": "720p", "aspect_ratio": "auto"},
        features=["audio_generation", "flexible_duration", "multiple_aspect_ratios"],
        max_duration=15,
        extended_params=["start_frame"],
        extended_features={
            "start_frame": True, "end_frame": False, "ref_images": False,
            "audio_input": False, "audio_generate": False, "ref_video": False,
        },
        cost_estimate=0.302,
        processing_time=60,
    ))

    # =========================================================================
    # IMAGE-TO-IMAGE MODELS (8)
    # Source: packages/providers/fal/image-to-image/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="photon",
        name="Luma Photon Flash",
        provider="Luma AI",
        endpoint="fal-ai/luma-photon/flash/modify",
        categories=["image_to_image"],
        description="Creative, personalizable, and intelligent image modification model",
        pricing={"per_megapixel": 0.019},
        duration_options=[],
        aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"],
        defaults={"strength": 0.8, "aspect_ratio": "1:1"},
        features=["Fast processing", "High-quality results", "Creative modifications",
                  "Personalizable outputs", "Aspect ratio control"],
        cost_estimate=0.02,
        processing_time=8,
    ))

    ModelRegistry.register(ModelDefinition(
        key="photon_base",
        name="Luma Photon Base",
        provider="Luma AI",
        endpoint="fal-ai/luma-photon/modify",
        categories=["image_to_image"],
        description="Most creative, personalizable, and intelligent visual model for creatives",
        pricing={"per_megapixel": 0.019},
        duration_options=[],
        aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"],
        defaults={"strength": 0.8, "aspect_ratio": "1:1"},
        features=["Step-function change in cost", "High-quality image generation",
                  "Creative image editing", "Prompt-based modifications", "Commercial use ready"],
        cost_estimate=0.03,
        processing_time=12,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kontext",
        name="FLUX Kontext Dev",
        provider="Black Forest Labs",
        endpoint="fal-ai/flux-kontext/dev",
        categories=["image_to_image"],
        description="Frontier image editing model focused on contextual understanding",
        pricing={"per_image": 0.025},
        duration_options=[],
        aspect_ratios=["auto"],
        defaults={"num_inference_steps": 28, "guidance_scale": 2.5, "resolution_mode": "auto"},
        features=["Contextual understanding", "Nuanced modifications",
                  "Style preservation", "Iterative editing", "Precise control"],
        cost_estimate=0.025,
        processing_time=15,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kontext_multi",
        name="FLUX Kontext [max] Multi",
        provider="Black Forest Labs",
        endpoint="fal-ai/flux-pro/kontext/max/multi",
        categories=["image_to_image"],
        description="Experimental multi-image version of FLUX Kontext [max] with advanced capabilities",
        pricing={"per_image": 0.04},
        duration_options=[],
        aspect_ratios=["21:9", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "9:21"],
        defaults={},
        features=["Multi-image input support", "Advanced contextual understanding",
                  "Experimental capabilities", "High-quality results",
                  "Safety tolerance control", "Multiple output formats"],
        cost_estimate=0.04,
        processing_time=25,
    ))

    ModelRegistry.register(ModelDefinition(
        key="seededit",
        name="ByteDance SeedEdit v3",
        provider="ByteDance",
        endpoint="fal-ai/bytedance/seededit/v3/edit-image",
        categories=["image_to_image"],
        description="Accurate image editing model with excellent content preservation",
        pricing={"per_image": 0.02},
        duration_options=[],
        aspect_ratios=[],
        defaults={"guidance_scale": 0.5},
        features=["Accurate editing instruction following", "Effective content preservation",
                  "Commercial use ready", "Simple parameter set",
                  "High-quality results", "ByteDance developed"],
        cost_estimate=0.02,
        processing_time=10,
    ))

    ModelRegistry.register(ModelDefinition(
        key="clarity",
        name="Clarity Upscaler",
        provider="FAL AI",
        endpoint="fal-ai/clarity-upscaler",
        categories=["image_to_image"],
        description="High-quality image upscaling with optional creative enhancement",
        pricing={"per_image": 0.05},
        duration_options=[],
        aspect_ratios=[],
        defaults={"scale": 2, "enable_enhancement": True},
        features=["Up to 4x upscaling", "Optional creative enhancement",
                  "Maintains image quality", "Fast processing",
                  "Commercial use ready", "Prompt-based enhancement"],
        cost_estimate=0.05,
        processing_time=30,
    ))

    ModelRegistry.register(ModelDefinition(
        key="nano_banana_pro_edit",
        name="Nano Banana Pro Edit",
        provider="FAL AI",
        endpoint="fal-ai/nano-banana-pro/edit",
        categories=["image_to_image"],
        description="Multi-image editing and composition model with resolution control",
        pricing={"1K_2K": 0.015, "4K": 0.030},
        duration_options=[],
        aspect_ratios=[
            "auto", "21:9", "16:9", "3:2", "4:3", "5:4",
            "1:1", "4:5", "3:4", "2:3", "9:16",
        ],
        resolutions=["1K", "2K", "4K"],
        defaults={
            "aspect_ratio": "auto", "resolution": "1K",
            "output_format": "png", "num_images": 1, "sync_mode": True,
        },
        features=["Multi-image input (up to 4)", "11 aspect ratio options",
                  "Up to 4K resolution", "Optional web search enhancement",
                  "Fast processing", "Commercial use ready"],
        cost_estimate=0.015,
        processing_time=8,
    ))

    ModelRegistry.register(ModelDefinition(
        key="gpt_image_1_5_edit",
        name="GPT Image 1.5 Edit",
        provider="OpenAI (via FAL)",
        endpoint="fal-ai/gpt-image-1.5/edit",
        categories=["image_to_image"],
        description="GPT-powered image editing with natural language understanding",
        pricing={"per_image": 0.02},
        duration_options=[],
        aspect_ratios=[],
        defaults={"strength": 0.75},
        features=["GPT-powered editing", "Natural language understanding",
                  "High-quality results", "Creative modifications", "Commercial use ready"],
        cost_estimate=0.02,
        processing_time=10,
    ))

    # =========================================================================
    # AVATAR MODELS (10)
    # Source: packages/providers/fal/avatar-generation/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="omnihuman_v1_5",
        name="OmniHuman v1.5 (ByteDance)",
        provider="ByteDance",
        endpoint="fal-ai/bytedance/omnihuman/v1.5",
        categories=["avatar"],
        description="High-quality audio-driven human animation",
        pricing={"per_second": 0.16},
        duration_options=[],
        aspect_ratios=[],
        resolutions=["720p", "1080p"],
        defaults={"resolution": "1080p", "turbo_mode": False},
        features=["audio_driven", "high_quality"],
        max_duration=30,
        input_requirements={"required": ["image_url", "audio_url"], "optional": ["prompt", "turbo_mode", "resolution"]},
        model_info={"max_durations": {"1080p": 30, "720p": 60}},
        cost_estimate=0.80,
        processing_time=60,
    ))

    ModelRegistry.register(ModelDefinition(
        key="fabric_1_0",
        name="VEED Fabric 1.0",
        provider="VEED",
        endpoint="veed/fabric-1.0",
        categories=["avatar"],
        description="Cost-effective lip-sync avatar generation",
        pricing={"480p": 0.08, "720p": 0.15},
        duration_options=[],
        aspect_ratios=[],
        resolutions=["480p", "720p"],
        defaults={"resolution": "720p"},
        features=["lipsync", "cost_effective"],
        max_duration=120,
        input_requirements={"required": ["image_url", "audio_url", "resolution"], "optional": []},
        cost_estimate=0.75,
        processing_time=45,
    ))

    ModelRegistry.register(ModelDefinition(
        key="fabric_1_0_fast",
        name="VEED Fabric 1.0 Fast",
        provider="VEED",
        endpoint="veed/fabric-1.0/fast",
        categories=["avatar"],
        description="Speed-optimized lip-sync avatar generation",
        pricing={"480p": 0.10, "720p": 0.19},
        duration_options=[],
        aspect_ratios=[],
        resolutions=["480p", "720p"],
        defaults={"resolution": "720p"},
        features=["lipsync", "fast_processing"],
        max_duration=120,
        input_requirements={"required": ["image_url", "audio_url", "resolution"], "optional": []},
        cost_estimate=0.94,
        processing_time=30,
    ))

    ModelRegistry.register(ModelDefinition(
        key="fabric_1_0_text",
        name="VEED Fabric 1.0 Text-to-Speech",
        provider="VEED",
        endpoint="veed/fabric-1.0/text",
        categories=["avatar"],
        description="Text-to-speech + lip-sync avatar generation",
        pricing={"480p": 0.08, "720p": 0.15},
        duration_options=[],
        aspect_ratios=[],
        resolutions=["480p", "720p"],
        defaults={"resolution": "720p"},
        features=["text_to_speech", "lipsync"],
        max_duration=120,
        input_requirements={"required": ["image_url", "text", "resolution"], "optional": ["voice_description"]},
        cost_estimate=0.75,
        processing_time=50,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_ref_to_video",
        name="Kling O1 Reference-to-Video",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o1/standard/reference-to-video",
        categories=["avatar"],
        description="Character consistency with reference image",
        pricing={"per_second": 0.112},
        duration_options=["5", "10"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        defaults={"duration": "5", "aspect_ratio": "16:9"},
        features=["character_consistency", "reference_image"],
        max_duration=10,
        input_requirements={
            "required": ["prompt", "reference_images"],
            "optional": ["duration", "aspect_ratio", "audio_url", "face_id"],
        },
        cost_estimate=0.56,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_v2v_reference",
        name="Kling O1 V2V Reference",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o1/standard/video-to-video/reference",
        categories=["avatar"],
        description="Style-guided video transformation",
        pricing={"per_second": 0.168},
        duration_options=["5", "10"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        defaults={"duration": "5", "aspect_ratio": "16:9"},
        features=["style_transfer", "video_reference"],
        max_duration=10,
        input_requirements={
            "required": ["prompt", "video_url"],
            "optional": ["duration", "aspect_ratio", "audio_url", "face_id"],
        },
        cost_estimate=0.84,
        processing_time=90,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_v2v_edit",
        name="Kling O1 V2V Edit",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o1/standard/video-to-video/edit",
        categories=["avatar"],
        description="Targeted video editing with prompts",
        pricing={"per_second": 0.168},
        duration_options=[],
        aspect_ratios=["16:9", "9:16", "1:1"],
        defaults={"aspect_ratio": "16:9"},
        features=["video_editing", "prompt_based"],
        max_duration=10,
        input_requirements={"required": ["video_url", "prompt"], "optional": ["mask_url"]},
        cost_estimate=0.84,
        processing_time=60,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_motion_control",
        name="Kling v2.6 Motion Control",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/v2.6/standard/motion-control",
        categories=["avatar"],
        description="Motion transfer from video to image",
        pricing={"per_second": 0.06},
        duration_options=[],
        aspect_ratios=[],
        defaults={"character_orientation": "video", "keep_original_sound": True},
        features=["motion_transfer", "audio_preservation"],
        max_duration=30,
        input_requirements={
            "required": ["image_url", "video_url"],
            "optional": ["character_orientation", "keep_original_sound", "prompt"],
        },
        model_info={"max_durations": {"video": 30, "image": 10}},
        cost_estimate=0.60,
        processing_time=60,
    ))

    ModelRegistry.register(ModelDefinition(
        key="multitalk",
        name="AI Avatar Multi (FAL)",
        provider="FAL AI",
        endpoint="fal-ai/ai-avatar/multi",
        categories=["avatar"],
        description="Multi-person conversational avatar generation",
        pricing={"base": 0.10, "720p_multiplier": 2.0, "extended_frames_multiplier": 1.25},
        duration_options=[],
        aspect_ratios=[],
        resolutions=["480p", "720p"],
        defaults={"num_frames": 81, "resolution": "480p", "acceleration": "regular"},
        features=["multi_person", "conversation", "audio_driven"],
        max_duration=60,
        input_requirements={
            "required": ["image_url", "first_audio_url", "prompt"],
            "optional": ["second_audio_url", "num_frames", "resolution", "seed", "acceleration", "use_only_first_audio"],
        },
        cost_estimate=0.10,
        processing_time=60,
    ))

    ModelRegistry.register(ModelDefinition(
        key="grok_video_edit",
        name="xAI Grok Video Edit",
        provider="xAI (via FAL)",
        endpoint="xai/grok-imagine-video/edit-video",
        categories=["avatar"],
        description="Video editing with AI-powered prompts",
        pricing={"input_per_second": 0.01, "output_per_second": 0.05},
        duration_options=[],
        aspect_ratios=[],
        resolutions=["auto", "480p", "720p"],
        defaults={"resolution": "auto"},
        features=["video_editing", "prompt_based", "colorize"],
        max_duration=8,
        input_requirements={"required": ["video_url", "prompt"], "optional": ["resolution"]},
        cost_estimate=0.36,
        processing_time=45,
    ))

    # =========================================================================
    # VIDEO-TO-VIDEO MODELS (6)
    # Source: packages/providers/fal/video-to-video/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="thinksound",
        name="ThinkSound",
        provider="FAL AI",
        endpoint="fal-ai/thinksound",
        categories=["add_audio"],
        description="AI-powered video audio generation that creates realistic sound effects",
        pricing={"per_second": 0.001},
        duration_options=[],
        aspect_ratios=[],
        defaults={"seed": None, "prompt": None},
        features=["Automatic sound effect generation", "Text prompt guidance",
                  "Video context understanding", "High-quality audio synthesis",
                  "Commercial use license"],
        max_duration=300,
        cost_estimate=0.05,
        processing_time=45,
    ))

    ModelRegistry.register(ModelDefinition(
        key="topaz",
        name="Topaz Video Upscale",
        provider="Topaz Labs (via FAL)",
        endpoint="fal-ai/topaz/upscale/video",
        categories=["upscale_video"],
        description="Professional-grade video upscaling with frame interpolation",
        pricing={"per_video": "commercial"},
        duration_options=[],
        aspect_ratios=[],
        defaults={"upscale_factor": 2, "target_fps": None},
        features=["Up to 4x upscaling", "Frame rate enhancement up to 120 FPS",
                  "Proteus v4 upscaling engine", "Apollo v8 frame interpolation",
                  "Professional quality enhancement", "Commercial use license"],
        cost_estimate=1.50,
        processing_time=120,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_o3_standard_edit",
        name="Kling O3 Standard Video Edit",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o3/standard/video-to-video/edit",
        categories=["video_to_video"],
        description="O3 video editing with element replacement and @ reference syntax",
        pricing={"per_second": 0.252},
        duration_options=["3", "5", "10", "15"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        defaults={"duration": "5", "elements": [], "image_urls": [], "aspect_ratio": "16:9"},
        features=["Element-based object/character replacement", "Environment modification",
                  "@ reference syntax", "Reference image integration"],
        max_duration=15,
        cost_estimate=1.26,
        processing_time=60,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_o3_pro_edit",
        name="Kling O3 Pro Video Edit",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o3/pro/video-to-video/edit",
        categories=["video_to_video"],
        description="Professional O3 video editing with enhanced quality and element replacement",
        pricing={"per_second": 0.336},
        duration_options=["3", "5", "10", "15"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        defaults={"duration": "5", "elements": [], "image_urls": [], "aspect_ratio": "16:9"},
        features=["Professional-tier quality", "Element-based object/character replacement",
                  "Environment modification", "@ reference syntax", "Reference image integration"],
        max_duration=15,
        cost_estimate=1.68,
        processing_time=60,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_o3_standard_v2v_ref",
        name="Kling O3 Standard V2V Reference",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o3/standard/video-to-video/reference",
        categories=["video_to_video"],
        description="O3 video-to-video with style transfer and element consistency",
        pricing={"per_second": 0.252},
        duration_options=["3", "5", "10", "15"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        defaults={"duration": "5", "elements": [], "image_urls": [], "aspect_ratio": "16:9", "keep_audio": False},
        features=["Style transfer from reference images", "Element integration with consistency",
                  "@ reference syntax", "Optional audio preservation"],
        max_duration=15,
        cost_estimate=1.26,
        processing_time=60,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_o3_pro_v2v_ref",
        name="Kling O3 Pro V2V Reference",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/o3/pro/video-to-video/reference",
        categories=["video_to_video"],
        description="Professional O3 video-to-video with style transfer and enhanced quality",
        pricing={"per_second": 0.336},
        duration_options=["3", "5", "10", "15"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        defaults={"duration": "5", "elements": [], "image_urls": [], "aspect_ratio": "16:9", "keep_audio": False},
        features=["Professional-tier quality", "Style transfer from reference images",
                  "Element integration with consistency", "@ reference syntax",
                  "Optional audio preservation"],
        max_duration=15,
        cost_estimate=1.68,
        processing_time=60,
    ))

    # =========================================================================
    # TEXT-TO-IMAGE MODELS (8)
    # Source: packages/core/ai_content_pipeline/.../config/constants.py
    # (Pipeline-only models, no dedicated provider package)
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="flux_dev",
        name="FLUX.1 Dev",
        provider="Black Forest Labs",
        endpoint="fal-ai/flux/dev",
        categories=["text_to_image"],
        description="Highest quality 12B parameter text-to-image model",
        pricing={"per_image": 0.003},
        duration_options=[],
        aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4"],
        defaults={"aspect_ratio": "16:9", "style": "cinematic"},
        features=["high_quality", "12B_parameters"],
        cost_estimate=0.003,
        processing_time=15,
    ))

    ModelRegistry.register(ModelDefinition(
        key="flux_schnell",
        name="FLUX.1 Schnell",
        provider="Black Forest Labs",
        endpoint="fal-ai/flux/schnell",
        categories=["text_to_image"],
        description="Fastest inference speed text-to-image model",
        pricing={"per_image": 0.001},
        duration_options=[],
        aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4"],
        defaults={"aspect_ratio": "16:9"},
        features=["fast_inference", "cost_effective"],
        cost_estimate=0.001,
        processing_time=5,
    ))

    ModelRegistry.register(ModelDefinition(
        key="imagen4",
        name="Google Imagen 4",
        provider="Google (via FAL)",
        endpoint="fal-ai/imagen4/preview",
        categories=["text_to_image"],
        description="Google's photorealistic text-to-image model",
        pricing={"per_image": 0.004},
        duration_options=[],
        aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4"],
        defaults={"aspect_ratio": "16:9"},
        features=["photorealistic", "high_quality"],
        cost_estimate=0.004,
        processing_time=20,
    ))

    ModelRegistry.register(ModelDefinition(
        key="seedream_v3",
        name="Seedream v3",
        provider="ByteDance",
        endpoint="fal-ai/seedream-3",
        categories=["text_to_image"],
        description="Multilingual text-to-image model",
        pricing={"per_image": 0.002},
        duration_options=[],
        aspect_ratios=["1:1", "16:9", "9:16"],
        defaults={"aspect_ratio": "16:9"},
        features=["multilingual", "cost_effective"],
        cost_estimate=0.002,
        processing_time=10,
    ))

    ModelRegistry.register(ModelDefinition(
        key="seedream3",
        name="Seedream-3",
        provider="ByteDance (via Replicate)",
        endpoint="replicate/seedream-3",
        categories=["text_to_image"],
        description="High-resolution text-to-image model",
        pricing={"per_image": 0.003},
        duration_options=[],
        aspect_ratios=["1:1", "16:9", "9:16"],
        defaults={"aspect_ratio": "16:9"},
        features=["high_resolution"],
        cost_estimate=0.003,
        processing_time=15,
    ))

    ModelRegistry.register(ModelDefinition(
        key="gen4",
        name="Runway Gen-4",
        provider="Runway (via Replicate)",
        endpoint="replicate/gen4",
        categories=["text_to_image"],
        description="Multi-reference guided image generation",
        pricing={"per_image": 0.08},
        duration_options=[],
        aspect_ratios=["1:1", "16:9", "9:16"],
        defaults={"aspect_ratio": "16:9"},
        features=["reference_guided", "cinematic"],
        cost_estimate=0.08,
        processing_time=20,
    ))

    ModelRegistry.register(ModelDefinition(
        key="nano_banana_pro",
        name="Nano Banana Pro",
        provider="FAL AI",
        endpoint="fal-ai/nano-banana-pro",
        categories=["text_to_image"],
        description="Fast, high-quality text-to-image generation",
        pricing={"per_image": 0.002},
        duration_options=[],
        aspect_ratios=["1:1", "16:9", "9:16"],
        defaults={"aspect_ratio": "16:9"},
        features=["fast_processing", "high_quality"],
        cost_estimate=0.002,
        processing_time=5,
    ))

    ModelRegistry.register(ModelDefinition(
        key="gpt_image_1_5",
        name="GPT Image 1.5",
        provider="OpenAI (via FAL)",
        endpoint="fal-ai/gpt-image-1.5",
        categories=["text_to_image"],
        description="GPT-powered image generation",
        pricing={"per_image": 0.003},
        duration_options=[],
        aspect_ratios=["1:1", "16:9", "9:16"],
        defaults={"aspect_ratio": "16:9"},
        features=["gpt_powered", "natural_language"],
        cost_estimate=0.003,
        processing_time=10,
    ))

    # =========================================================================
    # TEXT-TO-SPEECH MODELS (3)
    # Source: packages/core/ai_content_pipeline/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="elevenlabs",
        name="ElevenLabs TTS",
        provider="ElevenLabs",
        endpoint="elevenlabs/tts",
        categories=["text_to_speech"],
        description="High quality text-to-speech",
        pricing={"per_character": 0.00003},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["high_quality", "professional"],
        cost_estimate=0.05,
        processing_time=15,
    ))

    ModelRegistry.register(ModelDefinition(
        key="elevenlabs_turbo",
        name="ElevenLabs Turbo",
        provider="ElevenLabs",
        endpoint="elevenlabs/tts/turbo",
        categories=["text_to_speech"],
        description="Fast text-to-speech",
        pricing={"per_character": 0.00002},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["fast_processing"],
        cost_estimate=0.03,
        processing_time=8,
    ))

    ModelRegistry.register(ModelDefinition(
        key="elevenlabs_v3",
        name="ElevenLabs v3",
        provider="ElevenLabs",
        endpoint="elevenlabs/tts/v3",
        categories=["text_to_speech"],
        description="Latest ElevenLabs text-to-speech model",
        pricing={"per_character": 0.00005},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["latest_generation", "high_quality"],
        cost_estimate=0.08,
        processing_time=20,
    ))

    # =========================================================================
    # IMAGE UNDERSTANDING MODELS (7)
    # Source: packages/core/ai_content_pipeline/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="gemini_describe",
        name="Gemini Describe",
        provider="Google",
        endpoint="google/gemini/describe",
        categories=["image_understanding"],
        description="Basic image description",
        pricing={"per_request": 0.001},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["image_description", "basic"],
        cost_estimate=0.001,
        processing_time=3,
    ))

    ModelRegistry.register(ModelDefinition(
        key="gemini_detailed",
        name="Gemini Detailed",
        provider="Google",
        endpoint="google/gemini/detailed",
        categories=["image_understanding"],
        description="Detailed image analysis",
        pricing={"per_request": 0.002},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["image_analysis", "detailed"],
        cost_estimate=0.002,
        processing_time=5,
    ))

    ModelRegistry.register(ModelDefinition(
        key="gemini_classify",
        name="Gemini Classify",
        provider="Google",
        endpoint="google/gemini/classify",
        categories=["image_understanding"],
        description="Image classification and categorization",
        pricing={"per_request": 0.001},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["classification", "categorization"],
        cost_estimate=0.001,
        processing_time=3,
    ))

    ModelRegistry.register(ModelDefinition(
        key="gemini_objects",
        name="Gemini Objects",
        provider="Google",
        endpoint="google/gemini/objects",
        categories=["image_understanding"],
        description="Object detection and identification",
        pricing={"per_request": 0.002},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["object_detection", "identification"],
        cost_estimate=0.002,
        processing_time=4,
    ))

    ModelRegistry.register(ModelDefinition(
        key="gemini_ocr",
        name="Gemini OCR",
        provider="Google",
        endpoint="google/gemini/ocr",
        categories=["image_understanding"],
        description="Text extraction (OCR)",
        pricing={"per_request": 0.001},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["ocr", "text_extraction"],
        cost_estimate=0.001,
        processing_time=3,
    ))

    ModelRegistry.register(ModelDefinition(
        key="gemini_composition",
        name="Gemini Composition",
        provider="Google",
        endpoint="google/gemini/composition",
        categories=["image_understanding"],
        description="Artistic and technical composition analysis",
        pricing={"per_request": 0.002},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["composition_analysis", "artistic"],
        cost_estimate=0.002,
        processing_time=5,
    ))

    ModelRegistry.register(ModelDefinition(
        key="gemini_qa",
        name="Gemini Q&A",
        provider="Google",
        endpoint="google/gemini/qa",
        categories=["image_understanding"],
        description="Question and answer system for images",
        pricing={"per_request": 0.001},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["qa", "interactive"],
        cost_estimate=0.001,
        processing_time=4,
    ))

    # =========================================================================
    # PROMPT GENERATION MODELS (5)
    # Source: packages/core/ai_content_pipeline/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="openrouter_video_prompt",
        name="OpenRouter Video Prompt",
        provider="OpenRouter",
        endpoint="openrouter/video-prompt",
        categories=["prompt_generation"],
        description="General video prompt generation",
        pricing={"per_request": 0.002},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["prompt_generation", "general"],
        cost_estimate=0.002,
        processing_time=4,
    ))

    ModelRegistry.register(ModelDefinition(
        key="openrouter_video_cinematic",
        name="OpenRouter Video Cinematic",
        provider="OpenRouter",
        endpoint="openrouter/video-cinematic",
        categories=["prompt_generation"],
        description="Cinematic style video prompt generation",
        pricing={"per_request": 0.002},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["prompt_generation", "cinematic"],
        cost_estimate=0.002,
        processing_time=5,
    ))

    ModelRegistry.register(ModelDefinition(
        key="openrouter_video_realistic",
        name="OpenRouter Video Realistic",
        provider="OpenRouter",
        endpoint="openrouter/video-realistic",
        categories=["prompt_generation"],
        description="Realistic style video prompt generation",
        pricing={"per_request": 0.002},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["prompt_generation", "realistic"],
        cost_estimate=0.002,
        processing_time=4,
    ))

    ModelRegistry.register(ModelDefinition(
        key="openrouter_video_artistic",
        name="OpenRouter Video Artistic",
        provider="OpenRouter",
        endpoint="openrouter/video-artistic",
        categories=["prompt_generation"],
        description="Artistic style video prompt generation",
        pricing={"per_request": 0.002},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["prompt_generation", "artistic"],
        cost_estimate=0.002,
        processing_time=5,
    ))

    ModelRegistry.register(ModelDefinition(
        key="openrouter_video_dramatic",
        name="OpenRouter Video Dramatic",
        provider="OpenRouter",
        endpoint="openrouter/video-dramatic",
        categories=["prompt_generation"],
        description="Dramatic style video prompt generation",
        pricing={"per_request": 0.002},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["prompt_generation", "dramatic"],
        cost_estimate=0.002,
        processing_time=5,
    ))

    # =========================================================================
    # SPEECH-TO-TEXT MODELS (1)
    # Source: packages/core/ai_content_pipeline/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="scribe_v2",
        name="ElevenLabs Scribe v2",
        provider="ElevenLabs (via FAL)",
        endpoint="fal-ai/elevenlabs/scribe/v2",
        categories=["speech_to_text"],
        description="Fast, accurate transcription with speaker diarization",
        pricing={"per_minute": 0.008},
        duration_options=[],
        aspect_ratios=[],
        defaults={},
        features=["transcription", "speaker_diarization", "multilingual"],
        cost_estimate=0.08,
        processing_time=15,
    ))


# Auto-register on import
register_all_models()
