"""
Unified command dispatcher and entry point for video tools.

Provides a centralized entry point for all video processing, audio manipulation,
and AI analysis commands using the new class-based architecture.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .base_controller import BaseController
from .media_processing_controller import MediaProcessingController
from .ai_utils import check_ai_requirements, print_ai_status


class CommandDispatcher(BaseController):
    """Main command dispatcher for all video tools operations."""
    
    def __init__(self, input_dir: str = 'input', output_dir: str = 'output', 
                 verbose: bool = True):
        """Initialize the command dispatcher.
        
        Args:
            input_dir: Directory containing input files
            output_dir: Directory for output files
            verbose: Whether to print operation details
        """
        super().__init__(input_dir, output_dir, verbose)
        self.media_controller = MediaProcessingController(input_dir, output_dir, verbose)
    
    def run(self) -> bool:
        """Run the main command dispatcher menu.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.setup_directories():
            return False
        
        return self._show_main_menu()
    
    def _show_main_menu(self) -> bool:
        """Show the main menu for command selection."""
        self.print_header("🎬 VIDEO TOOLS - Enhanced Class-Based Architecture", 60)
        
        if self.verbose:
            print("Welcome to the enhanced video tools suite!")
            print("Reorganized with class-based architecture for better maintainability.")
            print()
        
        while True:
            options = {
                '1': 'Media Processing (Video & Audio)',
                '2': 'AI Analysis (Gemini)',
                '3': 'Speech Transcription (Whisper)',
                '4': 'Batch Operations',
                '5': 'System Status & Requirements',
                '6': 'Settings & Configuration',
                'h': 'Help & Documentation',
                'q': 'Quit'
            }
            
            choice = self.get_user_choice("🎯 Select operation category:", options)
            
            if choice == '1':
                result = self._handle_media_processing()
            elif choice == '2':
                result = self._handle_ai_analysis()
            elif choice == '3':
                result = self._handle_transcription()
            elif choice == '4':
                result = self._handle_batch_operations()
            elif choice == '5':
                result = self._handle_system_status()
            elif choice == '6':
                result = self._handle_settings()
            elif choice == 'h':
                result = self._show_help()
            elif choice == 'q':
                if self.verbose:
                    print("👋 Goodbye!")
                return True
            else:
                if self.verbose:
                    print("❌ Invalid choice. Please try again.")
                continue
            
            if not result and self.verbose:
                print("\n⚠️ Operation completed with issues.")
            
            if self.verbose:
                input("\nPress Enter to continue...")
    
    def _handle_media_processing(self) -> bool:
        """Handle media processing operations."""
        self.print_header("🎬 MEDIA PROCESSING")
        
        if self.verbose:
            print("Video cutting, audio manipulation, format conversion, and more.")
            print()
        
        return self.media_controller.run()
    
    def _handle_ai_analysis(self) -> bool:
        """Handle AI analysis operations."""
        self.print_header("🤖 AI ANALYSIS - Google Gemini")
        
        # Check Gemini requirements first
        gemini_available, gemini_message = check_ai_requirements()['gemini']['status']
        
        if not gemini_available:
            if self.verbose:
                print(f"❌ Gemini not available: {gemini_message}")
                print("\n💡 Setup instructions:")
                print("   1. Get API key: https://aistudio.google.com/app/apikey")
                print("   2. Set environment variable: export GEMINI_API_KEY=your_key")
                print("   3. Install library: pip install google-generativeai")
            return False
        
        if self.verbose:
            print("✅ Gemini AI ready for analysis")
            print("Video, audio, and image understanding with AI.")
            print()
        
        return self._show_ai_analysis_menu()
    
    def _show_ai_analysis_menu(self) -> bool:
        """Show AI analysis submenu."""
        from .ai_utils import (
            analyze_video_file, analyze_audio_file, analyze_image_file,
            analyze_media_comprehensively, save_analysis_result
        )
        from .file_utils import find_video_files, find_audio_files, find_image_files
        
        options = {
            '1': 'Analyze Videos (Gemini Direct)',
            '2': 'Analyze Audio Files (Gemini Direct)',
            '3': 'Analyze Images (Gemini Direct)',
            '4': 'Analyze Images (OpenRouter)',
            '5': 'Compare Providers (Gemini vs OpenRouter)',
            '6': 'Comprehensive Media Analysis',
            '7': 'Custom Q&A Analysis',
            '8': 'OpenRouter Info & Setup',
            '9': 'Detailed Video Timeline (FAL + Gemini)',
            'b': 'Back to main menu'
        }

        choice = self.get_user_choice("🤖 Select AI analysis type:", options)

        if choice == '1':
            return self._analyze_videos()
        elif choice == '2':
            return self._analyze_audio()
        elif choice == '3':
            return self._analyze_images()
        elif choice == '4':
            return self._analyze_images_openrouter()
        elif choice == '5':
            return self._compare_providers()
        elif choice == '6':
            return self._comprehensive_analysis()
        elif choice == '7':
            return self._custom_qa_analysis()
        elif choice == '8':
            return self._openrouter_info()
        elif choice == '9':
            return self._detailed_timeline()
        elif choice == 'b':
            return True
        else:
            return False

    def _detailed_timeline(self) -> bool:
        """Generate detailed second-by-second video timeline."""
        from .ai_commands import cmd_detailed_timeline
        cmd_detailed_timeline()
        return True
    
    def _analyze_videos(self) -> bool:
        """Analyze videos with Gemini."""
        from .ai_utils import analyze_video_file, save_analysis_result
        from .file_utils import find_video_files
        
        video_files = find_video_files(self.input_dir)
        if not video_files:
            if self.verbose:
                print("📁 No video files found in input directory")
            return False
        
        self.print_file_info(video_files, "video file")
        
        # Select analysis type
        analysis_options = {
            '1': 'Video Description',
            '2': 'Audio Transcription',
            '3': 'Scene Analysis',
            '4': 'Key Information Extraction'
        }
        
        analysis_choice = self.get_user_choice("🎯 Select analysis type:", analysis_options)
        analysis_map = {
            '1': 'description',
            '2': 'transcription',
            '3': 'scenes',
            '4': 'extraction'
        }
        
        analysis_type = analysis_map.get(analysis_choice)
        if not analysis_type:
            return False
        
        detailed = self.get_yes_no("📊 Detailed analysis?", False)
        
        successful = 0
        failed = 0
        
        for i, video_file in enumerate(video_files, 1):
            self.show_progress(i, len(video_files), "video")
            
            try:
                result = analyze_video_file(video_file, analysis_type, detailed=detailed)
                if result:
                    output_file = self.output_dir / f"{video_file.stem}_{analysis_type}"
                    save_analysis_result(result, output_file)
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                if self.verbose:
                    print(f"❌ Error analyzing {video_file.name}: {e}")
                failed += 1
        
        self.show_summary(successful, failed, len(video_files))
        return successful > 0
    
    def _analyze_audio(self) -> bool:
        """Analyze audio files with Gemini."""
        from .ai_utils import analyze_audio_file, save_analysis_result
        from .file_utils import find_audio_files
        
        audio_files = find_audio_files(self.input_dir)
        if not audio_files:
            if self.verbose:
                print("📁 No audio files found in input directory")
            return False
        
        self.print_file_info(audio_files, "audio file")
        
        # Select analysis type
        analysis_options = {
            '1': 'Audio Description',
            '2': 'Speech Transcription',
            '3': 'Content Analysis',
            '4': 'Event Detection'
        }
        
        analysis_choice = self.get_user_choice("🎯 Select analysis type:", analysis_options)
        analysis_map = {
            '1': 'description',
            '2': 'transcription',
            '3': 'content_analysis',
            '4': 'event_detection'
        }
        
        analysis_type = analysis_map.get(analysis_choice)
        if not analysis_type:
            return False
        
        detailed = self.get_yes_no("📊 Detailed analysis?", False)
        
        successful = 0
        failed = 0
        
        for i, audio_file in enumerate(audio_files, 1):
            self.show_progress(i, len(audio_files), "audio file")
            
            try:
                result = analyze_audio_file(audio_file, analysis_type, detailed=detailed)
                if result:
                    output_file = self.output_dir / f"{audio_file.stem}_{analysis_type}"
                    save_analysis_result(result, output_file)
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                if self.verbose:
                    print(f"❌ Error analyzing {audio_file.name}: {e}")
                failed += 1
        
        self.show_summary(successful, failed, len(audio_files))
        return successful > 0
    
    def _analyze_images(self) -> bool:
        """Analyze images with Gemini."""
        from .ai_utils import analyze_image_file, save_analysis_result
        from .file_utils import find_image_files
        
        image_files = find_image_files(self.input_dir)
        if not image_files:
            if self.verbose:
                print("📁 No image files found in input directory")
            return False
        
        self.print_file_info(image_files, "image file")
        
        # Select analysis type
        analysis_options = {
            '1': 'Image Description',
            '2': 'Image Classification',
            '3': 'Object Detection',
            '4': 'Text Extraction (OCR)',
            '5': 'Composition Analysis'
        }
        
        analysis_choice = self.get_user_choice("🎯 Select analysis type:", analysis_options)
        analysis_map = {
            '1': 'description',
            '2': 'classification',
            '3': 'object_detection',
            '4': 'text_extraction',
            '5': 'composition'
        }
        
        analysis_type = analysis_map.get(analysis_choice)
        if not analysis_type:
            return False
        
        detailed = self.get_yes_no("📊 Detailed analysis?", False)
        
        successful = 0
        failed = 0
        
        for i, image_file in enumerate(image_files, 1):
            self.show_progress(i, len(image_files), "image")
            
            try:
                result = analyze_image_file(image_file, analysis_type, detailed=detailed)
                if result:
                    output_file = self.output_dir / f"{image_file.stem}_{analysis_type}"
                    save_analysis_result(result, output_file)
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                if self.verbose:
                    print(f"❌ Error analyzing {image_file.name}: {e}")
                failed += 1
        
        self.show_summary(successful, failed, len(image_files))
        return successful > 0
    
    def _comprehensive_analysis(self) -> bool:
        """Perform comprehensive analysis on all media files."""
        from .ai_utils import analyze_media_comprehensively
        from .file_utils import find_video_files, find_audio_files, find_image_files
        
        # Find all media files
        video_files = find_video_files(self.input_dir)
        audio_files = find_audio_files(self.input_dir)
        image_files = find_image_files(self.input_dir)
        
        all_files = video_files + audio_files + image_files
        
        if not all_files:
            if self.verbose:
                print("📁 No media files found in input directory")
            return False
        
        if self.verbose:
            print(f"📊 Found {len(all_files)} media files:")
            print(f"   Videos: {len(video_files)}")
            print(f"   Audio: {len(audio_files)}")
            print(f"   Images: {len(image_files)}")
        
        proceed = self.get_yes_no("🚀 Start comprehensive analysis?", True)
        if not proceed:
            return False
        
        successful = 0
        failed = 0
        
        for i, file_path in enumerate(all_files, 1):
            self.show_progress(i, len(all_files), "media file")
            
            try:
                result = analyze_media_comprehensively(file_path, self.output_dir, save_results=True)
                if result and not result.get('errors'):
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                if self.verbose:
                    print(f"❌ Error analyzing {file_path.name}: {e}")
                failed += 1
        
        self.show_summary(successful, failed, len(all_files))
        return successful > 0
    
    def _custom_qa_analysis(self) -> bool:
        """Perform custom Q&A analysis."""
        # Implementation for custom Q&A would go here
        if self.verbose:
            print("🚧 Custom Q&A analysis - Coming soon!")
        return True
    
    def _handle_transcription(self) -> bool:
        """Handle transcription operations."""
        self.print_header("🎤 SPEECH TRANSCRIPTION - Whisper")
        
        # Check Whisper requirements
        whisper_req = check_ai_requirements()['whisper']
        
        api_available = whisper_req.get('api', (False, ''))[0]
        local_available = whisper_req.get('local', (False, ''))[0]
        
        if not api_available and not local_available:
            if self.verbose:
                print("❌ Whisper not available")
                print("\n💡 Setup instructions:")
                print("   API: Set OPENAI_API_KEY environment variable")
                print("   Local: pip install openai-whisper")
            return False
        
        return self._show_transcription_menu()
    
    def _show_transcription_menu(self) -> bool:
        """Show transcription submenu."""
        from .ai_utils import transcribe_with_whisper, batch_transcribe_whisper, save_analysis_result
        from .file_utils import find_video_files, find_audio_files
        
        options = {
            '1': 'Transcribe Individual Files',
            '2': 'Batch Transcription',
            '3': 'Compare Whisper Models',
            'b': 'Back to main menu'
        }
        
        choice = self.get_user_choice("🎤 Select transcription operation:", options)
        
        if choice == '1':
            return self._transcribe_individual()
        elif choice == '2':
            return self._transcribe_batch()
        elif choice == '3':
            return self._compare_models()
        elif choice == 'b':
            return True
        else:
            return False
    
    def _transcribe_individual(self) -> bool:
        """Transcribe individual files."""
        from .ai_utils import transcribe_with_whisper, save_analysis_result
        from .file_utils import find_video_files, find_audio_files
        
        # Find all transcribable files
        video_files = find_video_files(self.input_dir)
        audio_files = find_audio_files(self.input_dir)
        all_files = video_files + audio_files
        
        if not all_files:
            if self.verbose:
                print("📁 No audio/video files found")
            return False
        
        self.print_file_info(all_files, "transcribable file")
        
        # Select transcription method
        use_local = self.get_yes_no("🤖 Use local Whisper model? (otherwise API)", False)
        
        if use_local:
            model_options = {
                '1': 'tiny (fastest, lowest quality)',
                '2': 'base (balanced)',
                '3': 'small (good quality)',
                '4': 'medium (better quality)', 
                '5': 'large (best quality)',
                '6': 'turbo (fast, good quality)'
            }
            model_choice = self.get_user_choice("🎯 Select model size:", model_options, '6')
            model_map = {
                '1': 'tiny', '2': 'base', '3': 'small',
                '4': 'medium', '5': 'large', '6': 'turbo'
            }
            model_size = model_map.get(model_choice, 'turbo')
        else:
            model_size = 'turbo'
        
        language = self.get_user_input("🌍 Language code (optional, e.g., 'en', 'es')", "")
        if not language:
            language = None
        
        successful = 0
        failed = 0
        
        for i, file_path in enumerate(all_files, 1):
            self.show_progress(i, len(all_files), "file")
            
            try:
                result = transcribe_with_whisper(
                    file_path, 
                    use_local=use_local,
                    model_size=model_size,
                    language=language
                )
                if result:
                    output_file = self.output_dir / f"{file_path.stem}_transcription"
                    save_analysis_result(result, output_file)
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                if self.verbose:
                    print(f"❌ Error transcribing {file_path.name}: {e}")
                failed += 1
        
        self.show_summary(successful, failed, len(all_files))
        return successful > 0
    
    def _transcribe_batch(self) -> bool:
        """Perform batch transcription."""
        from .ai_utils import batch_transcribe_whisper
        from .file_utils import find_video_files, find_audio_files
        
        # Find all transcribable files
        video_files = find_video_files(self.input_dir)
        audio_files = find_audio_files(self.input_dir)
        all_files = video_files + audio_files
        
        if not all_files:
            if self.verbose:
                print("📁 No audio/video files found")
            return False
        
        if self.verbose:
            print(f"🎤 Found {len(all_files)} files for batch transcription")
        
        use_local = self.get_yes_no("🤖 Use local Whisper model?", False)
        
        try:
            results = batch_transcribe_whisper(
                all_files,
                use_local=use_local,
                save_results=True
            )
            
            successful = len([r for r in results if 'error' not in r])
            failed = len(results) - successful
            
            self.show_summary(successful, failed, len(all_files))
            return successful > 0
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Batch transcription failed: {e}")
            return False
    
    def _compare_models(self) -> bool:
        """Compare different Whisper models."""
        if self.verbose:
            print("🚧 Model comparison - Coming soon!")
        return True
    
    def _handle_batch_operations(self) -> bool:
        """Handle batch operations."""
        self.print_header("⚡ BATCH OPERATIONS")
        
        if self.verbose:
            print("Process multiple files efficiently with batch operations.")
            print()
        
        return self.media_controller.cmd_batch_process()
    
    def _handle_system_status(self) -> bool:
        """Handle system status and requirements."""
        self.print_header("🔧 SYSTEM STATUS & REQUIREMENTS")
        
        print_ai_status()
        
        # Additional system info
        if self.verbose:
            print("\n" + "=" * 40)
            print("📁 Directory Status:")
            print(f"   Input: {self.input_dir} {'✅' if self.input_dir.exists() else '❌'}")
            print(f"   Output: {self.output_dir} {'✅' if self.output_dir.exists() else '❌'}")
            
            # Check for files
            from .file_utils import find_video_files, find_audio_files, find_image_files
            
            video_count = len(find_video_files(self.input_dir)) if self.input_dir.exists() else 0
            audio_count = len(find_audio_files(self.input_dir)) if self.input_dir.exists() else 0
            image_count = len(find_image_files(self.input_dir)) if self.input_dir.exists() else 0
            
            print(f"\n📊 Files in input directory:")
            print(f"   Videos: {video_count}")
            print(f"   Audio: {audio_count}")
            print(f"   Images: {image_count}")
            print(f"   Total: {video_count + audio_count + image_count}")
        
        return True
    
    def _handle_settings(self) -> bool:
        """Handle settings and configuration."""
        self.print_header("⚙️ SETTINGS & CONFIGURATION")
        
        if self.verbose:
            print("Current settings:")
            print(f"   Input directory: {self.input_dir}")
            print(f"   Output directory: {self.output_dir}")
            print(f"   Verbose mode: {self.verbose}")
            print()
            print("🚧 Settings management - Coming soon!")
        
        return True
    
    def _show_help(self) -> bool:
        """Show help and documentation."""
        self.print_header("📚 HELP & DOCUMENTATION")
        
        if self.verbose:
            print("""
🎬 VIDEO TOOLS - Enhanced Class-Based Architecture

This tool provides comprehensive video, audio, and image processing capabilities
using modern class-based architecture for better maintainability and extensibility.

MAIN CATEGORIES:

1. 📹 Media Processing
   - Video cutting and trimming
   - Audio extraction and manipulation
   - Format conversion
   - Batch processing operations

2. 🤖 AI Analysis (Gemini)
   - Video description and analysis
   - Audio transcription and content analysis
   - Image classification and object detection
   - OCR text extraction
   - Custom Q&A analysis

3. 🎤 Speech Transcription (Whisper)
   - High-quality speech-to-text
   - Support for multiple languages
   - Both API and local model options
   - Batch transcription capabilities

SETUP REQUIREMENTS:

- FFmpeg: For video/audio processing
- Gemini API: Set GEMINI_API_KEY environment variable
- Whisper: Set OPENAI_API_KEY or install openai-whisper
- Python packages: See requirements files

DIRECTORY STRUCTURE:

- input/: Place your media files here
- output/: Processed files and results are saved here

For detailed documentation, see the README.md file.
            """)
        
        return True
    
    def _analyze_images_openrouter(self) -> bool:
        """Analyze images using OpenRouter."""
        from .openrouter_commands import cmd_analyze_images_openrouter
        
        if self.verbose:
            print("🌐 Running OpenRouter image analysis...")
        
        try:
            cmd_analyze_images_openrouter()
            return True
        except Exception as e:
            if self.verbose:
                print(f"❌ OpenRouter analysis failed: {e}")
            return False
    
    def _compare_providers(self) -> bool:
        """Compare Gemini direct vs OpenRouter."""
        from .openrouter_commands import cmd_compare_providers
        
        if self.verbose:
            print("⚖️ Running provider comparison...")
        
        try:
            cmd_compare_providers()
            return True
        except Exception as e:
            if self.verbose:
                print(f"❌ Provider comparison failed: {e}")
            return False
    
    def _openrouter_info(self) -> bool:
        """Show OpenRouter information and setup."""
        from .openrouter_commands import cmd_openrouter_info
        
        try:
            cmd_openrouter_info()
            return True
        except Exception as e:
            if self.verbose:
                print(f"❌ OpenRouter info failed: {e}")
            return False


def main():
    """Main entry point for the video tools command line interface."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced video tools with class-based architecture"
    )
    parser.add_argument(
        "--input-dir", "-i",
        default="input",
        help="Input directory (default: input)"
    )
    parser.add_argument(
        "--output-dir", "-o", 
        default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Run in quiet mode (minimal output)"
    )
    parser.add_argument(
        "--command", "-c",
        choices=['media', 'ai', 'transcribe', 'batch', 'status'],
        help="Run specific command directly"
    )
    
    args = parser.parse_args()
    
    # Create dispatcher
    dispatcher = CommandDispatcher(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        verbose=not args.quiet
    )
    
    try:
        if args.command:
            # Run specific command
            if args.command == 'media':
                success = dispatcher._handle_media_processing()
            elif args.command == 'ai':
                success = dispatcher._handle_ai_analysis()
            elif args.command == 'transcribe':
                success = dispatcher._handle_transcription()
            elif args.command == 'batch':
                success = dispatcher._handle_batch_operations()
            elif args.command == 'status':
                success = dispatcher._handle_system_status()
            else:
                success = False
            
            sys.exit(0 if success else 1)
        else:
            # Run interactive menu
            success = dispatcher.run()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        if not args.quiet:
            print("\n👋 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        if not args.quiet:
            print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()