# Avatar Video Generation Suite

Generate talking avatar videos from images using multiple AI providers. This implementation provides Python interfaces for creating lip-synced avatar videos with text-to-speech conversion, custom audio files, and multi-person conversations.

## 🎭 Available Models

### FAL AI Avatar Models
- **Text-to-Speech**: Convert text to talking avatar videos with 20 voice options
- **Audio-to-Avatar**: Use custom audio files for lip-sync animation  
- **Multi-Audio Conversation**: Two-person conversations with sequential speaking

### Replicate MultiTalk Model (DEPRECATED)

> **⚠️ DEPRECATED**: The Replicate MultiTalk model is deprecated. Use the **FAL AI Avatar Multi** model instead for multi-person conversations. See migration guide: `issues/migrate-replicate-to-fal-avatar.md`

- **Multi-Person Conversations**: Audio-driven conversational videos (up to 2 people)
- **Advanced Lip-Sync**: Natural facial expressions and mouth movements
- **Flexible Audio Input**: Support for single or dual audio tracks

### FAL AI Avatar Multi (Recommended)
- **Native Multi-Person Support**: Built-in 2-person conversation via `second_audio_url`
- **Commercial License**: Fully licensed for commercial use
- **Unified API**: Consistent with other FAL avatar models

## 🎭 Features

- **Triple-Mode Avatar Generation**:
  - **Text-to-Speech**: Convert text to talking avatar videos with 20 voice options
  - **Audio-to-Avatar**: Use custom audio files for lip-sync animation
  - **Multi-Audio Conversation**: Two-person conversations with sequential speaking
- **Natural Lip-Sync Technology**: Automatic mouth movement synchronization
- **Natural Expressions**: AI-generated facial expressions and movements
- **Conversation Support**: Multi-person dialogue with seamless transitions
- **Customizable Parameters**: Frame count, voice selection, prompts
- **Turbo Mode**: Faster generation with optimized processing
- **Local & Remote Support**: Both local files and URLs for images/audio
- **Cost-Conscious Testing**: Separate FREE and PAID test suites

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually for FAL AI
pip install fal-client requests python-dotenv

# For Replicate MultiTalk
pip install replicate requests python-dotenv
```

### 2. Configuration

Create a `.env` file with your API keys:

```env
# For FAL AI Avatar models
FAL_KEY=your-fal-ai-api-key-here

# For Replicate MultiTalk model
REPLICATE_API_TOKEN=your-replicate-api-token-here
```

Get API keys from:
- FAL AI: https://fal.ai/dashboard
- Replicate: https://replicate.com/account/api-tokens

### 3. Basic Usage

#### Official FAL AI Example (Recommended Start)

```python
from fal_avatar_generator import FALAvatarGenerator

# Initialize generator
generator = FALAvatarGenerator()

# Generate using exact official FAL AI example
# Uses: Bill voice, official image, official text, official prompt
result = generator.generate_official_example(
    output_path="output/official_example.mp4"
)

print(f"Official example video: {result['video']['url']}")
```

#### Text-to-Speech Mode (20 voices available)

```python
from fal_avatar_generator import FALAvatarGenerator

# Initialize generator
generator = FALAvatarGenerator()

# Generate avatar video from text (uses official example defaults)
result = generator.generate_avatar_video(
    image_url="path/to/your/image.jpg",
    text_input="Hello! This is my avatar speaking.",
    voice="Bill",  # Default: Bill (from official example)
    output_path="output/avatar_video.mp4"
)

print(f"Video generated: {result['video']['url']}")
```

#### Audio-to-Avatar Mode (custom audio files)

```python
from fal_avatar_generator import FALAvatarGenerator

# Initialize generator
generator = FALAvatarGenerator()

# Generate avatar video from audio file
result = generator.generate_avatar_from_audio(
    image_url="path/to/your/image.jpg",
    audio_url="path/to/your/audio.mp3",
    output_path="output/avatar_video.mp4"
)

print(f"Video generated: {result['video']['url']}")
```

#### Multi-Audio Conversation Mode (two-person dialogue)

```python
from fal_avatar_generator import FALAvatarGenerator

# Initialize generator
generator = FALAvatarGenerator()

# Generate multi-person conversation video
result = generator.generate_multi_avatar_conversation(
    image_url="path/to/your/image.jpg",
    first_audio_url="path/to/person1_audio.mp3",
    second_audio_url="path/to/person2_audio.mp3",
    prompt="Two people engaged in a natural conversation, speaking in sequence.",
    output_path="output/conversation_video.mp4"
)

print(f"Conversation video generated: {result['video']['url']}")
```

#### FAL AI Avatar Multi (Recommended for Conversations)

```python
from fal_avatar import FALAvatarGenerator

# Initialize generator
generator = FALAvatarGenerator()

# Single person video
result = generator.generate_conversation(
    image_url="path/to/your/image.jpg",
    first_audio_url="path/to/your/audio.mp3",
    prompt="A person speaking naturally with clear expressions"
)

# Multi-person conversation
result = generator.generate_conversation(
    image_url="path/to/two_people.jpg",
    first_audio_url="path/to/person1_audio.mp3",
    second_audio_url="path/to/person2_audio.mp3",
    prompt="A smiling man and woman hosting a podcast",
    num_frames=100,
    resolution="720p"
)

print(f"Video generated: {result.video_url}")
```

#### Replicate MultiTalk Model (DEPRECATED)

> **⚠️ DEPRECATED**: Use FAL AI Avatar Multi above instead.

```python
from replicate_multitalk_generator import ReplicateMultiTalkGenerator

# Initialize generator (will show deprecation warning)
generator = ReplicateMultiTalkGenerator()

# Single person video
result = generator.generate_single_person_video(
    image_url="path/to/your/image.jpg",
    audio_url="path/to/your/audio.mp3",
    prompt="A person speaking naturally with clear expressions",
    output_path="output/single_person.mp4"
)

# Multi-person conversation
result = generator.generate_conversation_video(
    image_url="path/to/two_people.jpg",
    first_audio_url="path/to/person1_audio.mp3",
    second_audio_url="path/to/person2_audio.mp3",
    prompt="A smiling man and woman hosting a podcast",
    num_frames=120,
    output_path="output/conversation.mp4"
)

print(f"MultiTalk video generated: {result['video']['url']}")
```

### 4. Interactive Demos

```bash
# FAL AI Avatar demo
python demo.py

# Replicate MultiTalk demo
python multitalk_demo.py
```

The demos provide user-friendly interfaces to:
- Choose between text-to-speech, audio-to-avatar, or multi-audio conversation modes
- Select images (local files, URLs, or sample images)
- Enter text for speech or select audio files
- Choose from 20 available voices (text mode only)
- Configure multiple audio files for conversations (multi-audio mode)
- Configure generation parameters
- Preview cost estimates before generation

## 📋 Available Voices

The FAL AI Avatar model supports 20 different voices:

**Male Voices**: Roger, Charlie, George, Callum, River, Liam, Will, Eric, Chris, Brian, Daniel, Bill

**Female Voices**: Aria, Sarah, Laura, Charlotte, Alice, Matilda, Jessica, Lily

## 🧪 Testing

### FREE Tests (No Cost)

Test your setup without generating videos:

```bash
# FAL AI environment and API validation
python test_setup.py

# Replicate MultiTalk validation
python tests/test_multitalk_integration.py
```

These scripts validate:
- Python environment and dependencies
- API key configurations (FAL AI and Replicate)
- Generator class functionality
- Output directory permissions
- Model integrations and compatibility

### PAID Tests (Costs Money)

⚠️ **WARNING**: These tests generate real videos and cost money (~$0.02-0.05 per video)

```bash
# Official FAL AI example test (exact documentation example)
python test_official_example.py

# Basic avatar generation test
python test_generation.py

# Quick test with minimal frames (cheaper)
python test_generation.py --quick

# Test specific voice
python test_generation.py --voice Bill

# Compare multiple voices (costs more)
python test_generation.py --compare

# Test audio-to-avatar generation
python test_generation.py --audio

# Test multi-audio conversation generation
python test_generation.py --multi

# Test custom scenarios
python test_generation.py --scenarios

# MultiTalk real example test (costs money)
python tests/test_real_multitalk_example.py

# MultiTalk dry-run test (free)
python tests/test_real_multitalk_example.py --dry-run

# Direct replicate.run() test (costs money)
python tests/direct_multitalk_test.py
```

## 💰 Cost Information

**Pricing**: ~$0.02-0.05 per avatar video
- Base cost: ~$0.03 per generation
- Frame count 81: Standard rate
- Frame count >81: 1.25x rate multiplier
- Turbo mode: No additional cost

**Cost Examples**:
- Single video (81 frames): ~$0.030
- Single video (136 frames): ~$0.038
- Voice comparison (3 voices, 136 frames): ~$0.114
- Custom scenarios (2 videos, 136 frames): ~$0.076

## 🎛️ API Reference

### FALAvatarGenerator Class

#### `__init__(api_key=None)`
Initialize the avatar generator.

**Parameters**:
- `api_key` (str, optional): FAL AI API key. Uses `FAL_KEY` environment variable if not provided.

#### `generate_avatar_video(**kwargs)`
Generate a talking avatar video.

**Parameters**:
- `image_url` (str): Image URL or local file path
- `text_input` (str): Text for the avatar to speak
- `voice` (str): Voice name (default: "Sarah")
- `prompt` (str): Generation prompt (default: natural speaking)
- `num_frames` (int): Frame count 81-129 (default: 136)
- `seed` (int, optional): Random seed for reproducibility
- `turbo` (bool): Enable turbo mode (default: True)
- `output_path` (str, optional): Local save path

**Returns**:
- Dictionary with video information and metadata

#### `generate_avatar_from_audio(**kwargs)`
Generate avatar video from custom audio file.

**Parameters**:
- `image_url` (str): Image URL or local file path
- `audio_url` (str): Audio URL or local file path
- `prompt` (str): Generation prompt (default: natural speaking)
- `num_frames` (int): Frame count 81-129 (default: 145)
- `seed` (int, optional): Random seed for reproducibility
- `turbo` (bool): Enable turbo mode (default: True)
- `output_path` (str, optional): Local save path

**Returns**:
- Dictionary with video information and metadata

#### `generate_multi_avatar_conversation(**kwargs)`
Generate multi-person conversation video from two audio files.

**Parameters**:
- `image_url` (str): Image URL or local file path
- `first_audio_url` (str): First person's audio URL or local file path
- `second_audio_url` (str): Second person's audio URL or local file path
- `prompt` (str): Generation prompt (default: natural conversation)
- `num_frames` (int): Frame count 81-129 (default: 181)
- `seed` (int, optional): Random seed for reproducibility
- `turbo` (bool): Enable turbo mode (default: True)
- `output_path` (str, optional): Local save path

**Returns**:
- Dictionary with video information and metadata

#### `generate_official_example(**kwargs)`
Generate avatar video using the exact official FAL AI example.

**Parameters**:
- `output_path` (str, optional): Local save path

**Returns**:
- Dictionary with video information and metadata

**Note**: This method uses the exact parameters from the official FAL AI documentation:
- Image: Official FAL AI example image
- Text: "Spend more time with people who make you feel alive, and less with things that drain your soul."
- Voice: "Bill"
- Prompt: Official podcast-style prompt
- Frames: 136, Seed: 42, Turbo: True

#### `get_available_voices()`
Get list of available voice options.

**Returns**:
- List of voice names

#### `test_connection()`
Test API connection without generating videos.

**Returns**:
- Boolean indicating connection status

## 🔧 Configuration Options

### Environment Variables

```env
# Required
FAL_KEY=your-api-key

# Optional defaults
DEFAULT_VOICE=Sarah
DEFAULT_FRAMES=136
DEFAULT_TURBO=true
OUTPUT_DIR=output
TEST_OUTPUT_DIR=test_output
```

### Generation Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `num_frames` | int | 81-129 | 136 | Video length in frames |
| `voice` | string | 20 options | "Sarah" | Voice personality |
| `turbo` | boolean | true/false | true | Fast generation mode |
| `seed` | int | any | random | Reproducibility seed |

### Frame Count Guidelines

- **81 frames**: Minimum, standard pricing
- **82-129 frames**: 1.25x pricing multiplier
- **136 frames**: Default, good balance of length and cost
- **129 frames**: Maximum, longest videos

## 🎬 Use Cases

### Professional Content
- Business presentations
- Corporate communications
- Training videos
- Product demonstrations

### Educational Content
- Online courses
- Tutorial videos
- Language learning
- Instructional content

### Creative Projects
- Character voices for stories
- Multilingual content
- Accessibility features
- Interactive experiences

## 📁 Project Structure

```
avatar/
├── fal_avatar_generator.py          # FAL AI avatar generator
├── replicate_multitalk_generator.py # Replicate MultiTalk generator
├── demo.py                          # FAL AI interactive demo
├── multitalk_demo.py               # MultiTalk interactive demo
├── test_setup.py                   # FREE environment tests
├── test_generation.py              # PAID generation tests
├── tests/
│   ├── test_generation.py          # FAL AI generation tests
│   ├── test_official_example.py    # FAL AI official example tests
│   ├── test_setup.py               # FAL AI setup tests
│   ├── test_multitalk_integration.py # MultiTalk integration tests
│   ├── test_real_multitalk_example.py # Real MultiTalk example with assets
│   └── direct_multitalk_test.py    # Direct replicate.run() test
├── requirements.txt                # Python dependencies
├── .env                           # Configuration file
├── README.md                      # This documentation
├── output/                        # Generated videos
└── test_output/                  # Test-generated videos
```

## 🛠️ Advanced Usage

### Custom Prompts

```python
# Professional presentation style
result = generator.generate_avatar_video(
    image_url="business_photo.jpg",
    text_input="Welcome to our quarterly review...",
    voice="Roger",
    prompt="A professional person in business attire presenting to an audience with confident and engaging expressions."
)

# Educational content style
result = generator.generate_avatar_video(
    image_url="teacher_photo.jpg",
    text_input="Today we'll learn about...",
    voice="Sarah",
    prompt="An educator explaining concepts with clear articulation and engaging facial expressions."
)
```

### Batch Processing

```python
voices = ["Sarah", "Roger", "Bill"]
text = "This is a voice comparison test."

for voice in voices:
    result = generator.generate_avatar_video(
        image_url="avatar.jpg",
        text_input=text,
        voice=voice,
        output_path=f"output/avatar_{voice.lower()}.mp4"
    )
```

### Error Handling

```python
try:
    result = generator.generate_avatar_video(
        image_url="image.jpg",
        text_input="Hello world!",
        voice="Sarah"
    )
    print("Success:", result['video']['url'])
except ValueError as e:
    print("Configuration error:", e)
except Exception as e:
    print("Generation error:", e)
```

## 🔍 Troubleshooting

### Common Issues

**"FAL_KEY environment variable not set"**
- Solution: Set your API key in `.env` file or environment variable

**"Invalid voice 'XYZ'"**
- Solution: Use `generator.get_available_voices()` to see valid options

**"num_frames must be between 81 and 129"**
- Solution: Adjust frame count to valid range

**"Failed to upload local image"**
- Solution: Check file path and permissions

### Performance Tips

1. **Use turbo mode** for faster generation (enabled by default)
2. **Minimize frame count** for cheaper/faster results
3. **Use remote images** to avoid upload time
4. **Batch similar requests** to optimize API usage

## 📊 Monitoring Usage

Track your API usage and costs:

```python
# Monitor generation results
result = generator.generate_avatar_video(...)

print(f"Generation time: {result['generation_time']:.2f}s")
print(f"File size: {result['video']['file_size'] / (1024*1024):.2f} MB")
print(f"Video URL: {result['video']['url']}")
```

## 🔗 Related Resources

- [FAL AI Documentation](https://fal.ai/models/fal-ai/ai-avatar/single-text)
- [FAL AI Dashboard](https://fal.ai/dashboard)
- [API Pricing](https://fal.ai/pricing)
- [Voice Samples](https://fal.ai/models/fal-ai/ai-avatar/single-text/playground)

## 🤝 Contributing

Contributions are welcome! Please:

1. Test changes with FREE tests first
2. Document any new features
3. Include cost estimates for new functionality
4. Follow the existing code style

## 📄 License

This project follows the same license as the parent repository.

---

**⚠️ Cost Reminder**: Always use FREE tests (`test_setup.py`) for development and validation. Only run PAID tests (`test_generation.py`) when you need to test actual video generation functionality. 