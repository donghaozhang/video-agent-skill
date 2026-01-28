# Phase 3: CLI Commands & Pipeline Support

**Created:** 2026-01-28
**Branch:** `feature/kimi-cli-integration`
**Status:** Pending
**Estimated Effort:** 3-4 hours
**Dependencies:** Phase 2 complete

---

## Objective

Add CLI commands for Kimi integration and enable Kimi agent steps in YAML pipelines.

---

## Subtasks

### 3.1 Add CLI Commands

**File to Modify:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

Add new commands:

```python
# Add imports at top
from .integrations.kimi import KimiIntegration, KimiClient


@cli.command()
@click.option("--prompt", "-p", required=True, help="Task description or question")
@click.option("--system", "-s", help="Optional system prompt")
@click.option("--code", "-c", help="Code to analyze (file path or inline)")
@click.option("--output", "-o", help="Output file path")
@click.option("--stream", is_flag=True, help="Stream response")
def kimi_chat(prompt: str, system: str, code: str, output: str, stream: bool):
    """
    Chat with Kimi AI assistant.

    Examples:

    \b
    # Simple chat
    aicp kimi-chat -p "Explain async/await in Python"

    \b
    # Analyze code file
    aicp kimi-chat -p "Find bugs" -c src/main.py

    \b
    # With custom system prompt
    aicp kimi-chat -p "Review this" -c code.py -s "You are a senior code reviewer"

    \b
    # Save response to file
    aicp kimi-chat -p "Generate tests for this code" -c utils.py -o tests.py
    """
    try:
        kimi = KimiIntegration()

        if not kimi.is_available():
            click.echo("Error: Kimi SDK not available or KIMI_API_KEY not set")
            click.echo("Install: pip install kimi-sdk")
            click.echo("Configure: export KIMI_API_KEY=your_key")
            return

        # Handle code input
        code_content = None
        if code:
            if os.path.isfile(code):
                with open(code, 'r') as f:
                    code_content = f.read()
                click.echo(f"Reading code from: {code}")
            else:
                code_content = code

        # Build request
        if code_content:
            result = kimi.analyze_code(
                code=code_content,
                question=prompt,
            )
        else:
            result = kimi.chat(
                message=prompt,
                system_prompt=system,
            )

        if result.success:
            if output:
                with open(output, 'w') as f:
                    f.write(result.content)
                click.echo(f"Response saved to: {output}")
            else:
                click.echo(result.content)
        else:
            click.echo(f"Error: {result.error}")

    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.option("--prompt", "-p", required=True, help="Describe the pipeline you want")
@click.option("--output", "-o", default="generated_pipeline.yaml", help="Output YAML file")
@click.option("--validate", is_flag=True, help="Validate generated pipeline")
@click.option("--estimate-cost", is_flag=True, help="Show cost estimate")
def generate_pipeline(prompt: str, output: str, validate: bool, estimate_cost: bool):
    """
    Generate a YAML pipeline from natural language description.

    Examples:

    \b
    # Generate simple image pipeline
    aicp generate-pipeline -p "Create an image of a sunset and upscale it"

    \b
    # Generate video pipeline with validation
    aicp generate-pipeline -p "Take a portrait photo and make it talk" --validate

    \b
    # With cost estimation
    aicp generate-pipeline -p "Create avatar from text" --estimate-cost -o avatar.yaml
    """
    try:
        from .integrations.kimi.pipeline_generator import PipelineGenerator

        generator = PipelineGenerator()

        if not generator.is_available():
            click.echo("Error: Kimi SDK not available")
            return

        click.echo(f"Generating pipeline for: {prompt}")
        click.echo("...")

        # Generate pipeline
        result = generator.generate_from_prompt(prompt)

        if not result.success:
            click.echo(f"Error: {result.error}")
            return

        pipeline_yaml = result.content

        # Validate if requested
        if validate:
            click.echo("\nValidating pipeline...")
            validation = generator.validate(pipeline_yaml)
            if validation.get("valid"):
                click.echo("✓ Pipeline is valid")
            else:
                click.echo("✗ Validation errors:")
                for error in validation.get("errors", []):
                    click.echo(f"  - {error}")

        # Estimate cost if requested
        if estimate_cost:
            click.echo("\nEstimating cost...")
            cost = generator.estimate_cost(pipeline_yaml)
            click.echo(f"Estimated total cost: ${cost.get('total', 0):.4f}")

        # Save to file
        with open(output, 'w') as f:
            f.write(pipeline_yaml)
        click.echo(f"\nPipeline saved to: {output}")

        # Show preview
        click.echo("\n--- Pipeline Preview ---")
        click.echo(pipeline_yaml[:500] + "..." if len(pipeline_yaml) > 500 else pipeline_yaml)

    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
def kimi_status():
    """
    Check Kimi integration status.

    Shows whether Kimi SDK is installed and configured.
    """
    click.echo("Kimi Integration Status")
    click.echo("=" * 40)

    # Check SDK
    try:
        import kimi_sdk
        version = getattr(kimi_sdk, "__version__", "unknown")
        click.echo(f"✓ kimi-sdk installed (v{version})")
    except ImportError:
        click.echo("✗ kimi-sdk not installed")
        click.echo("  Run: pip install kimi-sdk")
        return

    # Check API key
    api_key = os.getenv("KIMI_API_KEY")
    if api_key:
        masked = api_key[:8] + "..." + api_key[-4:]
        click.echo(f"✓ KIMI_API_KEY set ({masked})")
    else:
        click.echo("✗ KIMI_API_KEY not set")
        click.echo("  Add to .env: KIMI_API_KEY=your_key")

    # Check base URL
    base_url = os.getenv("KIMI_BASE_URL")
    if base_url:
        click.echo(f"✓ KIMI_BASE_URL: {base_url}")
    else:
        click.echo("○ KIMI_BASE_URL not set (using default)")

    # Test connection
    if api_key:
        click.echo("\nTesting connection...")
        try:
            kimi = KimiIntegration()
            result = kimi.chat("Say 'connection successful' in exactly those words.")
            if result.success:
                click.echo("✓ Connection successful")
            else:
                click.echo(f"✗ Connection failed: {result.error}")
        except Exception as e:
            click.echo(f"✗ Connection test error: {e}")
```

---

### 3.2 Create Pipeline Generator Module

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/integrations/kimi/pipeline_generator.py`

```python
"""
Pipeline generator using Kimi AI.

Converts natural language descriptions into YAML pipeline configurations.
"""

import yaml
from typing import Any, Dict, Optional
from dataclasses import dataclass

from .client import KimiIntegration, KimiResponse


@dataclass
class PipelineGeneratorResult:
    """Result from pipeline generation."""
    success: bool
    content: Optional[str] = None
    parsed: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PipelineGenerator:
    """
    Generate YAML pipelines from natural language using Kimi.
    """

    SYSTEM_PROMPT = """You are an AI Content Pipeline configuration expert.
Your task is to generate valid YAML pipeline configurations based on user descriptions.

Available step types and models:

TEXT_TO_IMAGE:
- flux_dev (highest quality, $0.003)
- flux_schnell (fastest, $0.001)
- imagen_4 (photorealistic)
- nano_banana_pro (fast, high quality)

IMAGE_TO_IMAGE:
- photon_flash (creative modifications)
- clarity_upscaler (resolution enhancement)
- nano_banana_pro_edit (fast editing)

IMAGE_TO_VIDEO:
- veo_3 (Google's latest, $0.50/video)
- veo_2 (previous gen, $0.25/video)
- hailuo (MiniMax, $0.20/video)
- kling (high quality, $0.15/video)

AVATAR:
- omnihuman_v1_5 (best quality, $0.16/sec)
- fabric_1_0 (lipsync, $0.08-0.15/sec)
- fabric_1_0_text (text-to-speech avatar)
- kling_ref_to_video (character consistency)

Pipeline YAML format:
```yaml
name: "Pipeline Name"
description: "What this pipeline does"

steps:
  - name: "step_name"
    type: "text_to_image"  # or image_to_image, image_to_video, avatar
    model: "model_name"
    params:
      prompt: "generation prompt"
      # other model-specific params
    output: "output_variable_name"

  - name: "next_step"
    type: "image_to_video"
    model: "veo_3"
    params:
      image_url: "{{step_name.output}}"  # Reference previous step output
      prompt: "video prompt"
    output: "video_output"
```

Rules:
1. Always include name, description, and steps
2. Each step needs: name, type, model, params, output
3. Use {{step_name.output}} to reference previous step outputs
4. Choose appropriate models for each task
5. Return ONLY valid YAML, no explanations
6. Add comments for complex configurations
"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize pipeline generator."""
        self._kimi = None
        self._api_key = api_key

    @property
    def kimi(self) -> KimiIntegration:
        """Lazy initialization of Kimi client."""
        if self._kimi is None:
            self._kimi = KimiIntegration(api_key=self._api_key)
        return self._kimi

    def is_available(self) -> bool:
        """Check if generator is available."""
        return self.kimi.is_available()

    def generate_from_prompt(
        self,
        prompt: str,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> PipelineGeneratorResult:
        """
        Generate pipeline YAML from natural language prompt.

        Args:
            prompt: Natural language description of desired pipeline
            constraints: Optional constraints (max_cost, preferred_models, etc.)

        Returns:
            PipelineGeneratorResult with YAML content
        """
        try:
            # Build user message
            user_message = f"Generate a YAML pipeline for: {prompt}"

            if constraints:
                if "max_cost" in constraints:
                    user_message += f"\nBudget constraint: max ${constraints['max_cost']}"
                if "preferred_models" in constraints:
                    user_message += f"\nPreferred models: {constraints['preferred_models']}"
                if "output_format" in constraints:
                    user_message += f"\nOutput format: {constraints['output_format']}"

            # Generate with Kimi
            response = self.kimi.chat(
                message=user_message,
                system_prompt=self.SYSTEM_PROMPT,
            )

            if not response.success:
                return PipelineGeneratorResult(
                    success=False,
                    error=response.error,
                )

            # Extract YAML from response
            yaml_content = self._extract_yaml(response.content)

            # Try to parse to validate
            try:
                parsed = yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                return PipelineGeneratorResult(
                    success=False,
                    error=f"Generated invalid YAML: {e}",
                    content=yaml_content,
                )

            return PipelineGeneratorResult(
                success=True,
                content=yaml_content,
                parsed=parsed,
            )

        except Exception as e:
            return PipelineGeneratorResult(
                success=False,
                error=str(e),
            )

    def _extract_yaml(self, content: str) -> str:
        """Extract YAML from response (may be in code blocks)."""
        # Check for code blocks
        if "```yaml" in content:
            start = content.find("```yaml") + 7
            end = content.find("```", start)
            if end > start:
                return content[start:end].strip()

        if "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end > start:
                return content[start:end].strip()

        # Return as-is if no code blocks
        return content.strip()

    def validate(self, yaml_content: str) -> Dict[str, Any]:
        """
        Validate pipeline YAML.

        Args:
            yaml_content: YAML string to validate

        Returns:
            Dict with 'valid', 'errors', 'warnings'
        """
        errors = []
        warnings = []

        try:
            config = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "errors": [f"YAML parse error: {e}"],
                "warnings": [],
            }

        # Check required fields
        if not config:
            errors.append("Empty configuration")
            return {"valid": False, "errors": errors, "warnings": warnings}

        if "name" not in config:
            errors.append("Missing 'name' field")

        if "steps" not in config:
            errors.append("Missing 'steps' field")
        elif not isinstance(config.get("steps"), list):
            errors.append("'steps' must be a list")
        elif len(config.get("steps", [])) == 0:
            warnings.append("Pipeline has no steps")
        else:
            # Validate each step
            for i, step in enumerate(config["steps"]):
                step_name = step.get("name", f"step_{i}")

                if "type" not in step:
                    errors.append(f"Step '{step_name}': missing 'type'")

                if "model" not in step:
                    warnings.append(f"Step '{step_name}': no model specified")

                if "output" not in step:
                    warnings.append(f"Step '{step_name}': no output defined")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def estimate_cost(self, yaml_content: str) -> Dict[str, Any]:
        """
        Estimate pipeline cost.

        Args:
            yaml_content: YAML string

        Returns:
            Dict with cost breakdown
        """
        # Cost estimates per model (simplified)
        COST_MAP = {
            "flux_dev": 0.003,
            "flux_schnell": 0.001,
            "imagen_4": 0.004,
            "nano_banana_pro": 0.002,
            "veo_3": 0.50,
            "veo_2": 0.25,
            "hailuo": 0.20,
            "kling": 0.15,
            "omnihuman_v1_5": 1.60,  # 10 sec at $0.16/sec
            "fabric_1_0": 1.50,
            "fabric_1_0_text": 1.50,
            "photon_flash": 0.02,
            "clarity_upscaler": 0.03,
        }

        try:
            config = yaml.safe_load(yaml_content)
            steps = config.get("steps", [])

            total = 0.0
            breakdown = []

            for step in steps:
                model = step.get("model", "unknown")
                cost = COST_MAP.get(model, 0.01)
                total += cost
                breakdown.append({
                    "step": step.get("name", "unnamed"),
                    "model": model,
                    "cost": cost,
                })

            return {
                "total": round(total, 4),
                "breakdown": breakdown,
                "currency": "USD",
            }

        except Exception as e:
            return {"total": 0, "error": str(e)}


    def improve_pipeline(
        self,
        yaml_content: str,
        feedback: str,
    ) -> PipelineGeneratorResult:
        """
        Improve existing pipeline based on feedback.

        Args:
            yaml_content: Current pipeline YAML
            feedback: What to improve

        Returns:
            PipelineGeneratorResult with improved YAML
        """
        message = f"""Improve this pipeline based on the feedback:

Current pipeline:
```yaml
{yaml_content}
```

Feedback: {feedback}

Return the improved YAML only."""

        response = self.kimi.chat(
            message=message,
            system_prompt=self.SYSTEM_PROMPT,
        )

        if not response.success:
            return PipelineGeneratorResult(success=False, error=response.error)

        yaml_content = self._extract_yaml(response.content)

        try:
            parsed = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return PipelineGeneratorResult(
                success=False,
                error=f"Invalid YAML: {e}",
                content=yaml_content,
            )

        return PipelineGeneratorResult(
            success=True,
            content=yaml_content,
            parsed=parsed,
        )
```

---

### 3.3 Add Pipeline Step Type for Kimi Agent

**File to Modify:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/executor.py`

Add handler for `kimi_agent` step type:

```python
# Add to step type handlers

async def _execute_kimi_agent_step(
    self,
    step: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Execute a Kimi agent step.

    Step params:
        task: str - Task description for the agent
        system_prompt: Optional[str] - Custom system prompt
        tools: Optional[List[str]] - Tools to enable
        max_turns: Optional[int] - Max conversation turns
    """
    from ..integrations.kimi import KimiIntegration
    from ..integrations.kimi.tools import create_kimi_toolset

    params = step.get("params", {})
    task = params.get("task", "")

    if not task:
        raise ValueError("Kimi agent step requires 'task' parameter")

    kimi = KimiIntegration()

    if not kimi.is_available():
        raise RuntimeError("Kimi SDK not available")

    # Resolve any template variables in task
    task = self._resolve_template(task, context)

    # Get optional parameters
    system_prompt = params.get("system_prompt")
    enable_tools = params.get("tools", [])
    max_turns = params.get("max_turns", 5)

    # Create toolset if tools requested
    toolset = None
    if enable_tools:
        toolset = create_kimi_toolset()

    # Execute agent
    if toolset:
        result = kimi.client.step(
            messages=[{"role": "user", "content": task}],
            tools=toolset,
            system_prompt=system_prompt,
        )
    else:
        result = kimi.chat(
            message=task,
            system_prompt=system_prompt,
        )

    if not result.success:
        raise RuntimeError(f"Kimi agent failed: {result.error}")

    return {
        "output": result.content,
        "model": "kimi",
        "success": True,
    }
```

**Add to step type registry:**

```python
STEP_TYPE_HANDLERS = {
    "text_to_image": _execute_text_to_image_step,
    "image_to_image": _execute_image_to_image_step,
    "image_to_video": _execute_image_to_video_step,
    "avatar": _execute_avatar_step,
    "kimi_agent": _execute_kimi_agent_step,  # NEW
    # ... other handlers
}
```

---

### 3.4 Example YAML Pipelines with Kimi

**File:** `input/pipelines/examples/kimi_pipeline_generation.yaml`

```yaml
name: "AI-Assisted Pipeline Creation"
description: "Use Kimi to analyze and improve pipeline configurations"

steps:
  - name: "analyze_requirements"
    type: "kimi_agent"
    params:
      task: "Analyze this content creation requirement and suggest the best approach: {{user_requirement}}"
      system_prompt: "You are an AI content pipeline expert. Suggest specific models and configurations."
    output: "analysis"

  - name: "generate_content"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{analysis.suggested_prompt}}"
    output: "generated_image"
```

**File:** `input/pipelines/examples/kimi_code_review.yaml`

```yaml
name: "Code Review Pipeline"
description: "Use Kimi to review code and suggest improvements"

steps:
  - name: "code_review"
    type: "kimi_agent"
    params:
      task: |
        Review this code for:
        1. Bugs and potential issues
        2. Performance improvements
        3. Code style and best practices

        Code:
        {{code_input}}
      system_prompt: "You are a senior code reviewer. Be thorough but constructive."
      max_turns: 3
    output: "review_result"
```

---

## Commit Checkpoint

```bash
git add .
git commit -m "feat: Add Kimi CLI commands and pipeline step support"
git push origin feature/kimi-cli-integration
```

---

## Verification Checklist

- [ ] `kimi-chat` command works
- [ ] `generate-pipeline` command works
- [ ] `kimi-status` command shows correct info
- [ ] Pipeline generator creates valid YAML
- [ ] `kimi_agent` step type executes correctly
- [ ] Example pipelines validate

---

## CLI Usage Examples

```bash
# Check Kimi status
aicp kimi-status

# Simple chat
aicp kimi-chat -p "What are best practices for async Python?"

# Analyze code file
aicp kimi-chat -p "Review this code for bugs" -c src/pipeline/executor.py

# Generate pipeline from description
aicp generate-pipeline -p "Create a talking avatar from a portrait photo and text script"

# Generate with validation and cost estimate
aicp generate-pipeline \
    -p "Generate an image, upscale it 2x, then create a 5-second video" \
    --validate \
    --estimate-cost \
    -o my_pipeline.yaml
```
