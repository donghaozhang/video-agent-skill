"""
Core pipeline CLI commands.

Commands: list-models, setup, generate-image, create-video, run-chain, create-examples.
"""

import json
import sys
from pathlib import Path

import click

from ..exit_codes import error_exit, EXIT_INVALID_ARGS, EXIT_MISSING_CONFIG
from ..interactive import confirm
from ..output import CLIOutput, read_input


def _check_save_json_deprecation(save_json, output):
    """Emit deprecation warning if --save-json is used."""
    if save_json:
        output.warning(
            "--save-json is deprecated and will be removed in a future release. "
            "Use '--json' to emit structured output to stdout, then redirect: "
            "aicp <command> --json > result.json"
        )


@click.command("list-models")
@click.pass_context
def list_models_cmd(ctx):
    """List all available models."""
    from ...pipeline.manager import AIPipelineManager

    output = ctx.obj["output"]
    output.info("\n🎨 AI Content Pipeline Supported Models")
    output.info("=" * 50)

    manager = AIPipelineManager(quiet=True)
    available_models = manager.get_available_models()

    if output.json_mode:
        output.table(
            [{"category": k, "models": v} for k, v in available_models.items()],
            command="list-models",
        )
        return

    for step_type, models in available_models.items():
        output.info(f"\n📦 {step_type.replace('_', '-').title()}")

        if models:
            for model in models:
                if step_type == "text_to_image":
                    info = manager.text_to_image.get_model_info(model)
                    output.info(f"   • {model}")
                    if info:
                        output.info(f"     Name: {info.get('name', 'N/A')}")
                        output.info(f"     Provider: {info.get('provider', 'N/A')}")
                        output.info(f"     Best for: {info.get('best_for', 'N/A')}")
                        output.info(f"     Cost: {info.get('cost_per_image', 'N/A')}")
                else:
                    output.info(f"   • {model}")
        else:
            output.info("   No models available (integration pending)")


@click.command("setup")
@click.option("--output-dir", default=None, help="Directory to create .env file (default: current directory)")
@click.pass_context
def setup_cmd(ctx, output_dir):
    """Create .env file with API key templates."""
    output = ctx.obj["output"]
    env_path = Path(output_dir) / ".env" if output_dir else Path(".env")
    env_example_path = Path(__file__).parent.parent.parent.parent.parent.parent / ".env.example"

    # Check if .env.example exists in the package
    if not env_example_path.exists():
        template_content = """# AI Content Pipeline - Environment Configuration
# Add your API keys below

# Required for most functionality
FAL_KEY=your_fal_api_key_here

# Optional - add as needed
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Get API keys from:
# FAL AI: https://fal.ai/dashboard
# Google Gemini: https://makersuite.google.com/app/apikey
# OpenRouter: https://openrouter.ai/keys
# ElevenLabs: https://elevenlabs.io/app/settings
"""
    else:
        with open(env_example_path, 'r') as f:
            template_content = f.read()

    if env_path.exists():
        if not confirm(f".env file already exists at {env_path}. Overwrite?"):
            output.info("Setup cancelled.")
            return

    try:
        with open(env_path, 'w') as f:
            f.write(template_content)
        output.info(f"Created .env file at {env_path}")
        output.info("Please edit the file and add your API keys:")
        output.info(f"   nano {env_path}")
        output.info("\nGet your API keys from:")
        output.info("   FAL AI: https://fal.ai/dashboard")
        output.info("   Google Gemini: https://makersuite.google.com/app/apikey")
        output.info("   OpenRouter: https://openrouter.ai/keys")
        output.info("   ElevenLabs: https://elevenlabs.io/app/settings")
    except Exception as e:
        output.error(f"Error creating .env file: {e}")


@click.command("generate-image")
@click.option("--text", required=True, help="Text prompt for image generation")
@click.option("--model", default="auto", show_default=True, help="Model to use")
@click.option("--aspect-ratio", default="16:9", show_default=True,
              help="Aspect ratio (auto, 21:9, 16:9, 3:2, 4:3, 5:4, 1:1, 4:5, 3:4, 2:3, 9:16)")
@click.option("--resolution", default="1K", show_default=True,
              help="Resolution for supported models (1K, 2K, 4K). Note: 4K costs double")
@click.option("--input", "input_file", default=None,
              help="Read prompt from file or stdin (use - for stdin)")
@click.option("--output-dir", default=None, help="Output directory")
@click.option("--save-json", default=None, help="Save result as JSON (deprecated, use --json)")
@click.pass_context
def generate_image_cmd(ctx, text, model, aspect_ratio, resolution, input_file, output_dir, save_json):
    """Generate image from text."""
    from ...pipeline.manager import AIPipelineManager

    output = ctx.obj["output"]
    base_dir = ctx.obj["base_dir"]
    _check_save_json_deprecation(save_json, output)
    quiet = ctx.obj["json_mode"] or ctx.obj["quiet"]

    try:
        manager = AIPipelineManager(base_dir, quiet=quiet)

        # Resolve input text
        if input_file:
            text = read_input(input_file, fallback=text)

        gen_params = {
            "prompt": text,
            "model": model,
            "aspect_ratio": aspect_ratio,
            "output_dir": output_dir or "output",
        }
        if resolution:
            gen_params["resolution"] = resolution

        result = manager.text_to_image.generate(**gen_params)

        result_dict = {
            "success": result.success,
            "model": result.model_used,
            "output_path": result.output_path,
            "cost": result.cost_estimate,
            "processing_time": result.processing_time,
            "error": result.error,
        }

        if output.json_mode:
            output.result(result_dict, command="generate-image")
        elif result.success:
            output.info("\nImage generation successful!")
            output.info(f"Model: {result.model_used}")
            if result.output_path:
                output.info(f"Output: {result.output_path}")
            output.info(f"Cost: ${result.cost_estimate:.3f}")
            output.info(f"Processing time: {result.processing_time:.1f} seconds")
        else:
            output.error(f"Image generation failed: {result.error}")

        if save_json:
            json_path = manager.output_dir / save_json
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            output.info(f"\nResult saved to: {json_path}")

    except Exception as e:
        error_exit(e, debug=ctx.obj["debug"])


@click.command("create-video")
@click.option("--text", required=True, help="Text prompt for content creation")
@click.option("--image-model", default="auto", show_default=True, help="Model for text-to-image")
@click.option("--video-model", default="auto", show_default=True, help="Model for image-to-video")
@click.option("--input", "input_file", default=None,
              help="Read prompt from file or stdin (use - for stdin)")
@click.option("--output-dir", default=None, help="Output directory")
@click.option("--save-json", default=None, help="Save result as JSON (deprecated, use --json)")
@click.pass_context
def create_video_cmd(ctx, text, image_model, video_model, input_file, output_dir, save_json):
    """Create video from text (text -> image -> video)."""
    from ...pipeline.manager import AIPipelineManager

    output = ctx.obj["output"]
    base_dir = ctx.obj["base_dir"]
    _check_save_json_deprecation(save_json, output)
    quiet = ctx.obj["json_mode"] or ctx.obj["quiet"]

    try:
        manager = AIPipelineManager(base_dir, quiet=quiet)

        if input_file:
            text = read_input(input_file, fallback=text)

        result = manager.quick_create_video(
            text=text,
            image_model=image_model,
            video_model=video_model,
            output_dir=output_dir,
        )

        result_dict = {
            "success": result.success,
            "steps_completed": result.steps_completed,
            "total_steps": result.total_steps,
            "total_cost": result.total_cost,
            "total_time": result.total_time,
            "outputs": result.outputs,
            "error": result.error,
        }

        if output.json_mode:
            output.result(result_dict, command="create-video")
        elif result.success:
            output.info("\nVideo creation successful!")
            output.info(f"Steps completed: {result.steps_completed}/{result.total_steps}")
            output.info(f"Total cost: ${result.total_cost:.3f}")
            output.info(f"Total time: {result.total_time:.1f} seconds")
            if result.outputs:
                output.info("\nOutputs:")
                for step_name, step_out in result.outputs.items():
                    if step_out.get("path"):
                        output.info(f"   {step_name}: {step_out['path']}")
        else:
            output.error(f"Video creation failed: {result.error}")

        if save_json:
            json_path = manager.output_dir / save_json
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            output.info(f"\nFull result saved to: {json_path}")

    except Exception as e:
        error_exit(e, debug=ctx.obj["debug"])


@click.command("run-chain")
@click.option("--config", required=True, help="Path to chain configuration (YAML/JSON)")
@click.option("--input-text", default=None, help="Input text for the chain")
@click.option("--prompt-file", default=None, help="Path to text file containing the prompt")
@click.option("--input", "input_file", default=None,
              help="Read input data from file or stdin (use - for stdin)")
@click.option("--no-confirm", is_flag=True, default=False,
              help="Skip confirmation prompt (auto-set in CI)")
@click.option("--stream", is_flag=True, default=False,
              help="Emit JSONL progress events to stderr during execution")
@click.option("--save-json", default=None, help="Save results as JSON (deprecated, use --json)")
@click.pass_context
def run_chain_cmd(ctx, config, input_text, prompt_file, input_file, no_confirm, stream, save_json):
    """Run custom chain from configuration."""
    from ...pipeline.manager import AIPipelineManager
    from ..stream import StreamEmitter, NullEmitter

    output = ctx.obj["output"]
    base_dir = ctx.obj["base_dir"]
    _check_save_json_deprecation(save_json, output)
    quiet = ctx.obj["json_mode"] or ctx.obj["quiet"]

    try:
        manager = AIPipelineManager(base_dir, quiet=quiet)
        chain = manager.create_chain_from_config(config)
        output.info(f"Loaded chain: {chain.name}")

        # Determine input data
        input_data = input_text
        initial_input_type = chain.get_initial_input_type()

        if input_file:
            input_data = read_input(input_file, fallback=input_data)

        if not input_data and prompt_file:
            try:
                with open(prompt_file, 'r') as f:
                    input_data = f.read().strip()
                    output.info(f"Using prompt from file ({prompt_file}): {input_data}")
            except FileNotFoundError:
                error_exit(FileNotFoundError(f"Prompt file not found: {prompt_file}"))
            except Exception as e:
                error_exit(e, debug=ctx.obj["debug"])

        if not input_data:
            _resolve_chain_input = {
                "text": ("prompt", "No input text provided. Use --input, --input-text, --prompt-file, or add 'prompt' field to config."),
                "video": ("input_video", "No input video provided. Use --input-text or add 'input_video' field to config."),
                "image": ("input_image", "No input image provided. Use --input-text or add 'input_image' field to config."),
                "any": ("prompt", "No input provided for parallel group. Add 'prompt' field to config or use --input-text."),
            }
            if initial_input_type in _resolve_chain_input:
                config_key, err_msg = _resolve_chain_input[initial_input_type]
                config_input = chain.config.get(config_key)
                if config_input:
                    input_data = config_input
                    output.info(f"Using {config_key} from config: {input_data}")
                else:
                    error_exit(ValueError(err_msg))
            else:
                error_exit(ValueError(f"Unknown input type: {initial_input_type}"))
        elif input_text:
            output.info(f"Using input text: {input_data}")

        # Validate chain
        errors = chain.validate()
        if errors:
            error_exit(ValueError(f"Chain validation failed: {'; '.join(errors)}"))

        # Show cost estimate
        cost_info = manager.estimate_chain_cost(chain)
        output.info(f"Estimated cost: ${cost_info['total_cost']:.3f}")

        if not no_confirm:
            if not confirm("\nProceed with execution?", default=True):
                output.info("Execution cancelled.")
                sys.exit(0)

        # Build emitter for --stream mode
        emitter = StreamEmitter(enabled=True) if stream else NullEmitter()
        emitter.pipeline_start(
            name=chain.name,
            total_steps=len(chain.get_enabled_steps()),
            config=config,
        )

        result = manager.execute_chain(chain, input_data, stream_emitter=emitter)

        result_dict = {
            "success": result.success,
            "steps_completed": result.steps_completed,
            "total_steps": result.total_steps,
            "total_cost": result.total_cost,
            "total_time": result.total_time,
            "outputs": result.outputs,
            "error": result.error,
        }

        if stream:
            emitter.pipeline_complete(result_dict)
        elif output.json_mode:
            output.result(result_dict, command="run-chain")
        elif result.success:
            output.info("\nChain execution successful!")
            output.info(f"Steps completed: {result.steps_completed}/{result.total_steps}")
            output.info(f"Total cost: ${result.total_cost:.3f}")
            output.info(f"Total time: {result.total_time:.1f} seconds")
        else:
            output.error(f"Chain execution failed: {result.error}")

        if save_json:
            json_path = manager.output_dir / save_json
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            output.info(f"\nResults saved to: {json_path}")

    except Exception as e:
        error_exit(e, debug=ctx.obj["debug"])


@click.command("create-examples")
@click.option("--output-dir", default=None, help="Directory for example configs")
@click.pass_context
def create_examples_cmd(ctx, output_dir):
    """Create example configuration files."""
    from ...pipeline.manager import AIPipelineManager

    output = ctx.obj["output"]
    base_dir = ctx.obj["base_dir"]
    quiet = ctx.obj["json_mode"] or ctx.obj["quiet"]

    try:
        manager = AIPipelineManager(base_dir, quiet=quiet)
        manager.create_example_configs(output_dir)
        output.info("Example configurations created successfully!")
    except Exception as e:
        error_exit(e, debug=ctx.obj["debug"])


def register_pipeline_commands(group):
    """Register all pipeline commands with the CLI group."""
    group.add_command(list_models_cmd)
    group.add_command(setup_cmd)
    group.add_command(generate_image_cmd)
    group.add_command(create_video_cmd)
    group.add_command(run_chain_cmd)
    group.add_command(create_examples_cmd)
