"""
Whisper transcription command implementations.

Contains commands for OpenAI Whisper-based audio and video transcription.
"""

from pathlib import Path

from .file_utils import find_video_files, find_audio_files
from .whisper_transcriber import WhisperTranscriber, check_whisper_requirements
from .gemini_analyzer import GeminiVideoAnalyzer, check_gemini_requirements
from .ai_utils import transcribe_with_whisper, batch_transcribe_whisper, save_analysis_result


def cmd_whisper_transcribe():
    """Transcribe audio/video files using OpenAI Whisper."""
    print("🎤 WHISPER TRANSCRIPTION - OpenAI Speech-to-Text")
    print("=" * 50)
    
    # Set up directories
    input_dir = Path('input')
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        print(f"❌ Input directory '{input_dir}' does not exist!")
        print("💡 Please create the 'input' directory and place your audio/video files there.")
        return
    
    # Check Whisper requirements
    whisper_status = check_whisper_requirements()
    
    # Show available options
    print("📋 Available Whisper options:")
    if 'api' in whisper_status:
        api_ready, api_msg = whisper_status['api']
        status_icon = "✅" if api_ready else "❌"
        print(f"   {status_icon} OpenAI API: {api_msg}")
    
    if 'local' in whisper_status:
        local_ready, local_msg = whisper_status['local']
        status_icon = "✅" if local_ready else "❌"
        print(f"   {status_icon} Local Whisper: {local_msg}")
    
    # Check if any option is available
    if not any(ready for ready, _ in whisper_status.values()):
        print("\n❌ No Whisper options available!")
        print("💡 Install options:")
        print("   - API: pip install openai (requires OPENAI_API_KEY)")
        print("   - Local: pip install openai-whisper")
        return
    
    # Find files to transcribe
    video_files = find_video_files(input_dir)
    audio_files = find_audio_files(input_dir)
    all_files = video_files + audio_files
    
    if not all_files:
        print(f"📁 No audio or video files found in '{input_dir}' directory")
        return
    
    print(f"\n📁 Found {len(all_files)} file(s) in '{input_dir}':")
    print(f"   📹 Videos: {len(video_files)}")
    print(f"   🎵 Audio: {len(audio_files)}")
    
    # Choose transcription method
    use_local = False
    if 'api' in whisper_status and 'local' in whisper_status:
        api_ready, _ = whisper_status['api']
        local_ready, _ = whisper_status['local']
        
        if api_ready and local_ready:
            print("\n🤖 Choose transcription method:")
            print("   1. OpenAI API (faster, requires internet, costs money)")
            print("   2. Local Whisper (free, offline, requires GPU for speed)")
            
            choice = input("\n📝 Select method (1-2): ").strip()
            use_local = choice == '2'
        elif local_ready:
            use_local = True
            print("\n💻 Using local Whisper (API not available)")
        else:
            print("\n🌐 Using OpenAI API (local not available)")
    elif 'local' in whisper_status:
        local_ready, _ = whisper_status['local']
        if local_ready:
            use_local = True
            print("\n💻 Using local Whisper")
    else:
        print("\n🌐 Using OpenAI API")
    
    # Additional options
    model_size = "turbo"
    language = None
    include_timestamps = True
    
    if use_local:
        print("\n🎛️ Model options: tiny, base, small, medium, large, turbo")
        model_choice = input("📝 Choose model size (default: turbo): ").strip().lower()
        if model_choice in ['tiny', 'base', 'small', 'medium', 'large', 'turbo']:
            model_size = model_choice
    
    lang_input = input("🌍 Specify language (e.g., 'en', 'es', 'fr') or press Enter for auto-detect: ").strip()
    if lang_input:
        language = lang_input
    
    timestamps_input = input("⏰ Include timestamps? (Y/n): ").strip().lower()
    include_timestamps = timestamps_input != 'n'
    
    print(f"\n🚀 Starting transcription with {'local' if use_local else 'API'} Whisper...")
    
    try:
        results = batch_transcribe_whisper(
            all_files,
            use_local=use_local,
            model_size=model_size,
            language=language,
            save_results=True
        )
        
        successful = sum(1 for r in results if 'error' not in r)
        failed = len(results) - successful
        
        print(f"\n📊 Results: {successful} successful | {failed} failed")
        
        if successful > 0:
            print(f"\n🎉 Transcription complete!")
            print(f"📄 Files saved to '{output_dir}' with '_whisper_transcription' suffix")
            print("💡 Both JSON and TXT formats saved for each file")
            
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Transcription failed: {e}")


def cmd_whisper_compare():
    """Compare Whisper transcription with Gemini transcription."""
    print("🆚 WHISPER VS GEMINI COMPARISON")
    print("=" * 50)
    
    # Set up directories
    input_dir = Path('input')
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        print(f"❌ Input directory '{input_dir}' does not exist!")
        print("💡 Please create the 'input' directory and place your audio/video files there.")
        return
    
    # Check requirements for both
    whisper_status = check_whisper_requirements()
    gemini_ready, gemini_msg = check_gemini_requirements()
    
    print("📋 Service availability:")
    print(f"   {'✅' if gemini_ready else '❌'} Gemini API: {gemini_msg}")
    
    whisper_available = False
    for service, (ready, msg) in whisper_status.items():
        status_icon = "✅" if ready else "❌"
        print(f"   {status_icon} Whisper {service}: {msg}")
        if ready:
            whisper_available = True
    
    if not (gemini_ready and whisper_available):
        print("\n❌ Both Gemini and Whisper are required for comparison")
        return
    
    # Find audio/video files
    video_files = find_video_files(input_dir)
    audio_files = find_audio_files(input_dir)
    all_files = video_files + audio_files
    
    if not all_files:
        print(f"📁 No audio or video files found in '{input_dir}' directory")
        return
    
    print(f"\n📁 Found {len(all_files)} file(s) to compare from '{input_dir}'")
    
    # Choose Whisper method
    use_local = False
    if 'api' in whisper_status and 'local' in whisper_status:
        api_ready, _ = whisper_status['api']
        local_ready, _ = whisper_status['local']
        
        if api_ready and local_ready:
            print("\n🤖 Choose Whisper method:")
            print("   1. OpenAI API")
            print("   2. Local Whisper")
            
            choice = input("\n📝 Select method (1-2): ").strip()
            use_local = choice == '2'
    
    print(f"\n🚀 Running comparison: Gemini vs {'Local' if use_local else 'API'} Whisper...")
    
    successful_comparisons = 0
    
    for i, file_path in enumerate(all_files, 1):
        print(f"\n📁 Processing file {i}/{len(all_files)}: {file_path.name}")
        
        try:
            # Transcribe with Whisper
            print("🎤 Transcribing with Whisper...")
            whisper_result = transcribe_with_whisper(
                file_path,
                use_local=use_local,
                include_timestamps=True
            )
            
            # Transcribe with Gemini
            print("🤖 Transcribing with Gemini...")
            if file_path.suffix.lower() in {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}:
                # Video file - use Gemini video transcription
                analyzer = GeminiVideoAnalyzer()
                gemini_result = analyzer.transcribe_video(file_path, include_timestamps=True)
            else:
                # Audio file - use Gemini audio transcription
                analyzer = GeminiVideoAnalyzer()
                gemini_result = analyzer.transcribe_audio(file_path, include_timestamps=True)
            
            # Create comparison
            comparison = {
                'file': str(file_path),
                'whisper': {
                    'method': whisper_result.get('method'),
                    'model': whisper_result.get('model'),
                    'text': whisper_result.get('text'),
                    'language': whisper_result.get('language'),
                    'duration': whisper_result.get('duration')
                },
                'gemini': {
                    'method': 'google_gemini',
                    'text': gemini_result.get('transcription'),
                    'analysis_type': gemini_result.get('analysis_type')
                },
                'comparison_stats': {
                    'whisper_length': len(whisper_result.get('text', '')),
                    'gemini_length': len(gemini_result.get('transcription', '')),
                    'whisper_words': len(whisper_result.get('text', '').split()),
                    'gemini_words': len(gemini_result.get('transcription', '').split())
                }
            }
            
            # Save comparison
            comparison_file = output_dir / f"{file_path.stem}_comparison.json"
            save_analysis_result(comparison, comparison_file)
            
            # Save readable comparison
            txt_file = output_dir / f"{file_path.stem}_comparison.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"TRANSCRIPTION COMPARISON: {file_path.name}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"WHISPER ({whisper_result.get('method', 'unknown')}):\n")
                f.write("-" * 30 + "\n")
                f.write(whisper_result.get('text', 'No transcription') + "\n\n")
                f.write("GEMINI:\n")
                f.write("-" * 30 + "\n")
                f.write(gemini_result.get('transcription', 'No transcription') + "\n\n")
                f.write("STATISTICS:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Whisper: {comparison['comparison_stats']['whisper_words']} words\n")
                f.write(f"Gemini: {comparison['comparison_stats']['gemini_words']} words\n")
            
            print(f"✅ Comparison saved: {txt_file.name}")
            successful_comparisons += 1
            
        except Exception as e:
            print(f"❌ Comparison failed for {file_path.name}: {e}")
    
    print(f"\n📊 Completed {successful_comparisons}/{len(all_files)} comparisons")
    
    if successful_comparisons > 0:
        print("🎉 Comparison complete!")
        print(f"📄 Check '{output_dir}' for '_comparison.txt' files with readable results")
        print(f"📊 Check '{output_dir}' for '_comparison.json' files with detailed data")


def cmd_whisper_batch():
    """Batch transcribe files with advanced options."""
    print("📦 WHISPER BATCH TRANSCRIPTION")
    print("=" * 50)
    
    # Set up directories
    input_dir = Path('input')
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        print(f"❌ Input directory '{input_dir}' does not exist!")
        print("💡 Please create the 'input' directory and place your audio/video files there.")
        return
    
    # Check Whisper requirements
    whisper_status = check_whisper_requirements()
    
    if not any(ready for ready, _ in whisper_status.values()):
        print("❌ No Whisper options available!")
        print("💡 Install: pip install openai (API) or pip install openai-whisper (local)")
        return
    
    # Find files
    video_files = find_video_files(input_dir)
    audio_files = find_audio_files(input_dir)
    all_files = video_files + audio_files
    
    if not all_files:
        print(f"📁 No audio or video files found in '{input_dir}' directory")
        return
    
    print(f"📁 Found {len(all_files)} file(s) to process from '{input_dir}'")
    
    # Advanced configuration
    print("\n🎛️ Advanced Configuration:")
    
    # Choose method
    use_local = False
    if 'api' in whisper_status and 'local' in whisper_status:
        api_ready, _ = whisper_status['api']
        local_ready, _ = whisper_status['local']
        
        if api_ready and local_ready:
            method_choice = input("🤖 Method (1=API, 2=Local): ").strip()
            use_local = method_choice == '2'
    
    # Model selection for local
    model_size = "turbo"
    if use_local:
        model_choice = input("🎯 Model (tiny/base/small/medium/large/turbo): ").strip().lower()
        if model_choice in ['tiny', 'base', 'small', 'medium', 'large', 'turbo']:
            model_size = model_choice
    
    # Language
    language = None
    lang_input = input("🌍 Language code (en/es/fr/etc, or Enter for auto): ").strip()
    if lang_input:
        language = lang_input
    
    # Output formats
    save_json = input("💾 Save JSON results? (Y/n): ").strip().lower() != 'n'
    save_txt = input("📄 Save TXT results? (Y/n): ").strip().lower() != 'n'
    save_srt = input("🎬 Generate SRT subtitles? (y/N): ").strip().lower() == 'y'
    
    print(f"\n🚀 Starting batch transcription...")
    print(f"   Method: {'Local ' + model_size if use_local else 'OpenAI API'}")
    print(f"   Language: {language or 'Auto-detect'}")
    print(f"   Files: {len(all_files)}")
    
    try:
        successful = 0
        failed = 0
        
        for i, file_path in enumerate(all_files, 1):
            print(f"\n📁 Processing {i}/{len(all_files)}: {file_path.name}")
            
            try:
                result = transcribe_with_whisper(
                    file_path,
                    use_local=use_local,
                    model_size=model_size,
                    language=language,
                    include_timestamps=True
                )
                
                if result:
                    # Save in requested formats
                    base_name = output_dir / file_path.stem
                    
                    if save_json:
                        json_file = Path(f"{base_name}_whisper.json")
                        save_analysis_result(result, json_file)
                    
                    if save_txt:
                        txt_file = Path(f"{base_name}_whisper.txt")
                        with open(txt_file, 'w', encoding='utf-8') as f:
                            f.write(result['text'])
                    
                    if save_srt and 'segments' in result:
                        srt_file = Path(f"{base_name}_whisper.srt")
                        with open(srt_file, 'w', encoding='utf-8') as f:
                            for i, seg in enumerate(result['segments'], 1):
                                start_time = format_srt_time(seg['start'])
                                end_time = format_srt_time(seg['end'])
                                f.write(f"{i}\n")
                                f.write(f"{start_time} --> {end_time}\n")
                                f.write(f"{seg['text'].strip()}\n\n")
                    
                    successful += 1
                    print(f"✅ Success: {file_path.name}")
                else:
                    failed += 1
                    print(f"❌ Failed: {file_path.name}")
                    
            except Exception as e:
                failed += 1
                print(f"❌ Error processing {file_path.name}: {e}")
        
        print(f"\n📊 Batch Results: {successful} successful | {failed} failed")
        
        if successful > 0:
            print("🎉 Batch transcription complete!")
            print(f"📄 Results saved to '{output_dir}' directory")
            
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")


def format_srt_time(seconds):
    """Format seconds as SRT timestamp."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"