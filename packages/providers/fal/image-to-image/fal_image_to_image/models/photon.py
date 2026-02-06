"""
Luma Photon model implementations
"""

from typing import Dict, Any, Optional, Tuple
from .base import BaseModel
from ..utils.validators import (
    validate_strength, validate_aspect_ratio,
    validate_reframing_coordinates, validate_grid_position
)
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, ASPECT_RATIOS, REFRAME_ENDPOINTS


class PhotonModel(BaseModel):
    """Luma Photon Flash model for creative image modifications."""

    MODEL_KEY = "photon"

    def __init__(self):
        """Initialize the Photon Flash model."""
        super().__init__("photon")
    
    def _calculate_centered_reframing(
        self,
        aspect_ratio: str,
        input_width: Optional[int] = None,
        input_height: Optional[int] = None
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Calculate reframing coordinates to center the input image in the output.
        
        Args:
            aspect_ratio: Target aspect ratio
            input_width: Width of input image (if known)
            input_height: Height of input image (if known)
            
        Returns:
            Tuple of (x_start, y_start, x_end, y_end) or None
        """
        if not input_width or not input_height:
            return None
        
        # Parse aspect ratio
        if ":" in aspect_ratio:
            width_ratio, height_ratio = map(int, aspect_ratio.split(":"))
            target_aspect = width_ratio / height_ratio
        else:
            return None
        
        input_aspect = input_width / input_height
        
        # Calculate centered crop
        if input_aspect > target_aspect:
            # Input is wider - crop width
            new_width = int(input_height * target_aspect)
            new_height = input_height
            x_start = (input_width - new_width) // 2
            y_start = 0
            x_end = x_start + new_width
            y_end = new_height
        else:
            # Input is taller - crop height
            new_width = input_width
            new_height = int(input_width / target_aspect)
            x_start = 0
            y_start = (input_height - new_height) // 2
            x_end = new_width
            y_end = y_start + new_height
        
        return (x_start, y_start, x_end, y_end)
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Photon Flash parameters."""
        defaults = DEFAULT_VALUES["photon"]
        
        strength = kwargs.get("strength", defaults["strength"])
        aspect_ratio = kwargs.get("aspect_ratio", defaults["aspect_ratio"])
        
        strength = validate_strength(strength)
        aspect_ratio = validate_aspect_ratio(aspect_ratio, "photon")
        
        # Validate reframing parameters
        x_start = kwargs.get("x_start")
        y_start = kwargs.get("y_start")
        x_end = kwargs.get("x_end")
        y_end = kwargs.get("y_end")
        
        coords = validate_reframing_coordinates(x_start, y_start, x_end, y_end)
        
        # Validate grid position
        grid_x = kwargs.get("grid_position_x")
        grid_y = kwargs.get("grid_position_y")
        
        grid_pos = validate_grid_position(grid_x, grid_y)
        
        # Auto-center if requested and no manual reframing
        auto_center = kwargs.get("auto_center", False)
        input_width = kwargs.get("input_width")
        input_height = kwargs.get("input_height")
        
        if auto_center and all(c is None for c in coords) and input_width and input_height:
            centered_coords = self._calculate_centered_reframing(
                aspect_ratio, input_width, input_height
            )
            if centered_coords:
                coords = centered_coords
        
        result = {
            "strength": strength,
            "aspect_ratio": aspect_ratio
        }
        
        # Add optional parameters if provided
        if any(c is not None for c in coords):
            result["x_start"] = coords[0]
            result["y_start"] = coords[1]
            result["x_end"] = coords[2]
            result["y_end"] = coords[3]
        
        if any(p is not None for p in grid_pos):
            result["grid_position_x"] = grid_pos[0]
            result["grid_position_y"] = grid_pos[1]
        
        return result
    
    def prepare_arguments(self, prompt: str, image_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Photon Flash."""
        # Check if this is a reframe operation
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        is_reframe = aspect_ratio != "1:1" or any(
            kwargs.get(param) is not None 
            for param in ["x_start", "y_start", "x_end", "y_end", "grid_position_x", "grid_position_y"]
        )
        
        if is_reframe:
            # For reframe endpoint, we don't need strength or prompt
            args = {
                "image_url": image_url,
                "aspect_ratio": aspect_ratio
            }
            
            # Add optional reframing parameters
            for param in ["x_start", "y_start", "x_end", "y_end", "grid_position_x", "grid_position_y"]:
                if param in kwargs and kwargs[param] is not None:
                    args[param] = kwargs[param]
        else:
            # For modify endpoint
            args = {
                "prompt": prompt,
                "image_url": image_url,
                "strength": kwargs["strength"],
                "aspect_ratio": kwargs["aspect_ratio"]
            }
        
        return args
    
    def _should_use_reframe(self, **kwargs) -> bool:
        """Determine if reframe endpoint should be used."""
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        has_reframe_params = any(
            kwargs.get(param) is not None 
            for param in ["x_start", "y_start", "x_end", "y_end", "grid_position_x", "grid_position_y"]
        )
        return aspect_ratio != "1:1" or has_reframe_params
    
    def generate(
        self,
        prompt: str,
        image_url: str,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate modified image using the model.
        Automatically uses reframe endpoint for aspect ratio changes.
        """
        try:
            # Validate parameters
            validated_params = self.validate_parameters(**kwargs)
            
            # Determine which endpoint to use
            if self._should_use_reframe(**validated_params):
                # Use reframe endpoint
                self.endpoint = REFRAME_ENDPOINTS[self.model_key]
                operation = "Reframing"
            else:
                # Use regular modify endpoint
                from ..config.constants import MODEL_ENDPOINTS
                self.endpoint = MODEL_ENDPOINTS[self.model_key]
                operation = "Modifying"
            
            # Prepare API arguments
            arguments = self.prepare_arguments(prompt, image_url, **validated_params)
            
            # Log generation info
            print(f"🎨 {operation} image with {self.display_name}...")
            if operation == "Modifying":
                print(f"   Prompt: {prompt}")
            for key, value in validated_params.items():
                if value is not None:
                    formatted_key = key.replace('_', ' ').title()
                    print(f"   {formatted_key}: {value}")
            
            # Make API call
            import time
            start_time = time.time()
            import fal_client
            response = fal_client.subscribe(self.endpoint, arguments=arguments)
            processing_time = time.time() - start_time
            
            print(f"✅ {operation} completed in {processing_time:.2f} seconds")
            
            # Process response
            images = self.process_response(response)
            if not images:
                raise Exception("No images generated")
            
            # Download images
            from ..utils.file_utils import download_images, ensure_output_directory
            output_directory = ensure_output_directory(output_dir)
            downloaded_files = download_images(images, output_directory)
            
            # Build result dictionary
            result = {
                "success": True,
                "model": self.display_name,
                "operation": operation.lower(),
                "processing_time": processing_time,
                "images": images,
                "downloaded_files": downloaded_files,
                "output_directory": str(output_directory)
            }
            
            if operation == "Modifying":
                result["prompt"] = prompt
            
            # Add model-specific parameters
            result.update(validated_params)
            
            return result
            
        except Exception as e:
            print(f"❌ Error during image {operation.lower()}: {e}")
            
            error_result = {
                "success": False,
                "error": str(e),
                "model": self.display_name,
                "prompt": prompt
            }
            
            # Add model-specific parameters to error response
            try:
                validated_params = self.validate_parameters(**kwargs)
                error_result.update(validated_params)
            except:
                pass
            
            return error_result
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Photon Flash model information."""
        return {
            **MODEL_INFO["photon"],
            "endpoint": self.endpoint
        }


class PhotonBaseModel(BaseModel):
    """Luma Photon Base model for high-quality creative modifications."""

    MODEL_KEY = "photon_base"

    def __init__(self):
        """Initialize the Photon Base model."""
        super().__init__("photon_base")
    
    def _calculate_centered_reframing(
        self,
        aspect_ratio: str,
        input_width: Optional[int] = None,
        input_height: Optional[int] = None
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Calculate reframing coordinates to center the input image in the output.
        
        Args:
            aspect_ratio: Target aspect ratio
            input_width: Width of input image (if known)
            input_height: Height of input image (if known)
            
        Returns:
            Tuple of (x_start, y_start, x_end, y_end) or None
        """
        if not input_width or not input_height:
            return None
        
        # Parse aspect ratio
        if ":" in aspect_ratio:
            width_ratio, height_ratio = map(int, aspect_ratio.split(":"))
            target_aspect = width_ratio / height_ratio
        else:
            return None
        
        input_aspect = input_width / input_height
        
        # Calculate centered crop
        if input_aspect > target_aspect:
            # Input is wider - crop width
            new_width = int(input_height * target_aspect)
            new_height = input_height
            x_start = (input_width - new_width) // 2
            y_start = 0
            x_end = x_start + new_width
            y_end = new_height
        else:
            # Input is taller - crop height
            new_width = input_width
            new_height = int(input_width / target_aspect)
            x_start = 0
            y_start = (input_height - new_height) // 2
            x_end = new_width
            y_end = y_start + new_height
        
        return (x_start, y_start, x_end, y_end)
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Photon Base parameters."""
        defaults = DEFAULT_VALUES["photon"]
        
        strength = kwargs.get("strength", defaults["strength"])
        aspect_ratio = kwargs.get("aspect_ratio", defaults["aspect_ratio"])
        
        strength = validate_strength(strength)
        aspect_ratio = validate_aspect_ratio(aspect_ratio, "photon_base")
        
        # Validate reframing parameters
        x_start = kwargs.get("x_start")
        y_start = kwargs.get("y_start")
        x_end = kwargs.get("x_end")
        y_end = kwargs.get("y_end")
        
        coords = validate_reframing_coordinates(x_start, y_start, x_end, y_end)
        
        # Validate grid position
        grid_x = kwargs.get("grid_position_x")
        grid_y = kwargs.get("grid_position_y")
        
        grid_pos = validate_grid_position(grid_x, grid_y)
        
        # Auto-center if requested and no manual reframing
        auto_center = kwargs.get("auto_center", False)
        input_width = kwargs.get("input_width")
        input_height = kwargs.get("input_height")
        
        if auto_center and all(c is None for c in coords) and input_width and input_height:
            centered_coords = self._calculate_centered_reframing(
                aspect_ratio, input_width, input_height
            )
            if centered_coords:
                coords = centered_coords
        
        result = {
            "strength": strength,
            "aspect_ratio": aspect_ratio
        }
        
        # Add optional parameters if provided
        if any(c is not None for c in coords):
            result["x_start"] = coords[0]
            result["y_start"] = coords[1]
            result["x_end"] = coords[2]
            result["y_end"] = coords[3]
        
        if any(p is not None for p in grid_pos):
            result["grid_position_x"] = grid_pos[0]
            result["grid_position_y"] = grid_pos[1]
        
        return result
    
    def prepare_arguments(self, prompt: str, image_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Photon Base."""
        # Check if this is a reframe operation
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        is_reframe = aspect_ratio != "1:1" or any(
            kwargs.get(param) is not None 
            for param in ["x_start", "y_start", "x_end", "y_end", "grid_position_x", "grid_position_y"]
        )
        
        if is_reframe:
            # For reframe endpoint, we don't need strength or prompt
            args = {
                "image_url": image_url,
                "aspect_ratio": aspect_ratio
            }
            
            # Add optional reframing parameters
            for param in ["x_start", "y_start", "x_end", "y_end", "grid_position_x", "grid_position_y"]:
                if param in kwargs and kwargs[param] is not None:
                    args[param] = kwargs[param]
        else:
            # For modify endpoint
            args = {
                "prompt": prompt,
                "image_url": image_url,
                "strength": kwargs["strength"],
                "aspect_ratio": kwargs["aspect_ratio"]
            }
        
        return args
    
    def _should_use_reframe(self, **kwargs) -> bool:
        """Determine if reframe endpoint should be used."""
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        has_reframe_params = any(
            kwargs.get(param) is not None 
            for param in ["x_start", "y_start", "x_end", "y_end", "grid_position_x", "grid_position_y"]
        )
        return aspect_ratio != "1:1" or has_reframe_params
    
    def generate(
        self,
        prompt: str,
        image_url: str,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate modified image using the model.
        Automatically uses reframe endpoint for aspect ratio changes.
        """
        try:
            # Validate parameters
            validated_params = self.validate_parameters(**kwargs)
            
            # Determine which endpoint to use
            if self._should_use_reframe(**validated_params):
                # Use reframe endpoint
                self.endpoint = REFRAME_ENDPOINTS[self.model_key]
                operation = "Reframing"
            else:
                # Use regular modify endpoint
                from ..config.constants import MODEL_ENDPOINTS
                self.endpoint = MODEL_ENDPOINTS[self.model_key]
                operation = "Modifying"
            
            # Prepare API arguments
            arguments = self.prepare_arguments(prompt, image_url, **validated_params)
            
            # Log generation info
            print(f"🎨 {operation} image with {self.display_name}...")
            if operation == "Modifying":
                print(f"   Prompt: {prompt}")
            for key, value in validated_params.items():
                if value is not None:
                    formatted_key = key.replace('_', ' ').title()
                    print(f"   {formatted_key}: {value}")
            
            # Make API call
            import time
            start_time = time.time()
            import fal_client
            response = fal_client.subscribe(self.endpoint, arguments=arguments)
            processing_time = time.time() - start_time
            
            print(f"✅ {operation} completed in {processing_time:.2f} seconds")
            
            # Process response
            images = self.process_response(response)
            if not images:
                raise Exception("No images generated")
            
            # Download images
            from ..utils.file_utils import download_images, ensure_output_directory
            output_directory = ensure_output_directory(output_dir)
            downloaded_files = download_images(images, output_directory)
            
            # Build result dictionary
            result = {
                "success": True,
                "model": self.display_name,
                "operation": operation.lower(),
                "processing_time": processing_time,
                "images": images,
                "downloaded_files": downloaded_files,
                "output_directory": str(output_directory)
            }
            
            if operation == "Modifying":
                result["prompt"] = prompt
            
            # Add model-specific parameters
            result.update(validated_params)
            
            return result
            
        except Exception as e:
            print(f"❌ Error during image {operation.lower()}: {e}")
            
            error_result = {
                "success": False,
                "error": str(e),
                "model": self.display_name,
                "prompt": prompt
            }
            
            # Add model-specific parameters to error response
            try:
                validated_params = self.validate_parameters(**kwargs)
                error_result.update(validated_params)
            except:
                pass
            
            return error_result
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Photon Base model information."""
        return {
            **MODEL_INFO["photon_base"],
            "endpoint": self.endpoint
        }