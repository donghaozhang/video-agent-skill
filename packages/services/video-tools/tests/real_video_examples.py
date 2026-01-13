#!/usr/bin/env python3
"""
Real Video Understanding Examples - Google Gemini AI

This script demonstrates how to use the video understanding functionality
with real videos, audio files, and images using Google Gemini API.

Prerequisites:
1. pip install google-generativeai python-dotenv
2. Set GEMINI_API_KEY in .env file
3. Have sample media files ready

Author: AI Assistant
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

# Add video_tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def setup_environment():
    """Setup and verify environment for Gemini API."""
    print("🔧 Setting up environment...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        env_file = Path(__file__).parent.parent / '.env'
        if env_file.exists():
            load_dotenv(env_file)
            print("✅ .env file loaded")
        else:
            print("⚠️  .env file not found")
    except ImportError:
        print("⚠️  python-dotenv not installed")
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
        return True
    else:
        print("❌ GEMINI_API_KEY not found")
        print("💡 Add your API key to .env file:")
        print("   GEMINI_API_KEY=your_actual_api_key_here")
        return False

def example_1_basic_video_description():
    """Example 1: Basic video description"""
    print("\n" + "="*60)
    print("📹 EXAMPLE 1: Basic Video Description")
    print("="*60)
    
    print("Command Line Usage:")
    print("cd /path/to/your/videos")
    print("python ../video_audio_utils.py describe-videos")
    print("# Choose 'N' for basic description")
    
    print("\nPython Function Usage:")
    print("""
from video_utils import GeminiVideoAnalyzer

# Initialize analyzer
analyzer = GeminiVideoAnalyzer()

# Analyze a video file
result = analyzer.describe_video(
    video_path='sample_video.mp4',
    detailed=False  # Basic description
)

if result:
    print("Description:", result['description'])
    print("File ID:", result['file_id'])
    print("Duration:", result.get('duration'))
""")
    
    # Live example if video exists
    video_path = Path(__file__).parent.parent / 'input/sample_video.mp4'
    if video_path.exists():
        print(f"\n🎬 Live Example with {video_path}:")
        try:
            from video_utils import GeminiVideoAnalyzer
            analyzer = GeminiVideoAnalyzer()
            result = analyzer.describe_video(video_path, detailed=False)
            if result:
                preview = result['description'][:150] + "..." if len(result['description']) > 150 else result['description']
                print(f"✅ Result: {preview}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"\n⚠️  Sample video not found at {video_path}")

def example_2_detailed_video_analysis():
    """Example 2: Detailed video analysis with multiple options"""
    print("\n" + "="*60)
    print("🎯 EXAMPLE 2: Comprehensive Video Analysis")
    print("="*60)
    
    print("Command Line Usage:")
    print("python ../video_audio_utils.py analyze-videos")
    print("# Choose option 1-5:")
    print("# 1. Video Description (detailed)")
    print("# 2. Audio Transcription") 
    print("# 3. Scene Analysis")
    print("# 4. Key Information Extraction")
    print("# 5. Custom Q&A")
    
    print("\nPython Function Usage:")
    print("""
from video_utils import analyze_video_file

# 1. Detailed Description
result = analyze_video_file(
    video_path='your_video.mp4',
    analysis_type='description',
    detailed=True
)

# 2. Audio Transcription with timestamps
result = analyze_video_file(
    video_path='your_video.mp4',
    analysis_type='transcription'
)

# 3. Scene Analysis
result = analyze_video_file(
    video_path='your_video.mp4',
    analysis_type='scenes'
)

# 4. Custom Q&A
questions = [
    "What is the main topic of this video?",
    "Who are the people in the video?",
    "What location is shown?"
]
result = analyze_video_file(
    video_path='your_video.mp4',
    analysis_type='qa',
    questions=questions
)
""")

def example_3_batch_video_processing():
    """Example 3: Batch processing multiple videos"""
    print("\n" + "="*60)
    print("📦 EXAMPLE 3: Batch Video Processing")
    print("="*60)
    
    print("Command Line Usage:")
    print("# Put all videos in one directory, then run:")
    print("cd /path/to/video/directory")
    print("python ../video_audio_utils.py describe-videos")
    print("# This will process ALL video files in the directory")
    
    print("\nPython Function Usage:")
    print("""
from pathlib import Path
from video_utils import analyze_video_file, save_analysis_result
from video_utils.file_utils import find_video_files

# Find all videos in directory
video_dir = Path('path/to/videos')
video_files = find_video_files(video_dir)

print(f"Found {len(video_files)} videos to process")

# Process each video
for video_path in video_files:
    print(f"Processing: {video_path.name}")
    
    # Analyze video
    result = analyze_video_file(
        video_path=video_path,
        analysis_type='description',
        detailed=True
    )
    
    if result:
        # Save result to JSON file
        output_file = video_path.parent / f"{video_path.stem}_analysis.json"
        save_analysis_result(result, output_file)
        print(f"Saved: {output_file.name}")
    else:
        print(f"Failed to analyze: {video_path.name}")
""")

def example_4_audio_analysis():
    """Example 4: Audio file analysis"""
    print("\n" + "="*60)
    print("🎵 EXAMPLE 4: Audio Analysis")
    print("="*60)
    
    print("Command Line Usage:")
    print("cd /path/to/audio/files")
    print("python ../video_audio_utils.py analyze-audio")
    print("python ../video_audio_utils.py transcribe-audio")
    print("python ../video_audio_utils.py describe-audio")
    
    print("\nPython Function Usage:")
    print("""
from video_utils import analyze_audio_file, GeminiVideoAnalyzer

# Method 1: Using analyze_audio_file function
result = analyze_audio_file(
    audio_path='speech.mp3',
    analysis_type='transcription',
    speaker_identification=True
)

# Method 2: Using GeminiVideoAnalyzer class
analyzer = GeminiVideoAnalyzer()

# Transcribe audio with timestamps
transcription = analyzer.transcribe_audio(
    audio_path='interview.mp3',
    include_timestamps=True,
    speaker_identification=True
)

# Describe audio content
description = analyzer.describe_audio(
    audio_path='music.mp3',
    detailed=True
)

# Content analysis (music, speech, sound effects)
content_analysis = analyze_audio_file(
    audio_path='podcast.mp3',
    analysis_type='content_analysis'
)
""")

def example_5_image_analysis():
    """Example 5: Image analysis and OCR"""
    print("\n" + "="*60)
    print("🖼️ EXAMPLE 5: Image Analysis & OCR")
    print("="*60)
    
    print("Command Line Usage:")
    print("cd /path/to/images")
    print("python ../video_audio_utils.py analyze-images")
    print("python ../video_audio_utils.py describe-images") 
    print("python ../video_audio_utils.py extract-text")
    
    print("\nPython Function Usage:")
    print("""
from video_utils import analyze_image_file, GeminiVideoAnalyzer

# Image description
result = analyze_image_file(
    image_path='photo.jpg',
    analysis_type='description',
    detailed=True
)

# Object detection
objects = analyze_image_file(
    image_path='street_scene.jpg',
    analysis_type='objects'
)

# OCR text extraction
text = analyze_image_file(
    image_path='document.png',
    analysis_type='text'
)

# Using GeminiVideoAnalyzer class
analyzer = GeminiVideoAnalyzer()

# Extract text from image
ocr_result = analyzer.extract_text_from_image('receipt.jpg')
print("Extracted text:", ocr_result['extracted_text'])

# Ask questions about image
qa_result = analyze_image_file(
    image_path='chart.png',
    analysis_type='qa',
    questions=[
        "What type of chart is this?",
        "What are the main data points?",
        "What trends can you see?"
    ]
)
""")

def example_6_whisper_integration():
    """Example 6: Whisper transcription comparison"""
    print("\n" + "="*60)
    print("🎤 EXAMPLE 6: Whisper Integration")
    print("="*60)
    
    print("Command Line Usage:")
    print("python ../video_audio_utils.py whisper-transcribe")
    print("python ../video_audio_utils.py whisper-compare")
    print("python ../video_audio_utils.py whisper-batch")
    
    print("\nPython Function Usage:")
    print("""
from video_utils import (
    transcribe_with_whisper, 
    batch_transcribe_whisper,
    check_whisper_requirements
)

# Check what's available
whisper_status = check_whisper_requirements()
print("Whisper options:", whisper_status)

# Single file transcription
result = transcribe_with_whisper(
    file_path='speech.mp3',
    use_local=True,  # Use local Whisper (free)
    model_size='base',
    language='en',
    include_timestamps=True
)

# Batch transcription
audio_files = ['file1.mp3', 'file2.wav', 'video.mp4']
results = batch_transcribe_whisper(
    file_paths=audio_files,
    use_local=False,  # Use OpenAI API
    save_results=True
)

# Compare Gemini vs Whisper
# This creates comparison files showing both transcriptions
""")

def example_7_advanced_configurations():
    """Example 7: Advanced configurations and error handling"""
    print("\n" + "="*60)
    print("⚙️ EXAMPLE 7: Advanced Usage & Error Handling")
    print("="*60)
    
    print("Python Function Usage:")
    print("""
from video_utils import GeminiVideoAnalyzer
import os

# Custom API key configuration
custom_analyzer = GeminiVideoAnalyzer(api_key="your_custom_key")

# Error handling example
def safe_video_analysis(video_path, analysis_type='description'):
    try:
        from video_utils import check_gemini_requirements
        
        # Check if API is ready
        ready, message = check_gemini_requirements()
        if not ready:
            print(f"API not ready: {message}")
            return None
        
        # Perform analysis
        analyzer = GeminiVideoAnalyzer()
        
        if analysis_type == 'description':
            result = analyzer.describe_video(video_path, detailed=True)
        elif analysis_type == 'transcription':
            result = analyzer.transcribe_video(video_path, include_timestamps=True)
        else:
            print(f"Unknown analysis type: {analysis_type}")
            return None
            
        return result
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        return None

# Usage
result = safe_video_analysis('my_video.mp4', 'description')
if result:
    print("Success:", result['description'][:100])
else:
    print("Analysis failed")

# File size and format checking
def check_video_compatibility(video_path):
    from pathlib import Path
    
    path = Path(video_path)
    if not path.exists():
        return False, "File not found"
    
    # Check file size (Gemini has limits)
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 100:  # Example limit
        return False, f"File too large: {size_mb:.1f}MB"
    
    # Check format
    supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    if path.suffix.lower() not in supported_formats:
        return False, f"Unsupported format: {path.suffix}"
    
    return True, f"Compatible video: {size_mb:.1f}MB"

# Check before analysis
compatible, message = check_video_compatibility('test.mp4')
print(message)
""")

def example_8_output_formats():
    """Example 8: Different output formats and saving options"""
    print("\n" + "="*60)
    print("💾 EXAMPLE 8: Output Formats & Saving")
    print("="*60)
    
    print("The system automatically saves results in multiple formats:")
    print("""
# When you run CLI commands, files are automatically saved:
python ../video_audio_utils.py describe-videos
# Creates: video_name_description.json (structured data)
# Creates: video_name_description.txt (readable text)

python ../video_audio_utils.py transcribe-videos  
# Creates: video_name_transcription.json (with metadata)
# Creates: video_name_transcription.txt (clean text)

python ../video_audio_utils.py whisper-batch
# Options for: JSON, TXT, and SRT subtitle files
""")
    
    print("\nPython Function Usage:")
    print("""
from video_utils import save_analysis_result
import json

# Custom saving example
result = {
    'description': 'A detailed video description...',
    'file_id': 'files/abc123',
    'analysis_type': 'description',
    'timestamp': '2024-01-01T12:00:00Z'
}

# Save as JSON (structured)
save_analysis_result(result, 'output/analysis.json')

# Save as text (readable) 
with open('output/analysis.txt', 'w') as f:
    f.write(result['description'])

# Save as CSV for batch processing
import csv
results = [result1, result2, result3]  # Multiple analysis results

with open('batch_results.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['file_id', 'description', 'analysis_type'])
    writer.writeheader()
    for r in results:
        writer.writerow({
            'file_id': r['file_id'],
            'description': r['description'][:100],  # Truncate for CSV
            'analysis_type': r['analysis_type']
        })
""")

def main():
    """Run all real-world examples."""
    print("🎬 REAL VIDEO UNDERSTANDING EXAMPLES")
    print("="*70)
    print("💡 Comprehensive guide to using Google Gemini AI video analysis")
    
    if not setup_environment():
        print("\n❌ Environment setup failed. Please configure your API key first.")
        return
    
    examples = [
        example_1_basic_video_description,
        example_2_detailed_video_analysis, 
        example_3_batch_video_processing,
        example_4_audio_analysis,
        example_5_image_analysis,
        example_6_whisper_integration,
        example_7_advanced_configurations,
        example_8_output_formats
    ]
    
    print(f"\n📚 Running {len(examples)} comprehensive examples...")
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Example {i} error: {e}")
    
    print("\n" + "="*70)
    print("🎉 EXAMPLES COMPLETE!")
    print("="*70)
    print("\n💡 Quick Start Commands:")
    print("   python ../video_audio_utils.py describe-videos")
    print("   python ../video_audio_utils.py analyze-videos") 
    print("   python ../video_audio_utils.py transcribe-videos")
    print("   python ../video_audio_utils.py analyze-audio")
    print("   python ../video_audio_utils.py analyze-images")
    print("\n📖 For more help: python ../video_audio_utils.py --help")

if __name__ == "__main__":
    main()