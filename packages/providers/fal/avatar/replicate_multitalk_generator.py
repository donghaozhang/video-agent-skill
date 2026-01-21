"""
Replicate MultiTalk Generator

DEPRECATED: This module is deprecated. Use the FAL AI Avatar Multi model instead.
See: issues/migrate-replicate-to-fal-avatar.md

Migration example:
    # Old (deprecated):
    from replicate_multitalk_generator import ReplicateMultiTalkGenerator
    generator = ReplicateMultiTalkGenerator()

    # New (recommended):
    from fal_avatar import FALAvatarGenerator
    generator = FALAvatarGenerator()
    result = generator.generate_conversation(
        image_url="...",
        first_audio_url="...",
        prompt="..."
    )

This module provides a Python interface for generating multi-person conversational videos using
Replicate's MultiTalk model (zsxkib/multitalk). The MultiTalk model creates realistic conversations
between multiple people by synchronizing audio files with a reference image.

Features:
- Multi-person conversational video generation (up to 2 people)
- Audio-driven lip-sync and facial expressions
- Customizable frame count and generation parameters
- Turbo mode for faster generation
- Support for both local and remote images/audio files
- Flexible conversation scenarios via prompt

API Endpoint: zsxkib/multitalk
Documentation: https://replicate.com/zsxkib/multitalk
"""

import os
import time
import warnings
import replicate
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ReplicateMultiTalkGenerator:
    """
    Replicate MultiTalk Video Generator
    
    This class provides methods to generate multi-person conversational videos from images 
    and audio files using Replicate's MultiTalk model.
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Replicate MultiTalk Generator

        DEPRECATED: Use FALAvatarGenerator with model='multitalk' instead.

        Args:
            api_token (str, optional): Replicate API token. If not provided, will look for REPLICATE_API_TOKEN environment variable.
        """
        warnings.warn(
            "ReplicateMultiTalkGenerator is deprecated and will be removed in a future version. "
            "Use FALAvatarGenerator with model='multitalk' instead. "
            "See: issues/migrate-replicate-to-fal-avatar.md\n"
            "Example: from fal_avatar import FALAvatarGenerator; "
            "generator = FALAvatarGenerator(); generator.generate_conversation(...)",
            DeprecationWarning,
            stacklevel=2
        )
        self.api_token = api_token or os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN environment variable not set or api_token not provided")
        
        # Set the API token for replicate client
        os.environ['REPLICATE_API_TOKEN'] = self.api_token
        
        # Model endpoint
        self.model_name = "zsxkib/multitalk"
        self.model_version = "zsxkib/multitalk:0bd2390c40618c910ffc345b36c8fd218fd8fa59c9124aa641fea443fa203b44"
        
        print(f"✅ Replicate MultiTalk Generator initialized")
        print(f"📍 Model endpoint: {self.model_name}")
        print(f"🗣️ Supports: Multi-person conversational video generation")
    
    def generate_conversation_video(
        self,
        image_url: str,
        first_audio_url: str,
        second_audio_url: Optional[str] = None,
        prompt: str = "A smiling man and woman hosting a podcast",
        num_frames: int = 81,
        seed: Optional[int] = None,
        turbo: bool = True,
        sampling_steps: int = 40,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a multi-person conversational video from an image and audio files
        
        Args:
            image_url (str): URL of the input image or local file path containing person(s)
            first_audio_url (str): URL of the first audio file or local file path
            second_audio_url (str, optional): URL of the second audio file for multi-person conversation
            prompt (str): Text describing conversation scenario (default: "A smiling man and woman hosting a podcast")
            num_frames (int): Number of frames to generate (25-201, default: 81)
            seed (int, optional): Random seed for reproducible results
            turbo (bool): Enable turbo mode for faster generation (default: True)
            sampling_steps (int): Number of enhancement iterations (2-100, default: 40)
            output_path (str, optional): Path to save the generated video
            
        Returns:
            Dict containing the generated video information and metadata
        """
        try:
            print(f"🎬 Starting MultiTalk conversational video generation...")
            print(f"🖼️ Image: {image_url}")
            print(f"🎵 First audio: {first_audio_url}")
            if second_audio_url:
                print(f"🎵 Second audio: {second_audio_url}")
            print(f"📝 Prompt: {prompt}")
            print(f"⚡ Turbo mode: {turbo}")
            print(f"🎞️ Frames: {num_frames}")
            
            # Handle local image files
            if os.path.isfile(image_url):
                print(f"📤 Uploading local image: {image_url}")
                with open(image_url, 'rb') as f:
                    image_url = f
                print(f"✅ Image prepared for upload")
            
            # Handle local audio files
            if os.path.isfile(first_audio_url):
                print(f"📤 Uploading first audio: {first_audio_url}")
                with open(first_audio_url, 'rb') as f:
                    first_audio_url = f
                print(f"✅ First audio prepared for upload")
            
            if second_audio_url and os.path.isfile(second_audio_url):
                print(f"📤 Uploading second audio: {second_audio_url}")
                with open(second_audio_url, 'rb') as f:
                    second_audio_url = f
                print(f"✅ Second audio prepared for upload")
            
            # Validate parameters
            if not (25 <= num_frames <= 201):
                raise ValueError(f"num_frames must be between 25 and 201, got {num_frames}")
            
            if not (2 <= sampling_steps <= 100):
                raise ValueError(f"sampling_steps must be between 2 and 100, got {sampling_steps}")
            
            # Prepare input arguments
            input_args = {
                "image": image_url,
                "first_audio": first_audio_url,
                "prompt": prompt,
                "num_frames": num_frames,
                "turbo": turbo,
                "sampling_steps": sampling_steps
            }
            
            # Add optional parameters
            if second_audio_url:
                input_args["second_audio"] = second_audio_url
            
            if seed is not None:
                input_args["seed"] = seed
            
            print(f"🚀 Submitting request to {self.model_name}...")
            
            # Track generation time
            start_time = time.time()
            
            # Generate the conversational video using the specific model version
            output = replicate.run(
                self.model_version,
                input=input_args
            )
            
            generation_time = time.time() - start_time
            
            if output:
                video_url = str(output)
                
                print(f"✅ MultiTalk conversation video generated successfully!")
                print(f"⏱️ Generation time: {generation_time:.2f} seconds")
                print(f"🔗 Video URL: {video_url}")
                
                # Download video if output path specified
                if output_path:
                    self._download_video(video_url, output_path)
                
                # Prepare result with metadata
                result = {
                    'video': {
                        'url': video_url,
                        'file_size': None  # Replicate doesn't provide file size in response
                    },
                    'generation_time': generation_time,
                    'parameters': input_args
                }
                
                return result
            else:
                raise Exception(f"No output received from MultiTalk model")
                
        except Exception as e:
            print(f"❌ Error generating MultiTalk conversation video: {str(e)}")
            raise
    
    def generate_single_person_video(
        self,
        image_url: str,
        audio_url: str,
        prompt: str = "A person speaking naturally with clear expressions",
        num_frames: int = 81,
        seed: Optional[int] = None,
        turbo: bool = True,
        sampling_steps: int = 40,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a single-person talking video (convenience method for single audio)
        
        Args:
            image_url (str): URL of the input image or local file path
            audio_url (str): URL of the audio file or local file path
            prompt (str): Text describing the scenario
            num_frames (int): Number of frames to generate (25-201, default: 81)
            seed (int, optional): Random seed for reproducible results
            turbo (bool): Enable turbo mode for faster generation
            sampling_steps (int): Number of enhancement iterations (2-100, default: 40)
            output_path (str, optional): Path to save the generated video
            
        Returns:
            Dict containing the generated video information and metadata
        """
        return self.generate_conversation_video(
            image_url=image_url,
            first_audio_url=audio_url,
            second_audio_url=None,
            prompt=prompt,
            num_frames=num_frames,
            seed=seed,
            turbo=turbo,
            sampling_steps=sampling_steps,
            output_path=output_path
        )
    
    def _download_video(self, video_url: str, output_path: str) -> None:
        """Download video from URL to local path"""
        try:
            import requests
            
            print(f"📥 Downloading video to {output_path}...")
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            response = requests.get(video_url)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(output_path)
            print(f"✅ Video downloaded: {output_path} ({file_size / (1024*1024):.2f} MB)")
            
        except Exception as e:
            print(f"❌ Error downloading video: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the MultiTalk model"""
        return {
            "name": "MultiTalk",
            "provider": "Replicate",
            "model_id": self.model_name,
            "description": "Audio-driven multi-person conversational video generation",
            "features": [
                "Multi-person conversations (up to 2 people)",
                "Audio-driven lip-sync",
                "Natural facial expressions", 
                "Customizable frame count (25-201)",
                "Turbo mode for faster generation",
                "Adjustable sampling steps (2-100)"
            ],
            "input_formats": {
                "image": "URL or local file path",
                "audio": "URL or local file path (supports first_audio and second_audio)",
                "prompt": "Text description of conversation scenario",
                "num_frames": "Integer (25-201)",
                "seed": "Integer (optional)",
                "turbo": "Boolean (default: True)",
                "sampling_steps": "Integer (2-100, default: 40)"
            },
            "output_format": "Video file URL",
            "hardware": "H100 GPU",
            "cost_estimate": "Variable based on processing time"
        }
    
    def generate_official_example(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate conversation video using typical MultiTalk example parameters
        
        This method demonstrates common usage patterns for the MultiTalk model.
        
        Args:
            output_path (str, optional): Path to save the generated video
            
        Returns:
            Dict containing the generated video information and metadata
        """
        print("🎭 Generating MultiTalk video using example parameters...")
        print("📖 Model: zsxkib/multitalk")
        
        # Example using placeholder data (users should replace with actual files)
        return self.generate_conversation_video(
            image_url="https://via.placeholder.com/512x512/CCCCCC/FFFFFF?text=Upload+Your+Image",
            first_audio_url="https://via.placeholder.com/1x1/CCCCCC/FFFFFF?text=.mp3",  # Placeholder - users need real audio
            second_audio_url=None,  # Single person example
            prompt="A smiling person speaking naturally during a video call",
            num_frames=81,
            seed=42,
            turbo=True,
            sampling_steps=40,
            output_path=output_path
        )
    
    def test_connection(self) -> bool:
        """Test connection to Replicate API"""
        try:
            print("🔍 Testing Replicate API connection...")
            
            # Try to get model information
            model = replicate.models.get(self.model_name)
            
            if model:
                print("✅ Replicate API connection successful")
                print(f"📋 Model: {model.name}")
                print(f"🏷️ Latest version: {model.latest_version.id if model.latest_version else 'N/A'}")
                return True
            else:
                print("❌ Could not retrieve model information")
                return False
                
        except Exception as e:
            print(f"❌ Replicate API connection test failed: {str(e)}")
            return False

def main():
    """Example usage of the Replicate MultiTalk Generator"""
    try:
        # Initialize generator
        generator = ReplicateMultiTalkGenerator()
        
        # Test connection
        if not generator.test_connection():
            print("❌ Connection test failed. Please check your API token.")
            return
        
        # Display model information
        print("\n🔍 Model Information:")
        model_info = generator.get_model_info()
        print(f"📋 Name: {model_info['name']}")
        print(f"🏢 Provider: {model_info['provider']}")
        print(f"🆔 Model ID: {model_info['model_id']}")
        print(f"📝 Description: {model_info['description']}")
        
        print(f"\n✨ Features:")
        for feature in model_info['features']:
            print(f"   • {feature}")
        
        print(f"\n📥 Input Formats:")
        for key, value in model_info['input_formats'].items():
            print(f"   • {key}: {value}")
        
        print(f"\n📤 Output: {model_info['output_format']}")
        print(f"💻 Hardware: {model_info['hardware']}")
        print(f"💰 Cost: {model_info['cost_estimate']}")
        
        print(f"\n📋 Usage Examples:")
        print(f"   • Single person: generator.generate_single_person_video(image, audio)")
        print(f"   • Conversation: generator.generate_conversation_video(image, audio1, audio2)")
        print(f"   • Example: generator.generate_official_example()")
        
        print(f"\n⚠️ Note: MultiTalk requires actual audio files and images.")
        print(f"   The official_example() method uses placeholders for demonstration.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()