"""
AI utilities and convenience functions for video, audio, and image analysis.

Provides high-level convenience functions that wrap the underlying AI analyzers
and transcribers, making it easy to perform common analysis tasks.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from .gemini_analyzer import GeminiVideoAnalyzer, check_gemini_requirements
from .whisper_transcriber import WhisperTranscriber, check_whisper_requirements
from .analyzer_factory import get_analyzer, AnalyzerFactory, print_provider_status


def save_analysis_result(result: Dict[str, Any], output_path: Path) -> bool:
    """Save analysis result to JSON and text files.
    
    Args:
        result: Analysis result dictionary
        output_path: Output file path (without extension)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Save JSON version
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Save text version for readability
        txt_path = output_path.with_suffix('.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Analysis Type: {result.get('analysis_type', 'unknown')}\n")
            f.write(f"File: {result.get('source_file', 'unknown')}\n")
            f.write(f"Timestamp: {result.get('timestamp', 'unknown')}\n")
            f.write("=" * 50 + "\n\n")
            
            # Write main content based on analysis type
            if 'description' in result:
                f.write(result['description'])
            elif 'transcription' in result:
                f.write(result['transcription'])
            elif 'answers' in result:
                f.write("Questions and Answers:\n\n")
                f.write(result['answers'])
            elif 'scene_analysis' in result:
                f.write("Scene Analysis:\n\n")
                f.write(result['scene_analysis'])
            elif 'key_info' in result:
                f.write("Key Information:\n\n")
                f.write(result['key_info'])
            elif 'content_analysis' in result:
                f.write("Content Analysis:\n\n")
                f.write(result['content_analysis'])
            elif 'event_detection' in result:
                f.write("Event Detection:\n\n")
                f.write(result['event_detection'])
            elif 'classification' in result:
                f.write("Classification:\n\n")
                f.write(result['classification'])
            elif 'object_detection' in result:
                f.write("Object Detection:\n\n")
                f.write(result['object_detection'])
            elif 'extracted_text' in result:
                f.write("Extracted Text:\n\n")
                f.write(result['extracted_text'])
            elif 'composition_analysis' in result:
                f.write("Composition Analysis:\n\n")
                f.write(result['composition_analysis'])
            elif 'text' in result:
                f.write("Transcription:\n\n")
                f.write(result['text'])
            else:
                f.write("Result:\n\n")
                f.write(str(result))
        
        print(f"💾 Results saved: {json_path.name} and {txt_path.name}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        return False


def analyze_video_file(video_path: Path, analysis_type: str = "description",
                      questions: Optional[List[str]] = None, detailed: bool = False,
                      provider: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
    """Convenience function to analyze video.

    Args:
        video_path: Path to video file (or URL for FAL provider)
        analysis_type: Type of analysis ('description', 'transcription', 'scenes', 'extraction', 'qa')
        questions: List of questions for Q&A analysis
        detailed: Whether to perform detailed analysis
        provider: Provider to use ('gemini', 'fal'). Defaults to MEDIA_ANALYZER_PROVIDER env var
        **kwargs: Additional provider-specific arguments (e.g., model for FAL)

    Returns:
        Analysis result dictionary or None if failed
    """
    try:
        # Use factory to get analyzer - defaults to Gemini for backward compatibility
        analyzer = get_analyzer(provider=provider, **kwargs)

        if analysis_type == "description":
            return analyzer.describe_video(video_path, detailed=detailed)
        elif analysis_type == "transcription":
            return analyzer.transcribe_video(video_path, include_timestamps=True)
        elif analysis_type == "scenes":
            return analyzer.analyze_scenes(video_path)
        elif analysis_type == "extraction":
            return analyzer.extract_key_info(video_path)
        elif analysis_type == "qa" and questions:
            return analyzer.answer_questions(video_path, questions)
        else:
            print(f"❌ Unknown analysis type: {analysis_type}")
            return None

    except Exception as e:
        print(f"❌ Video analysis failed: {e}")
        return None


def analyze_audio_file(audio_path: Path, analysis_type: str = "description",
                      questions: Optional[List[str]] = None, detailed: bool = False,
                      speaker_identification: bool = True,
                      provider: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
    """Convenience function to analyze audio.

    Args:
        audio_path: Path to audio file (or URL for FAL provider)
        analysis_type: Type of analysis ('description', 'transcription', 'content_analysis', 'event_detection', 'qa')
        questions: List of questions for Q&A analysis
        detailed: Whether to perform detailed analysis
        speaker_identification: Whether to identify speakers in transcription
        provider: Provider to use ('gemini', 'fal'). Defaults to MEDIA_ANALYZER_PROVIDER env var
        **kwargs: Additional provider-specific arguments (e.g., model for FAL)

    Returns:
        Analysis result dictionary or None if failed
    """
    try:
        # Use factory to get analyzer - defaults to Gemini for backward compatibility
        analyzer = get_analyzer(provider=provider, **kwargs)

        if analysis_type == "description":
            return analyzer.describe_audio(audio_path, detailed=detailed)
        elif analysis_type == "transcription":
            return analyzer.transcribe_audio(audio_path, include_timestamps=True,
                                           speaker_identification=speaker_identification)
        elif analysis_type == "content_analysis":
            return analyzer.analyze_audio_content(audio_path)
        elif analysis_type == "event_detection":
            return analyzer.detect_audio_events(audio_path)
        elif analysis_type == "qa" and questions:
            return analyzer.answer_audio_questions(audio_path, questions)
        else:
            print(f"❌ Unknown analysis type: {analysis_type}")
            return None

    except Exception as e:
        print(f"❌ Audio analysis failed: {e}")
        return None


def analyze_image_file(image_path: Path, analysis_type: str = "description",
                      questions: Optional[List[str]] = None, detailed: bool = False,
                      provider: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
    """Convenience function to analyze image.

    Args:
        image_path: Path to image file (or URL for FAL provider)
        analysis_type: Type of analysis ('description', 'classification', 'object_detection', 'text_extraction', 'composition', 'qa')
        questions: List of questions for Q&A analysis
        detailed: Whether to perform detailed analysis
        provider: Provider to use ('gemini', 'fal'). Defaults to MEDIA_ANALYZER_PROVIDER env var
        **kwargs: Additional provider-specific arguments (e.g., model for FAL)

    Returns:
        Analysis result dictionary or None if failed
    """
    try:
        # Use factory to get analyzer - defaults to Gemini for backward compatibility
        analyzer = get_analyzer(provider=provider, **kwargs)

        if analysis_type == "description":
            return analyzer.describe_image(image_path, detailed=detailed)
        elif analysis_type == "classification":
            return analyzer.classify_image(image_path)
        elif analysis_type == "object_detection":
            return analyzer.detect_objects(image_path, detailed=detailed)
        elif analysis_type == "text_extraction":
            return analyzer.extract_text_from_image(image_path)
        elif analysis_type == "composition":
            return analyzer.analyze_image_composition(image_path)
        elif analysis_type == "qa" and questions:
            return analyzer.answer_image_questions(image_path, questions)
        else:
            print(f"❌ Unknown analysis type: {analysis_type}")
            return None

    except Exception as e:
        print(f"❌ Image analysis failed: {e}")
        return None


def transcribe_with_whisper(file_path: Path, use_local: bool = False, model_size: str = "turbo",
                           language: Optional[str] = None, include_timestamps: bool = True) -> Optional[Dict[str, Any]]:
    """Convenience function to transcribe audio/video using Whisper.
    
    Args:
        file_path: Path to audio or video file
        use_local: Whether to use local Whisper model
        model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large', 'turbo')
        language: Language code (e.g., 'en', 'es', 'fr')
        include_timestamps: Whether to include timestamps
        
    Returns:
        Transcription result dictionary or None if failed
    """
    try:
        transcriber = WhisperTranscriber(use_local=use_local)
        
        # Determine if it's a video or audio file
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        is_video = file_path.suffix.lower() in video_extensions
        
        if is_video:
            return transcriber.transcribe_video_audio(
                file_path, 
                model_size=model_size,
                language=language,
                include_timestamps=include_timestamps
            )
        else:
            return transcriber.transcribe_audio_file(
                file_path,
                model_size=model_size,
                language=language,
                include_timestamps=include_timestamps
            )
            
    except Exception as e:
        print(f"❌ Whisper transcription failed: {e}")
        return None


def batch_transcribe_whisper(file_paths: List[Path], use_local: bool = False, model_size: str = "turbo",
                            language: Optional[str] = None, save_results: bool = True) -> List[Dict[str, Any]]:
    """Convenience function to batch transcribe files using Whisper.
    
    Args:
        file_paths: List of audio/video file paths
        use_local: Whether to use local Whisper model
        model_size: Whisper model size
        language: Language code
        save_results: Whether to save results to files
        
    Returns:
        List of transcription results
    """
    try:
        transcriber = WhisperTranscriber(use_local=use_local)
        
        return transcriber.batch_transcribe(
            file_paths,
            save_results=save_results,
            model_size=model_size,
            language=language,
            include_timestamps=True
        )
        
    except Exception as e:
        print(f"❌ Batch transcription failed: {e}")
        return []


def analyze_media_comprehensively(file_path: Path, output_dir: Optional[Path] = None,
                                save_results: bool = True) -> Dict[str, Any]:
    """Perform comprehensive analysis of a media file using multiple methods.
    
    Args:
        file_path: Path to media file (video, audio, or image)
        output_dir: Directory to save results
        save_results: Whether to save results to files
        
    Returns:
        Dictionary containing all analysis results
    """
    if output_dir is None:
        output_dir = Path.cwd() / "comprehensive_analysis"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        'file_path': str(file_path),
        'file_type': None,
        'gemini_analysis': {},
        'whisper_transcription': None,
        'errors': []
    }
    
    # Determine file type
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    audio_extensions = {'.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma'}
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    file_ext = file_path.suffix.lower()
    
    if file_ext in video_extensions:
        results['file_type'] = 'video'
        
        # Video analysis with Gemini
        try:
            print("🎬 Performing comprehensive video analysis...")
            
            # Description
            desc_result = analyze_video_file(file_path, "description", detailed=True)
            if desc_result:
                results['gemini_analysis']['description'] = desc_result
            
            # Scene analysis
            scene_result = analyze_video_file(file_path, "scenes")
            if scene_result:
                results['gemini_analysis']['scenes'] = scene_result
            
            # Key information extraction
            key_result = analyze_video_file(file_path, "extraction")
            if key_result:
                results['gemini_analysis']['key_info'] = key_result
            
            # Gemini transcription
            transcribe_result = analyze_video_file(file_path, "transcription")
            if transcribe_result:
                results['gemini_analysis']['transcription'] = transcribe_result
            
        except Exception as e:
            results['errors'].append(f"Gemini video analysis error: {e}")
        
        # Whisper transcription
        try:
            print("🎤 Performing Whisper transcription...")
            whisper_result = transcribe_with_whisper(file_path, use_local=False)
            if whisper_result:
                results['whisper_transcription'] = whisper_result
        except Exception as e:
            results['errors'].append(f"Whisper transcription error: {e}")
    
    elif file_ext in audio_extensions:
        results['file_type'] = 'audio'
        
        # Audio analysis with Gemini
        try:
            print("🎵 Performing comprehensive audio analysis...")
            
            # Description
            desc_result = analyze_audio_file(file_path, "description", detailed=True)
            if desc_result:
                results['gemini_analysis']['description'] = desc_result
            
            # Content analysis
            content_result = analyze_audio_file(file_path, "content_analysis")
            if content_result:
                results['gemini_analysis']['content_analysis'] = content_result
            
            # Event detection
            event_result = analyze_audio_file(file_path, "event_detection")
            if event_result:
                results['gemini_analysis']['event_detection'] = event_result
            
            # Gemini transcription
            transcribe_result = analyze_audio_file(file_path, "transcription")
            if transcribe_result:
                results['gemini_analysis']['transcription'] = transcribe_result
            
        except Exception as e:
            results['errors'].append(f"Gemini audio analysis error: {e}")
        
        # Whisper transcription
        try:
            print("🎤 Performing Whisper transcription...")
            whisper_result = transcribe_with_whisper(file_path, use_local=False)
            if whisper_result:
                results['whisper_transcription'] = whisper_result
        except Exception as e:
            results['errors'].append(f"Whisper transcription error: {e}")
    
    elif file_ext in image_extensions:
        results['file_type'] = 'image'
        
        # Image analysis with Gemini
        try:
            print("🖼️ Performing comprehensive image analysis...")
            
            # Description
            desc_result = analyze_image_file(file_path, "description", detailed=True)
            if desc_result:
                results['gemini_analysis']['description'] = desc_result
            
            # Classification
            class_result = analyze_image_file(file_path, "classification")
            if class_result:
                results['gemini_analysis']['classification'] = class_result
            
            # Object detection
            obj_result = analyze_image_file(file_path, "object_detection", detailed=True)
            if obj_result:
                results['gemini_analysis']['object_detection'] = obj_result
            
            # Text extraction (OCR)
            text_result = analyze_image_file(file_path, "text_extraction")
            if text_result:
                results['gemini_analysis']['text_extraction'] = text_result
            
            # Composition analysis
            comp_result = analyze_image_file(file_path, "composition")
            if comp_result:
                results['gemini_analysis']['composition'] = comp_result
            
        except Exception as e:
            results['errors'].append(f"Gemini image analysis error: {e}")
    
    else:
        results['file_type'] = 'unknown'
        results['errors'].append(f"Unsupported file type: {file_ext}")
    
    # Save comprehensive results
    if save_results:
        output_file = output_dir / f"{file_path.stem}_comprehensive_analysis"
        save_analysis_result(results, output_file)
    
    # Print summary
    if results['errors']:
        print(f"\n⚠️ Analysis completed with {len(results['errors'])} errors:")
        for error in results['errors']:
            print(f"   - {error}")
    else:
        print("\n✅ Comprehensive analysis completed successfully")
    
    analysis_count = len(results['gemini_analysis'])
    if results['whisper_transcription']:
        analysis_count += 1
    
    print(f"📊 Total analyses performed: {analysis_count}")
    
    return results


def check_ai_requirements() -> Dict[str, Dict[str, tuple[bool, str]]]:
    """Check all AI service requirements.
    
    Returns:
        Dictionary with requirement check results for all services
    """
    results = {}
    
    # Check Gemini requirements
    gemini_available, gemini_message = check_gemini_requirements()
    results['gemini'] = {'status': (gemini_available, gemini_message)}
    
    # Check Whisper requirements
    whisper_results = check_whisper_requirements()
    results['whisper'] = whisper_results
    
    return results


def print_ai_status():
    """Print the status of all AI services."""
    print("🤖 AI Services Status Check")
    print("=" * 40)
    
    requirements = check_ai_requirements()
    
    # Gemini status
    gemini_available, gemini_message = requirements['gemini']['status']
    gemini_icon = "✅" if gemini_available else "❌"
    print(f"{gemini_icon} Gemini AI: {gemini_message}")
    
    # Whisper status
    whisper_req = requirements['whisper']
    
    if 'api' in whisper_req:
        api_available, api_message = whisper_req['api']
        api_icon = "✅" if api_available else "❌"
        print(f"{api_icon} Whisper API: {api_message}")
    
    if 'local' in whisper_req:
        local_available, local_message = whisper_req['local']
        local_icon = "✅" if local_available else "❌"
        print(f"{local_icon} Whisper Local: {local_message}")
    
    if 'ffmpeg' in whisper_req:
        ffmpeg_available, ffmpeg_message = whisper_req['ffmpeg']
        ffmpeg_icon = "✅" if ffmpeg_available else "❌"
        print(f"{ffmpeg_icon} FFmpeg: {ffmpeg_message}")
    
    # Overall status
    all_available = (
        gemini_available and 
        (whisper_req.get('api', (False, ''))[0] or whisper_req.get('local', (False, ''))[0]) and
        whisper_req.get('ffmpeg', (False, ''))[0]
    )
    
    print("\n" + "=" * 40)
    if all_available:
        print("🎉 All AI services are ready!")
    else:
        print("⚠️ Some AI services need setup")
        print("\n💡 Setup instructions:")
        
        if not gemini_available:
            print("   Gemini: Set GEMINI_API_KEY environment variable")
            print("   Get key: https://aistudio.google.com/app/apikey")
        
        if not whisper_req.get('api', (False, ''))[0] and not whisper_req.get('local', (False, ''))[0]:
            print("   Whisper: Set OPENAI_API_KEY or install: pip install openai-whisper")
        
        if not whisper_req.get('ffmpeg', (False, ''))[0]:
            print("   FFmpeg: Install ffmpeg for video/audio processing")