# Phase 4: Natural Language Pipeline Generation

**Created:** 2026-01-28
**Branch:** `feature/kimi-cli-integration`
**Status:** Pending
**Estimated Effort:** 4-5 hours
**Dependencies:** Phase 3 complete

---

## Objective

Enable advanced natural language to pipeline conversion with:
1. Multi-turn refinement
2. Template-based generation
3. Cost optimization
4. Model selection recommendations

---

## Subtasks

### 4.1 Enhanced Pipeline Generator

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/integrations/kimi/advanced_generator.py`

```python
"""
Advanced pipeline generator with multi-turn refinement and optimization.
"""

import yaml
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .client import KimiIntegration, KimiResponse
from .pipeline_generator import PipelineGenerator, PipelineGeneratorResult


class OptimizationGoal(Enum):
    """Pipeline optimization goals."""
    QUALITY = "quality"
    SPEED = "speed"
    COST = "cost"
    BALANCED = "balanced"


@dataclass
class ConversationTurn:
    """Single turn in pipeline generation conversation."""
    user_message: str
    assistant_response: str
    pipeline_yaml: Optional[str] = None


@dataclass
class GenerationSession:
    """Multi-turn pipeline generation session."""
    session_id: str
    initial_prompt: str
    turns: List[ConversationTurn] = field(default_factory=list)
    current_pipeline: Optional[str] = None
    optimization_goal: OptimizationGoal = OptimizationGoal.BALANCED


class AdvancedPipelineGenerator:
    """
    Advanced pipeline generator with conversation history and optimization.
    """

    MODEL_RECOMMENDATIONS = {
        OptimizationGoal.QUALITY: {
            "text_to_image": "flux_dev",
            "image_to_video": "veo_3",
            "avatar": "omnihuman_v1_5",
            "upscale": "clarity_upscaler",
        },
        OptimizationGoal.SPEED: {
            "text_to_image": "flux_schnell",
            "image_to_video": "hailuo",
            "avatar": "fabric_1_0_fast",
            "upscale": "photon_flash",
        },
        OptimizationGoal.COST: {
            "text_to_image": "flux_schnell",
            "image_to_video": "kling",
            "avatar": "fabric_1_0",
            "upscale": "photon_flash",
        },
        OptimizationGoal.BALANCED: {
            "text_to_image": "flux_dev",
            "image_to_video": "hailuo",
            "avatar": "fabric_1_0",
            "upscale": "clarity_upscaler",
        },
    }

    PIPELINE_TEMPLATES = {
        "image_generation": """
name: "Image Generation Pipeline"
description: "{description}"

steps:
  - name: "generate_image"
    type: "text_to_image"
    model: "{model}"
    params:
      prompt: "{prompt}"
      width: {width}
      height: {height}
    output: "generated_image"
""",
        "image_to_video": """
name: "Image to Video Pipeline"
description: "{description}"

steps:
  - name: "create_video"
    type: "image_to_video"
    model: "{model}"
    params:
      image_url: "{image_url}"
      prompt: "{prompt}"
      duration: {duration}
    output: "video_output"
""",
        "text_to_video": """
name: "Text to Video Pipeline"
description: "{description}"

steps:
  - name: "generate_image"
    type: "text_to_image"
    model: "{image_model}"
    params:
      prompt: "{image_prompt}"
    output: "base_image"

  - name: "create_video"
    type: "image_to_video"
    model: "{video_model}"
    params:
      image_url: "{{{{generate_image.output}}}}"
      prompt: "{video_prompt}"
    output: "final_video"
""",
        "avatar_from_text": """
name: "Text-to-Avatar Pipeline"
description: "{description}"

steps:
  - name: "create_avatar"
    type: "avatar"
    model: "fabric_1_0_text"
    params:
      image_url: "{image_url}"
      text: "{text}"
      resolution: "{resolution}"
    output: "avatar_video"
""",
        "full_production": """
name: "Full Production Pipeline"
description: "{description}"

steps:
  - name: "generate_portrait"
    type: "text_to_image"
    model: "{image_model}"
    params:
      prompt: "{portrait_prompt}"
      width: 1024
      height: 1024
    output: "portrait"

  - name: "create_avatar"
    type: "avatar"
    model: "{avatar_model}"
    params:
      image_url: "{{{{generate_portrait.output}}}}"
      text: "{script}"
      resolution: "720p"
    output: "avatar_video"

  - name: "upscale_video"
    type: "video_processing"
    model: "topaz"
    params:
      video_url: "{{{{create_avatar.output}}}}"
      scale: 2
    output: "final_video"
""",
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize advanced generator."""
        self.base_generator = PipelineGenerator(api_key=api_key)
        self.sessions: Dict[str, GenerationSession] = {}

    def is_available(self) -> bool:
        """Check availability."""
        return self.base_generator.is_available()

    def start_session(
        self,
        prompt: str,
        optimization_goal: OptimizationGoal = OptimizationGoal.BALANCED,
    ) -> Tuple[str, PipelineGeneratorResult]:
        """
        Start a new pipeline generation session.

        Args:
            prompt: Initial description
            optimization_goal: Optimization priority

        Returns:
            Tuple of (session_id, initial_result)
        """
        import uuid
        session_id = str(uuid.uuid4())[:8]

        # Analyze prompt to determine best template
        template_name, params = self._analyze_prompt(prompt, optimization_goal)

        # Generate initial pipeline
        if template_name:
            # Use template
            pipeline_yaml = self._apply_template(template_name, params)
            result = PipelineGeneratorResult(
                success=True,
                content=pipeline_yaml,
                parsed=yaml.safe_load(pipeline_yaml),
            )
        else:
            # Use AI generation
            result = self.base_generator.generate_from_prompt(
                prompt,
                constraints={"optimization": optimization_goal.value},
            )

        # Create session
        session = GenerationSession(
            session_id=session_id,
            initial_prompt=prompt,
            optimization_goal=optimization_goal,
            current_pipeline=result.content if result.success else None,
        )

        if result.success:
            session.turns.append(ConversationTurn(
                user_message=prompt,
                assistant_response="Generated initial pipeline",
                pipeline_yaml=result.content,
            ))

        self.sessions[session_id] = session
        return session_id, result

    def refine_session(
        self,
        session_id: str,
        feedback: str,
    ) -> PipelineGeneratorResult:
        """
        Refine pipeline based on feedback.

        Args:
            session_id: Active session ID
            feedback: User feedback/refinement request

        Returns:
            PipelineGeneratorResult with refined pipeline
        """
        if session_id not in self.sessions:
            return PipelineGeneratorResult(
                success=False,
                error=f"Session {session_id} not found",
            )

        session = self.sessions[session_id]

        if not session.current_pipeline:
            return PipelineGeneratorResult(
                success=False,
                error="No current pipeline to refine",
            )

        # Refine using base generator
        result = self.base_generator.improve_pipeline(
            session.current_pipeline,
            feedback,
        )

        if result.success:
            session.current_pipeline = result.content
            session.turns.append(ConversationTurn(
                user_message=feedback,
                assistant_response="Refined pipeline based on feedback",
                pipeline_yaml=result.content,
            ))

        return result

    def _analyze_prompt(
        self,
        prompt: str,
        goal: OptimizationGoal,
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Analyze prompt to determine best template and parameters.

        Returns:
            Tuple of (template_name or None, parameters dict)
        """
        prompt_lower = prompt.lower()
        params = {}
        template = None

        # Get recommended models for goal
        models = self.MODEL_RECOMMENDATIONS[goal]

        # Detect pipeline type from keywords
        if any(word in prompt_lower for word in ["avatar", "talking", "speaking", "lipsync"]):
            if "text" in prompt_lower or "script" in prompt_lower:
                template = "avatar_from_text"
                params = {
                    "description": prompt,
                    "image_url": "{{input_image}}",
                    "text": "{{input_text}}",
                    "resolution": "720p",
                }
            elif "portrait" in prompt_lower or "generate" in prompt_lower:
                template = "full_production"
                params = {
                    "description": prompt,
                    "image_model": models["text_to_image"],
                    "avatar_model": models["avatar"],
                    "portrait_prompt": "Professional portrait, neutral background",
                    "script": "{{input_script}}",
                }

        elif any(word in prompt_lower for word in ["video", "animate", "motion"]):
            if "image" in prompt_lower or "picture" in prompt_lower:
                template = "image_to_video"
                params = {
                    "description": prompt,
                    "model": models["image_to_video"],
                    "image_url": "{{input_image}}",
                    "prompt": "Subtle motion, high quality",
                    "duration": 5,
                }
            else:
                template = "text_to_video"
                params = {
                    "description": prompt,
                    "image_model": models["text_to_image"],
                    "video_model": models["image_to_video"],
                    "image_prompt": "{{input_prompt}}",
                    "video_prompt": "Cinematic motion",
                }

        elif any(word in prompt_lower for word in ["image", "picture", "photo", "generate"]):
            template = "image_generation"
            params = {
                "description": prompt,
                "model": models["text_to_image"],
                "prompt": "{{input_prompt}}",
                "width": 1024,
                "height": 1024,
            }

        return template, params

    def _apply_template(
        self,
        template_name: str,
        params: Dict[str, Any],
    ) -> str:
        """Apply parameters to template."""
        template = self.PIPELINE_TEMPLATES.get(template_name, "")
        return template.format(**params)

    def get_session(self, session_id: str) -> Optional[GenerationSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def list_templates(self) -> List[str]:
        """List available pipeline templates."""
        return list(self.PIPELINE_TEMPLATES.keys())

    def generate_from_template(
        self,
        template_name: str,
        params: Dict[str, Any],
    ) -> PipelineGeneratorResult:
        """
        Generate pipeline from a specific template.

        Args:
            template_name: Template to use
            params: Parameters for template

        Returns:
            PipelineGeneratorResult
        """
        if template_name not in self.PIPELINE_TEMPLATES:
            return PipelineGeneratorResult(
                success=False,
                error=f"Unknown template: {template_name}. Available: {self.list_templates()}",
            )

        try:
            yaml_content = self._apply_template(template_name, params)
            parsed = yaml.safe_load(yaml_content)

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

    def optimize_pipeline(
        self,
        yaml_content: str,
        goal: OptimizationGoal,
    ) -> PipelineGeneratorResult:
        """
        Optimize existing pipeline for a specific goal.

        Args:
            yaml_content: Current pipeline
            goal: Optimization goal

        Returns:
            PipelineGeneratorResult with optimized pipeline
        """
        models = self.MODEL_RECOMMENDATIONS[goal]

        try:
            config = yaml.safe_load(yaml_content)

            # Replace models based on goal
            for step in config.get("steps", []):
                step_type = step.get("type", "")

                if step_type == "text_to_image" and "text_to_image" in models:
                    step["model"] = models["text_to_image"]
                elif step_type == "image_to_video" and "image_to_video" in models:
                    step["model"] = models["image_to_video"]
                elif step_type == "avatar" and "avatar" in models:
                    step["model"] = models["avatar"]

            optimized_yaml = yaml.dump(config, default_flow_style=False)

            return PipelineGeneratorResult(
                success=True,
                content=optimized_yaml,
                parsed=config,
            )

        except Exception as e:
            return PipelineGeneratorResult(
                success=False,
                error=str(e),
            )
```

---

### 4.2 Add Interactive CLI Mode

**File to Modify:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

Add interactive pipeline builder:

```python
@cli.command()
@click.option("--goal", type=click.Choice(["quality", "speed", "cost", "balanced"]),
              default="balanced", help="Optimization goal")
def pipeline_builder(goal: str):
    """
    Interactive pipeline builder using Kimi AI.

    Starts an interactive session where you can describe what you want,
    refine the generated pipeline, and save when satisfied.

    Example:
        aicp pipeline-builder --goal quality
    """
    from .integrations.kimi.advanced_generator import (
        AdvancedPipelineGenerator,
        OptimizationGoal,
    )

    generator = AdvancedPipelineGenerator()

    if not generator.is_available():
        click.echo("Error: Kimi SDK not available")
        return

    click.echo("=" * 60)
    click.echo("AI Pipeline Builder (Interactive Mode)")
    click.echo(f"Optimization goal: {goal}")
    click.echo("=" * 60)
    click.echo("\nDescribe the pipeline you want to create.")
    click.echo("Type 'quit' to exit, 'save' to save current pipeline.\n")

    # Get initial prompt
    prompt = click.prompt("Your request")

    if prompt.lower() == "quit":
        return

    # Start session
    optimization = OptimizationGoal(goal)
    session_id, result = generator.start_session(prompt, optimization)

    if not result.success:
        click.echo(f"Error: {result.error}")
        return

    click.echo("\n--- Generated Pipeline ---")
    click.echo(result.content)
    click.echo("-" * 40)

    # Refinement loop
    while True:
        click.echo("\nOptions:")
        click.echo("  - Type feedback to refine the pipeline")
        click.echo("  - 'save <filename>' to save")
        click.echo("  - 'cost' to estimate cost")
        click.echo("  - 'validate' to check for errors")
        click.echo("  - 'quit' to exit")

        user_input = click.prompt("\nYour input")

        if user_input.lower() == "quit":
            break

        elif user_input.lower().startswith("save"):
            parts = user_input.split(maxsplit=1)
            filename = parts[1] if len(parts) > 1 else "generated_pipeline.yaml"
            if not filename.endswith(".yaml"):
                filename += ".yaml"

            session = generator.get_session(session_id)
            if session and session.current_pipeline:
                with open(filename, "w") as f:
                    f.write(session.current_pipeline)
                click.echo(f"Saved to: {filename}")
            continue

        elif user_input.lower() == "cost":
            session = generator.get_session(session_id)
            if session and session.current_pipeline:
                cost = generator.base_generator.estimate_cost(session.current_pipeline)
                click.echo(f"Estimated cost: ${cost.get('total', 0):.4f}")
            continue

        elif user_input.lower() == "validate":
            session = generator.get_session(session_id)
            if session and session.current_pipeline:
                validation = generator.base_generator.validate(session.current_pipeline)
                if validation.get("valid"):
                    click.echo("✓ Pipeline is valid")
                else:
                    click.echo("✗ Errors found:")
                    for err in validation.get("errors", []):
                        click.echo(f"  - {err}")
            continue

        else:
            # Refine based on feedback
            result = generator.refine_session(session_id, user_input)

            if result.success:
                click.echo("\n--- Refined Pipeline ---")
                click.echo(result.content)
                click.echo("-" * 40)
            else:
                click.echo(f"Error: {result.error}")

    click.echo("\nGoodbye!")
```

---

### 4.3 Add Template Listing Command

```python
@cli.command()
@click.option("--detailed", "-d", is_flag=True, help="Show template contents")
def list_templates(detailed: bool):
    """
    List available pipeline templates.

    Templates provide quick starting points for common use cases.
    """
    from .integrations.kimi.advanced_generator import AdvancedPipelineGenerator

    generator = AdvancedPipelineGenerator()
    templates = generator.list_templates()

    click.echo("Available Pipeline Templates")
    click.echo("=" * 40)

    for template in templates:
        click.echo(f"\n• {template}")
        if detailed:
            content = generator.PIPELINE_TEMPLATES.get(template, "")
            click.echo(content[:300] + "..." if len(content) > 300 else content)

    click.echo(f"\nTotal: {len(templates)} templates")
    click.echo("\nUse with: aicp generate-pipeline --template <name>")
```

---

## Commit Checkpoint

```bash
git add .
git commit -m "feat: Add advanced pipeline generation with templates and interactive mode"
git push origin feature/kimi-cli-integration
```

---

## Verification Checklist

- [ ] Advanced generator works with templates
- [ ] Session-based refinement functional
- [ ] Interactive builder mode works
- [ ] Cost optimization produces valid pipelines
- [ ] Template listing command works

---

## Usage Examples

```bash
# Interactive builder
aicp pipeline-builder --goal quality

# List templates
aicp list-templates --detailed

# Generate from template (to be added)
aicp generate-pipeline --template "text_to_video" \
    --param image_prompt="A beautiful sunset" \
    --param video_prompt="Gentle motion"
```
