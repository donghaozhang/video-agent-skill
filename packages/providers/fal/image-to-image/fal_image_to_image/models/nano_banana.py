"""
Nano Banana Pro Edit model implementation

This model supports multi-image editing and composition with resolution control.
"""

import logging
from typing import Dict, Any, List, Optional
from .base import BaseModel

logger = logging.getLogger(__name__)
from ..config.constants import MODEL_INFO, DEFAULT_VALUES
from ..utils.validators import (
    validate_nano_banana_aspect_ratio,
    validate_resolution,
    validate_image_urls,
    validate_num_images,
    validate_output_format
)


class NanoBananaProEditModel(BaseModel):
    """
    Nano Banana Pro Edit model for multi-image editing and composition.

    Unlike other image-to-image models, this accepts multiple input images
    and supports resolution selection (1K, 2K, 4K).

    API Parameters:
        - aspect_ratio: auto, 21:9, 16:9, 3:2, 4:3, 5:4, 1:1, 4:5, 3:4, 2:3, 9:16
        - resolution: 1K, 2K, 4K
        - output_format: jpeg, png, webp
        - num_images: 1-4
        - enable_web_search: bool

    Pricing:
        - 1K/2K: $0.015 per image
        - 4K: $0.030 per image (double rate)
        - Web search: +$0.015 per request
    """

    MODEL_KEY = "nano_banana_pro_edit"

    def __init__(self):
        """Initialize the Nano Banana Pro Edit model."""
        super().__init__("nano_banana_pro_edit")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate Nano Banana Pro Edit parameters.

        Returns:
            Dictionary of validated parameters
        """
        defaults = DEFAULT_VALUES.get("nano_banana_pro_edit", {})

        # Get parameters with defaults
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "auto"))
        resolution = kwargs.get("resolution", defaults.get("resolution", "1K"))
        output_format = kwargs.get("output_format", defaults.get("output_format", "png"))
        num_images = kwargs.get("num_images", defaults.get("num_images", 1))
        enable_web_search = kwargs.get("enable_web_search", False)
        sync_mode = kwargs.get("sync_mode", defaults.get("sync_mode", True))

        # Validate all parameters
        validated_aspect_ratio = validate_nano_banana_aspect_ratio(aspect_ratio)
        validated_resolution = validate_resolution(resolution)
        validated_output_format = validate_output_format(output_format)
        validated_num_images = validate_num_images(num_images, max_images=4)

        # Warn about 4K resolution cost
        if validated_resolution == "4K":
            logger.warning("4K resolution costs $0.030/image (double the 1K/2K rate)")

        # Warn about web search cost
        if enable_web_search:
            logger.info("Web search enabled: +$0.015 per request")

        return {
            "aspect_ratio": validated_aspect_ratio,
            "resolution": validated_resolution,
            "output_format": validated_output_format,
            "num_images": validated_num_images,
            "enable_web_search": bool(enable_web_search),
            "sync_mode": bool(sync_mode)
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Prepare API arguments for Nano Banana Pro Edit.

        This model supports multiple input images via image_urls parameter.
        For backwards compatibility, image_url (singular) is also accepted.

        Note:
            Callers should invoke validate_parameters() before this method
            to ensure kwargs values (aspect_ratio, resolution, output_format,
            num_images) are valid. The base class's generate() method handles
            this automatically.

        Args:
            prompt: Edit instruction
            image_url: Single image URL (backwards compatibility)
            image_urls: List of image URLs (preferred)
            **kwargs: Pre-validated parameters from validate_parameters()

        Returns:
            Dictionary of API arguments ready for the FAL endpoint
        """
        # Handle both single and multiple image inputs
        if image_urls:
            urls = validate_image_urls(image_urls, min_count=1, max_count=4)
        elif image_url:
            # Validate single URL by wrapping in list
            urls = validate_image_urls([image_url], min_count=1, max_count=1)
        else:
            raise ValueError("Either image_url or image_urls must be provided")

        args = {
            "prompt": prompt,
            "image_urls": urls,
            "aspect_ratio": kwargs.get("aspect_ratio", "auto"),
            "resolution": kwargs.get("resolution", "1K"),
            "output_format": kwargs.get("output_format", "png"),
            "num_images": kwargs.get("num_images", 1),
            "sync_mode": kwargs.get("sync_mode", True)
        }

        # Add optional web search
        if kwargs.get("enable_web_search"):
            args["enable_web_search"] = True

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Nano Banana Pro Edit model information."""
        return {
            **MODEL_INFO.get("nano_banana_pro_edit", {}),
            "endpoint": self.endpoint,
            "supports_multi_image": True,
            "max_input_images": 4
        }

    def estimate_cost(
        self,
        resolution: str = "1K",
        num_images: int = 1,
        enable_web_search: bool = False
    ) -> float:
        """
        Estimate cost for generation.

        Args:
            resolution: Output resolution (1K, 2K, 4K)
            num_images: Number of images to generate
            enable_web_search: Whether web search is enabled

        Returns:
            Estimated cost in USD
        """
        # Base cost per image
        if resolution == "4K":
            base_cost = 0.030
        else:
            base_cost = 0.015

        total = base_cost * num_images

        # Add web search cost if enabled
        if enable_web_search:
            total += 0.015

        return total
