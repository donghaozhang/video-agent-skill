# Installation Guide

Complete guide to installing and configuring the AI Content Generation Suite.

## System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB for package, additional space for generated content
- **Network**: Internet connection for API calls

### Recommended Setup
- Python 3.11 or 3.12
- 16GB RAM for parallel processing
- SSD storage for faster I/O

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
# Install the latest stable version
pip install video-ai-studio

# Verify installation
ai-content-pipeline --version
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/donghaozhang/video-agent-skill.git
cd video-agent-skill

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e .
```

### Method 3: Install with Optional Dependencies

```bash
# Install with all optional dependencies
pip install video-ai-studio[all]

# Install with specific extras
pip install video-ai-studio[dev]      # Development tools
pip install video-ai-studio[test]     # Testing tools
```

## Virtual Environment Setup

### Linux/macOS

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install package
pip install video-ai-studio

# Deactivate when done
deactivate
```

### Windows

```powershell
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install package
pip install video-ai-studio

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n ai-content python=3.11
conda activate ai-content

# Install package
pip install video-ai-studio
```

## API Keys Configuration

### Required API Keys

At minimum, you need one API key to use the package:

| Provider | Key Name | Required For | Get Key At |
|----------|----------|--------------|------------|
| FAL AI | `FAL_KEY` | Most models | [fal.ai/dashboard](https://fal.ai/dashboard) |
| Google | `GEMINI_API_KEY` | Image analysis | [makersuite.google.com](https://makersuite.google.com) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Text-to-speech | [elevenlabs.io/app/settings](https://elevenlabs.io/app/settings) |
| OpenRouter | `OPENROUTER_API_KEY` | Alternative models | [openrouter.ai/keys](https://openrouter.ai/keys) |

### Setting Up Environment Variables

#### Option 1: .env File (Recommended)

Create a `.env` file in your project root:

```env
# FAL AI - Required for most functionality
FAL_KEY=your_fal_api_key_here

# Google Gemini - For image analysis
GEMINI_API_KEY=your_gemini_api_key_here

# ElevenLabs - For text-to-speech
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# OpenRouter - For alternative models
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Google Cloud - For Veo video generation
PROJECT_ID=your-gcp-project-id
OUTPUT_BUCKET_PATH=gs://your-bucket/output/
```

#### Option 2: System Environment Variables

**Linux/macOS:**
```bash
export FAL_KEY="your_fal_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

**Windows:**
```powershell
setx FAL_KEY "your_fal_api_key"
setx GEMINI_API_KEY "your_gemini_api_key"
```

### Google Cloud Setup (For Veo Models)

If using Google Veo video generation:

```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
```

## Verifying Installation

### Basic Verification

```bash
# Check CLI is available
ai-content-pipeline --help

# List available models
ai-content-pipeline list-models

# Check version
ai-content-pipeline --version
```

### API Connection Test

```bash
# Test with mock mode (no API calls)
ai-content-pipeline generate-image --text "test" --mock

# Test actual API connection (uses credits)
ai-content-pipeline generate-image --text "test image" --model flux_schnell
```

### Python Import Test

```python
# Test Python imports
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

# Initialize manager
manager = AIPipelineManager()
print("Installation successful!")
```

## Dependencies

The package automatically installs these core dependencies:

```text
click>=8.0.0          # CLI framework
pydantic>=2.0.0       # Data validation
python-dotenv>=1.0.0  # Environment management
httpx>=0.24.0         # HTTP client
rich>=13.0.0          # Console output
PyYAML>=6.0           # YAML configuration
fal-client>=0.4.0     # FAL AI SDK
google-cloud-aiplatform>=1.38.0  # Google Vertex AI
elevenlabs>=0.2.0     # ElevenLabs TTS
```

## Upgrading

### Upgrade to Latest Version

```bash
pip install --upgrade video-ai-studio
```

### Upgrade from Source

```bash
cd video-agent-skill
git pull origin main
pip install -e .
```

## Uninstalling

```bash
pip uninstall video-ai-studio
```

## Troubleshooting Installation

### Python Version Issues

```bash
# Check Python version
python --version

# Use specific Python version
python3.11 -m pip install video-ai-studio
```

### Permission Errors

```bash
# Use user installation
pip install --user video-ai-studio

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install video-ai-studio
```

### SSL Certificate Errors

```bash
# Upgrade certifi
pip install --upgrade certifi

# Or use trusted host
pip install --trusted-host pypi.org video-ai-studio
```

### Dependency Conflicts

```bash
# Create fresh environment
python -m venv fresh_env
source fresh_env/bin/activate
pip install video-ai-studio
```

## Platform-Specific Notes

### Windows
- Use PowerShell or Command Prompt
- Ensure Python is in PATH
- Consider using Windows Terminal for better experience

### macOS
- Install Python via Homebrew: `brew install python@3.11`
- May need Xcode command line tools: `xcode-select --install`

### Linux
- Install Python via package manager
- May need `python3-venv` package: `sudo apt install python3-venv`

---

[Back to Documentation Index](../../index.md) | [Next: Quick Start](quick-start.md)
