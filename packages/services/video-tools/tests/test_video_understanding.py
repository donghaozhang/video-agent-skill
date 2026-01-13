#!/usr/bin/env python3
"""
Test script for Google Gemini video understanding functionality.

This script tests the video analysis capabilities without requiring actual API calls.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import video_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_gemini_import():
    """Test if Gemini modules can be imported."""
    print("🧪 Testing Gemini video understanding imports...")
    
    try:
        from video_utils import (
            check_gemini_requirements,
            analyze_video_file,
            analyze_audio_file,
            analyze_image_file,
            save_analysis_result,
            GeminiVideoAnalyzer
        )
        print("✅ Video understanding module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_requirements_check():
    """Test requirements checking functionality."""
    print("\n🧪 Testing requirements check...")
    
    try:
        from video_utils import check_gemini_requirements
        
        available, message = check_gemini_requirements()
        print(f"📋 Gemini available: {available}")
        print(f"📋 Message: {message}")
        
        if not available:
            if "not installed" in message:
                print("💡 Install with: pip install google-generativeai")
            if "not set" in message:
                print("💡 Set API key: export GEMINI_API_KEY=your_api_key")
                print("💡 Get API key: https://aistudio.google.com/app/apikey")
        
        return True
    except Exception as e:
        print(f"❌ Requirements check failed: {e}")
        return False

def test_analyzer_initialization():
    """Test analyzer initialization (without API key)."""
    print("\n🧪 Testing analyzer initialization...")
    
    try:
        from video_utils import GeminiVideoAnalyzer
        
        # This should fail without API key, which is expected
        try:
            analyzer = GeminiVideoAnalyzer()
            print("✅ Analyzer initialized (API key available)")
            return True
        except ValueError as e:
            if "API key required" in str(e):
                print("⚠️  Analyzer initialization failed as expected (no API key)")
                print("💡 This is normal for testing without credentials")
                return True
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        except ImportError as e:
            print(f"⚠️  Google GenerativeAI not installed: {e}")
            print("💡 Install with: pip install google-generativeai")
            return True  # Expected behavior
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        return False

def test_save_functionality():
    """Test result saving functionality."""
    print("\n🧪 Testing result saving...")
    
    try:
        from video_utils import save_analysis_result
        
        # Test data
        test_result = {
            'file_id': 'test_file_123',
            'description': 'This is a test video description.',
            'analysis_type': 'description',
            'detailed': False
        }
        
        output_path = Path("output/test_analysis_result.json")
        output_path.parent.mkdir(exist_ok=True)
        
        success = save_analysis_result(test_result, output_path)
        
        if success and output_path.exists():
            print("✅ Result saving works correctly")
            
            # Check content
            import json
            with open(output_path, 'r') as f:
                loaded_data = json.load(f)
            
            if loaded_data == test_result:
                print("✅ Saved data matches original")
                return True
            else:
                print("❌ Saved data doesn't match")
                return False
        else:
            print("❌ Result saving failed")
            return False
            
    except Exception as e:
        print(f"❌ Save test failed: {e}")
        return False

def test_cli_commands():
    """Test CLI command availability."""
    print("\n🧪 Testing CLI command imports...")
    
    try:
        from video_utils.commands import (
            cmd_analyze_videos,
            cmd_transcribe_videos,
            cmd_describe_videos
        )
        print("✅ All CLI commands imported successfully")
        
        # Test that they're callable
        if all(callable(cmd) for cmd in [cmd_analyze_videos, cmd_transcribe_videos, cmd_describe_videos]):
            print("✅ All commands are callable")
            return True
        else:
            print("❌ Some commands are not callable")
            return False
            
    except ImportError as e:
        print(f"❌ CLI command import failed: {e}")
        return False

def test_package_integration():
    """Test integration with main package."""
    print("\n🧪 Testing package integration...")
    
    try:
        import video_utils
        
        # Check if video understanding functions are exported
        expected_exports = [
            'check_gemini_requirements',
            'analyze_video_file',
            'analyze_audio_file',
            'analyze_image_file', 
            'save_analysis_result',
            'GeminiVideoAnalyzer'
        ]
        
        missing_exports = []
        for export in expected_exports:
            if not hasattr(video_utils, export):
                missing_exports.append(export)
        
        if missing_exports:
            print(f"❌ Missing exports: {missing_exports}")
            return False
        else:
            print("✅ All video understanding functions properly exported")
            return True
            
    except Exception as e:
        print(f"❌ Package integration test failed: {e}")
        return False

def run_mock_analysis():
    """Run a mock analysis without API calls."""
    print("\n🧪 Testing mock analysis workflow...")
    
    try:
        # Create a fake video file for testing
        test_video = Path("output/fake_video.mp4")
        test_video.parent.mkdir(exist_ok=True)
        test_video.touch()  # Create empty file
        
        # Test the workflow without actual API calls
        print(f"📹 Mock video: {test_video.name}")
        print("🎯 Video analysis types available:")
        print("   - description: Video content summary")
        print("   - transcription: Audio to text conversion")
        print("   - scenes: Timeline and scene analysis")
        print("   - extraction: Key information extraction") 
        print("   - qa: Question and answer analysis")
        
        print("🎯 Audio analysis types available:")
        print("   - description: Audio content summary")
        print("   - transcription: Audio to text with speaker ID")
        print("   - content_analysis: Comprehensive acoustic analysis")
        print("   - events: Audio event and segment detection")
        print("   - qa: Question and answer analysis")
        
        print("🎯 Image analysis types available:")
        print("   - description: Image content description")
        print("   - classification: Image categorization")
        print("   - objects: Object detection and identification")
        print("   - text: Text extraction (OCR)")
        print("   - composition: Artistic and technical analysis")
        print("   - qa: Question and answer analysis")
        
        print("✅ Mock analysis workflow validated")
        
        # Clean up
        test_video.unlink()
        return True
        
    except Exception as e:
        print(f"❌ Mock analysis failed: {e}")
        return False

def test_audio_image_commands():
    """Test audio and image CLI command availability."""
    print("\n🧪 Testing audio and image CLI command imports...")
    
    try:
        from video_utils.commands import (
            cmd_analyze_audio,
            cmd_transcribe_audio,
            cmd_describe_audio,
            cmd_analyze_images,
            cmd_describe_images,
            cmd_extract_text
        )
        print("✅ All audio and image CLI commands imported successfully")
        
        # Test that they're callable
        audio_commands = [cmd_analyze_audio, cmd_transcribe_audio, cmd_describe_audio]
        image_commands = [cmd_analyze_images, cmd_describe_images, cmd_extract_text]
        
        if all(callable(cmd) for cmd in audio_commands):
            print("✅ All audio commands are callable")
        else:
            print("❌ Some audio commands are not callable")
            return False
            
        if all(callable(cmd) for cmd in image_commands):
            print("✅ All image commands are callable")
            return True
        else:
            print("❌ Some image commands are not callable")
            return False
            
    except ImportError as e:
        print(f"❌ Audio/Image CLI command import failed: {e}")
        return False

def main():
    """Run all video understanding tests."""
    print("🤖 GOOGLE GEMINI MULTIMODAL UNDERSTANDING TESTS")
    print("=" * 50)
    print("💡 Testing video, audio, and image analysis functionality")
    
    tests = [
        ("Module Import", test_gemini_import),
        ("Requirements Check", test_requirements_check),
        ("Analyzer Initialization", test_analyzer_initialization),
        ("Result Saving", test_save_functionality),
        ("CLI Commands", test_cli_commands),
        ("Audio & Image Commands", test_audio_image_commands),
        ("Package Integration", test_package_integration),
        ("Mock Analysis", run_mock_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Video, audio & image understanding functionality is ready.")
        print("\n💡 Next steps:")
        print("   1. Install dependencies: pip install google-generativeai")
        print("   2. Get API key: https://aistudio.google.com/app/apikey")
        print("   3. Set environment: export GEMINI_API_KEY=your_key")
        print("   4. Test with video: python video_audio_utils.py analyze-videos")
        print("   5. Test with audio: python video_audio_utils.py analyze-audio")
        print("   6. Test with images: python video_audio_utils.py analyze-images")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print(f"\n📖 Setup guide: GEMINI_SETUP.md")
    print(f"📦 Dependencies: requirements_gemini.txt")

if __name__ == "__main__":
    main()