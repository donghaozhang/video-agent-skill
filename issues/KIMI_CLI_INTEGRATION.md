# Kimi CLI Integration Guide

This document outlines how to integrate [MoonshotAI/kimi-cli](https://github.com/MoonshotAI/kimi-cli) as a submodule into the AI Content Pipeline repository.

## Overview

**Kimi Code CLI** is an AI agent operating in terminal environments that can:
- Read and edit code
- Execute shell commands
- Search and fetch web pages
- Autonomously plan and adjust actions during execution

**License:** Apache-2.0
**Python Version:** Requires Python 3.12+
**Latest Release:** v1.2 (January 2026)

---

## Repository Structure

```
kimi-cli/
├── .agents/skills/          # Agent skill definitions
├── docs/                    # Documentation
├── examples/                # Usage examples
├── klips/                   # Quick reference clips
├── packages/                # Package dependencies
├── scripts/                 # Utility scripts
├── sdks/kimi-sdk/          # SDK for programmatic access
├── src/kimi_cli/           # Main CLI source code
│   ├── acp/                # Agent Client Protocol
│   ├── agents/             # Agent implementations
│   ├── auth/               # Authentication logic
│   ├── cli/                # CLI components
│   ├── deps/               # Dependency management
│   ├── prompts/            # Prompt templates
│   ├── skill/              # Skill definitions
│   ├── skills/             # Skill implementations
│   ├── soul/               # Core behavioral logic
│   ├── tools/              # Tool integrations
│   ├── ui/                 # User interface utilities
│   ├── utils/              # Helper utilities
│   ├── wire/               # Dependency injection
│   ├── app.py              # Main application entry
│   ├── config.py           # Configuration management
│   ├── llm.py              # Language model integration
│   └── session.py          # Session management
├── tests/                   # Unit tests
├── tests_ai/               # AI-specific tests
├── tests_e2e/              # End-to-end tests
├── pyproject.toml          # Project configuration
└── Makefile                # Build automation
```

---

## Integration Options

### Option 1: Git Submodule (Recommended for Development)

Add kimi-cli as a submodule to track upstream changes:

```bash
# Add as submodule in packages/external/
mkdir -p packages/external
git submodule add https://github.com/MoonshotAI/kimi-cli.git packages/external/kimi-cli

# Initialize and update
git submodule update --init --recursive

# Commit the submodule
git add .gitmodules packages/external/kimi-cli
git commit -m "feat: Add kimi-cli as submodule"
git push origin main
```

**Update submodule to latest:**
```bash
cd packages/external/kimi-cli
git fetch origin
git checkout main
git pull origin main
cd ../../..
git add packages/external/kimi-cli
git commit -m "chore: Update kimi-cli submodule"
```

### Option 2: Install kimi-sdk as Dependency

For programmatic access only, install the SDK:

```bash
# Using pip
pip install kimi-sdk

# Using uv (recommended by kimi-cli)
uv add kimi-sdk
```

### Option 3: Clone and Ignore (Quick Exploration)

For initial exploration without tracking:

```bash
# Clone into ignored directory
git clone https://github.com/MoonshotAI/kimi-cli.git _external/kimi-cli

# Add to .gitignore
echo "_external/" >> .gitignore
```

---

## Kimi SDK Usage

The SDK provides programmatic access to Kimi's capabilities:

### Core Components

| Class | Purpose |
|-------|---------|
| `Kimi` | Main client for API communication |
| `Message` | Chat messages with role and content |
| `SimpleToolset` | Container for callable tools |
| `StepResult` | Tool execution results |

### Basic Example

```python
import asyncio
from kimi_sdk import Kimi, Message

async def main():
    # Initialize client (uses KIMI_API_KEY env var)
    client = Kimi()

    # Create conversation
    messages = [
        Message(role="user", content="Analyze this code structure")
    ]

    # Generate response
    response = await client.generate(
        messages=messages,
        system_prompt="You are a code analysis assistant."
    )

    print(response)

asyncio.run(main())
```

### Tool Integration Example

```python
from kimi_sdk import Kimi, SimpleToolset, CallableTool2, ToolOk
from pydantic import BaseModel

class AnalyzeVideoParams(BaseModel):
    video_path: str
    analysis_type: str = "timeline"

class AnalyzeVideoTool(CallableTool2):
    name = "analyze_video"
    description = "Analyze a video file"
    parameters = AnalyzeVideoParams

    async def call(self, params: AnalyzeVideoParams):
        # Integration with AI Content Pipeline
        result = await analyze_video_with_pipeline(
            params.video_path,
            params.analysis_type
        )
        return ToolOk(result)

# Register tools
toolset = SimpleToolset([AnalyzeVideoTool()])

# Use in agent step
result = await client.step(messages, toolset=toolset)
```

---

## Configuration Requirements

### Environment Variables

```bash
# Required for Kimi CLI/SDK
KIMI_API_KEY=your_kimi_api_key
KIMI_BASE_URL=https://api.moonshot.cn  # Optional, defaults to official API

# Existing AI Content Pipeline variables
FAL_KEY=your_fal_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### Authentication

First-time setup requires login:
```bash
# If using CLI directly
kimi
# Then run /login inside the CLI
```

---

## Integration Architecture

### Proposed Directory Structure

```
ai-content-pipeline/
├── packages/
│   ├── core/
│   │   └── ai_content_pipeline/
│   ├── providers/
│   │   └── ...
│   ├── services/
│   │   └── ...
│   └── external/                    # NEW
│       └── kimi-cli/                # Submodule
│           └── sdks/kimi-sdk/       # SDK we'll use
├── ai_content_pipeline/
│   └── integrations/
│       └── kimi_integration.py      # Integration wrapper
```

### Integration Wrapper Concept

```python
# ai_content_pipeline/integrations/kimi_integration.py

from typing import Optional
import asyncio

class KimiIntegration:
    """
    Wrapper for Kimi SDK integration with AI Content Pipeline.
    """

    def __init__(self, api_key: Optional[str] = None):
        from kimi_sdk import Kimi
        self.client = Kimi(api_key=api_key)

    async def analyze_with_agent(
        self,
        task: str,
        context: Optional[dict] = None
    ) -> str:
        """
        Use Kimi agent to analyze/process content.

        Args:
            task: The task description
            context: Optional context dict

        Returns:
            Agent response
        """
        from kimi_sdk import Message

        messages = [Message(role="user", content=task)]
        response = await self.client.generate(messages=messages)
        return response

    async def code_generation(
        self,
        prompt: str,
        language: str = "python"
    ) -> str:
        """
        Generate code using Kimi.
        """
        system = f"Generate {language} code. Return only code, no explanations."
        messages = [{"role": "user", "content": prompt}]
        return await self.client.generate(
            messages=messages,
            system_prompt=system
        )
```

---

## Key Dependencies

Kimi CLI has specific version requirements:

| Package | Version | Notes |
|---------|---------|-------|
| Python | >=3.12 | Required |
| aiohttp | 3.13.3 | Async HTTP |
| pydantic | 2.12.5 | Data validation |
| typer | 0.21.1 | CLI framework |
| rich | 14.2.0 | Terminal UI |
| httpx | 0.28.1 | HTTP client |
| jinja2 | 3.1.6 | Templating |

**Potential Conflicts:** Check against existing `requirements.txt` for version mismatches.

---

## Use Cases for AI Content Pipeline

### 1. Intelligent Pipeline Generation
Use Kimi to generate YAML pipeline configurations from natural language:
```
"Create a pipeline that takes an image, upscales it, and generates a 5-second video"
```

### 2. Code Analysis & Refactoring
Analyze existing pipeline code for improvements or bug fixes.

### 3. Documentation Generation
Auto-generate documentation for new models or features.

### 4. Interactive Debugging
Use Kimi's shell mode for debugging pipeline issues.

### 5. Multi-Agent Workflows
Combine Kimi agent with existing AI models for complex tasks.

---

## Implementation Steps

### Phase 1: Setup (Week 1)
1. [ ] Add kimi-cli as submodule
2. [ ] Update `.gitmodules`
3. [ ] Add kimi-sdk to `requirements.txt`
4. [ ] Create integration wrapper module

### Phase 2: Core Integration (Week 2)
1. [ ] Implement `KimiIntegration` class
2. [ ] Add configuration for Kimi API
3. [ ] Write unit tests
4. [ ] Document new commands

### Phase 3: Feature Implementation (Week 3+)
1. [ ] Pipeline generation from natural language
2. [ ] Code analysis tools
3. [ ] Interactive debugging mode

---

## Commands Reference

### Kimi CLI Commands

```bash
# Start interactive session
kimi

# ACP mode (for IDE integration)
kimi acp

# MCP server management
kimi mcp add <server>
kimi mcp list
kimi mcp remove <server>

# With MCP config file
kimi --mcp-config-file config.json
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl-X` | Toggle shell mode |
| `Ctrl-C` | Cancel current operation |
| `/login` | Authenticate |
| `/help` | Show help |

---

## Resources

- **Repository:** https://github.com/MoonshotAI/kimi-cli
- **SDK Docs:** https://github.com/MoonshotAI/kimi-cli/tree/main/sdks/kimi-sdk
- **Examples:** https://github.com/MoonshotAI/kimi-cli/tree/main/examples
- **License:** Apache-2.0

---

## Notes

- Kimi CLI requires Python 3.12+, while AI Content Pipeline may use older versions
- Consider using a separate virtual environment for Kimi integration if version conflicts arise
- The SDK is async-native, ensure proper async handling in integration code
- Authentication tokens are stored locally after `/login`
