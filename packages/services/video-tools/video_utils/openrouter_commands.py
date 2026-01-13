"""
OpenRouter-specific command implementations.

Contains commands for AI-powered image analysis using OpenRouter's unified API.
"""

import time
from pathlib import Path

from .file_utils import find_image_files
from .ai_utils import save_analysis_result
from .gemini_analyzer import GeminiVideoAnalyzer
from .openrouter_analyzer import OpenRouterAnalyzer, check_openrouter_requirements


def cmd_analyze_images_openrouter():
    """Comprehensive image analysis using OpenRouter (Gemini via unified API)."""
    print("🌐 IMAGE ANALYSIS - OpenRouter (Gemini)")
    print("=" * 50)
    
    # Check requirements
    openrouter_ready, message = check_openrouter_requirements()
    if not openrouter_ready:
        print(f"❌ OpenRouter not available: {message}")
        if "not installed" in message:
            print("📥 Install with: pip install openai")
        if "not set" in message:
            print("🔑 Set API key: export OPENROUTER_API_KEY=your_api_key")
            print("🌐 Get API key: https://openrouter.ai/keys")
        return
    
    input_dir = Path('input')
    output_dir = Path('output')
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        print("📁 Input directory 'input' not found")
        print("💡 Create an 'input' directory and place your image files there")
        return
    
    image_files = find_image_files(input_dir)
    
    if not image_files:
        print("📁 No image files found in input directory")
        return
    
    print(f"🖼️ Found {len(image_files)} image file(s)")
    
    # Model selection
    available_models = [
        ("google/gemini-2.0-flash-001", "Gemini 2.0 Flash (Latest, Fast)"),
        ("google/gemini-pro-1.5", "Gemini 1.5 Pro (High Quality)"), 
        ("google/gemini-flash-1.5", "Gemini 1.5 Flash (Fast)"),
        ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet (Alternative)")
    ]
    
    print("\n🤖 Available models:")
    for i, (model_id, description) in enumerate(available_models, 1):
        print(f"   {i}. {description}")
    
    try:
        model_choice = input(f"\n🔢 Select model (1-{len(available_models)}, default=1): ").strip()
        if not model_choice:
            model_choice = '1'
            print("🤖 Using default: Gemini 2.0 Flash")
        
        model_index = int(model_choice) - 1
        if 0 <= model_index < len(available_models):
            selected_model, model_name = available_models[model_index]
        else:
            print("❌ Invalid selection, using default")
            selected_model, model_name = available_models[0]
        
        print(f"✅ Selected: {model_name}")
    except (ValueError, KeyboardInterrupt):
        selected_model, model_name = available_models[0]
        print(f"✅ Using default: {model_name}")
    
    # Analysis type selection
    analysis_types = {
        '1': ('description', 'Image description and visual analysis'),
        '2': ('classification', 'Image classification and categorization'),
        '3': ('objects', 'Object detection and identification'),
        '4': ('text', 'Text extraction (OCR) from images'),
        '5': ('composition', 'Artistic and technical composition analysis'),
        '6': ('qa', 'Question and answer analysis')
    }
    
    print("\n🎯 Available analysis types:")
    for key, (type_name, description) in analysis_types.items():
        print(f"   {key}. {description}")
    
    try:
        choice = input("\n📝 Select analysis type (1-6): ").strip()
        if choice not in analysis_types:
            print("❌ Invalid selection")
            return
        
        analysis_type, _ = analysis_types[choice]
        
        # Additional options
        detailed = False
        questions = None
        
        if analysis_type in ['description', 'objects']:
            detailed = input("📖 Detailed analysis? (y/N): ").strip().lower() == 'y'
        elif analysis_type == 'qa':
            print("\n❓ Enter questions (one per line, empty line to finish):")
            questions = []
            while True:
                q = input("   Question: ").strip()
                if not q:
                    break
                questions.append(q)
            if not questions:
                questions = ["What is the main subject of this image?", "What can you tell me about this image?"]
        
        # Initialize OpenRouter analyzer
        analyzer = OpenRouterAnalyzer(model=selected_model)
        
        successful = 0
        failed = 0
        
        for image_path in image_files:
            print(f"\n🖼️ Analyzing: {image_path.name}")
            
            try:
                # Perform analysis based on type
                if analysis_type == 'description':
                    result_text = analyzer.describe_image(image_path, detailed)
                elif analysis_type == 'classification':
                    result_text = analyzer.classify_image(image_path)
                elif analysis_type == 'objects':
                    result_text = analyzer.detect_objects(image_path, detailed)
                elif analysis_type == 'text':
                    result_text = analyzer.extract_text_from_image(image_path)
                elif analysis_type == 'composition':
                    result_text = analyzer.analyze_image_composition(image_path)
                elif analysis_type == 'qa':
                    result_text = analyzer.answer_image_questions(image_path, questions)
                
                if result_text:
                    # Create result structure compatible with existing code
                    result = {
                        'analysis_type': analysis_type,
                        'model': selected_model,
                        'provider': 'OpenRouter',
                        'timestamp': time.time(),
                        analysis_type: result_text,  # Dynamic key based on analysis type
                        'image_path': str(image_path),
                        'detailed': detailed if analysis_type in ['description', 'objects'] else None,
                        'questions': questions if analysis_type == 'qa' else None
                    }
                    
                    # Save result
                    output_file = output_dir / f"{image_path.stem}_{analysis_type}_openrouter.json"
                    if save_analysis_result(result, output_file):
                        successful += 1
                        
                        # Save text version too
                        txt_file = output_dir / f"{image_path.stem}_{analysis_type}_openrouter.txt"
                        with open(txt_file, 'w', encoding='utf-8') as f:
                            f.write(f"OpenRouter Image Analysis: {image_path.name}\n")
                            f.write("=" * 50 + "\n\n")
                            f.write(f"Model: {model_name}\n")
                            f.write(f"Analysis Type: {analysis_type}\n\n")
                            f.write(result_text)
                        
                        # Show preview of result
                        print(f"\n📋 Analysis Preview:")
                        preview = result_text[:200] + "..." if len(result_text) > 200 else result_text
                        print(f"'{preview}'")
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"❌ Analysis failed: {e}")
                failed += 1
        
        print(f"\n📊 Results: {successful} successful | {failed} failed")
        
        if successful > 0:
            print(f"\n🎉 Analysis complete! Check JSON and TXT files for full results.")
            print("💡 OpenRouter provides access to multiple AI models through unified API")
            
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")


def cmd_openrouter_info():
    """Display information about OpenRouter integration."""
    print("🌐 OPENROUTER INTEGRATION INFO")
    print("=" * 50)
    
    print("📋 About OpenRouter:")
    print("   • Unified API access to 400+ AI models")
    print("   • OpenAI-compatible interface")
    print("   • Multiple providers: Google, Anthropic, Meta, etc.")
    print("   • Cost-effective model access")
    print("")
    
    print("🤖 Supported Models (Image Analysis):")
    print("   • Google Gemini 2.0 Flash (Latest, Fast)")
    print("   • Google Gemini 1.5 Pro (High Quality)")
    print("   • Google Gemini 1.5 Flash (Balanced)")
    print("   • Anthropic Claude 3.5 Sonnet (Alternative)")
    print("")
    
    print("✅ Supported Features:")
    print("   • Image description and analysis")
    print("   • Image classification")
    print("   • Object detection")
    print("   • OCR text extraction")
    print("   • Composition analysis")
    print("   • Custom Q&A")
    print("")
    
    print("⚠️ Limitations:")
    print("   • Video analysis requires file upload (not supported)")
    print("   • Audio analysis requires file upload (not supported)")
    print("   • Use direct Gemini API for video/audio processing")
    print("")
    
    print("🔧 Setup:")
    print("   1. Get API key: https://openrouter.ai/keys")
    print("   2. Set environment: export OPENROUTER_API_KEY=your_key")
    print("   3. Install requirements: pip install openai")
    print("")
    
    # Check current setup
    openrouter_ready, message = check_openrouter_requirements()
    if openrouter_ready:
        print("✅ OpenRouter is ready to use!")
    else:
        print(f"❌ Setup required: {message}")
        
    print("\n💡 Use 'analyze-images-openrouter' command to get started!")


def cmd_compare_providers():
    """Compare analysis results between Gemini direct and OpenRouter."""
    print("⚖️ PROVIDER COMPARISON - Gemini Direct vs OpenRouter")
    print("=" * 60)
    
    # Check both providers
    from .gemini_analyzer import check_gemini_requirements
    gemini_ready, gemini_msg = check_gemini_requirements()
    openrouter_ready, openrouter_msg = check_openrouter_requirements()
    
    if not gemini_ready:
        print(f"❌ Gemini not available: {gemini_msg}")
    else:
        print("✅ Gemini Direct API ready")
        
    if not openrouter_ready:
        print(f"❌ OpenRouter not available: {openrouter_msg}")
    else:
        print("✅ OpenRouter API ready")
    
    if not (gemini_ready and openrouter_ready):
        print("\n💡 Both providers required for comparison")
        return
    
    input_dir = Path('input')
    output_dir = Path('output')
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        print("📁 Input directory 'input' not found")
        print("💡 Create an 'input' directory and place your image files there")
        return
    
    image_files = find_image_files(input_dir)
    
    if not image_files:
        print("📁 No image files found in input directory")
        return
    
    # Limit to first few images for comparison
    if len(image_files) > 3:
        print(f"🖼️ Found {len(image_files)} images, comparing first 3 for performance")
        image_files = image_files[:3]
    else:
        print(f"🖼️ Found {len(image_files)} image file(s) for comparison")
    
    try:
        # Initialize both analyzers
        gemini_analyzer = GeminiVideoAnalyzer()
        openrouter_analyzer = OpenRouterAnalyzer(model="google/gemini-2.0-flash-001")
        
        print("\n🔄 Running comparison analysis...")
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n📷 Image {i}: {image_path.name}")
            print("-" * 40)
            
            # Gemini Direct Analysis
            print("🔗 Gemini Direct Analysis...")
            try:
                start_time = time.time()
                gemini_result = gemini_analyzer.describe_image(image_path, detailed=False)
                gemini_time = time.time() - start_time
                gemini_desc = gemini_result.get('description', 'Analysis failed') if gemini_result else 'Analysis failed'
                print(f"⏱️ Time: {gemini_time:.1f}s")
                print(f"📝 Result: {gemini_desc[:100]}...")
            except Exception as e:
                gemini_desc = f"Error: {str(e)}"
                gemini_time = 0
                print(f"❌ Failed: {e}")
            
            # OpenRouter Analysis  
            print("\n🌐 OpenRouter Analysis...")
            try:
                start_time = time.time()
                openrouter_desc = openrouter_analyzer.describe_image(image_path, detailed=False)
                openrouter_time = time.time() - start_time
                print(f"⏱️ Time: {openrouter_time:.1f}s")
                print(f"📝 Result: {openrouter_desc[:100]}...")
            except Exception as e:
                openrouter_desc = f"Error: {str(e)}"
                openrouter_time = 0
                print(f"❌ Failed: {e}")
            
            # Save comparison results
            comparison_result = {
                'image': str(image_path),
                'timestamp': time.time(),
                'gemini_direct': {
                    'result': gemini_desc,
                    'processing_time': gemini_time,
                    'provider': 'Google Gemini Direct'
                },
                'openrouter': {
                    'result': openrouter_desc,
                    'processing_time': openrouter_time,
                    'provider': 'OpenRouter (Gemini 2.0 Flash)'
                },
                'comparison': {
                    'speed_winner': 'gemini' if gemini_time < openrouter_time else 'openrouter',
                    'speed_difference': abs(gemini_time - openrouter_time)
                }
            }
            
            # Save comparison
            comp_file = output_dir / f"{image_path.stem}_comparison.json"
            save_analysis_result(comparison_result, comp_file)
            
            print(f"\n💾 Comparison saved: {comp_file.name}")
        
        print(f"\n📊 Comparison complete!")
        print("💡 Check comparison JSON files for detailed results")
        print("🔍 Both providers use Gemini models but with different APIs")
        
    except KeyboardInterrupt:
        print("\n👋 Comparison cancelled by user")