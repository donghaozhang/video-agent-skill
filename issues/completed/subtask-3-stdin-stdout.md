# Subtask 3: Stdin/Stdout First

**Status**: COMPLETED (core helper + tests; wiring into commands is follow-up work)
**PR**: [#20](https://github.com/donghaozhang/video-agent-skill/pull/20)
**Parent**: [plan-unix-style-migration.md](plan-unix-style-migration.md)
**Depends on**: Subtask 2 (JSON output)
**Estimated Time**: 45 minutes

### Implementation Summary
- Added `read_input()` to `cli/output.py` — reads from stdin (`-`), file path, or fallback
- Raises `ValueError` for TTY stdin (maps to exit code 2 via exit_codes module)
- Raises `FileNotFoundError` for missing files (maps to exit code 3)
- 8 tests in `tests/test_stdin_input.py` — all passing
- **Remaining work**: Add `--input` flag to `create-video`, `generate-image`, `run-chain` commands

---

## Objective

Support `--input -` for reading prompts/configs from stdin. Support `--output -` for writing raw result payloads to stdout. Enable Unix pipe workflows.

---

## Step-by-Step Implementation

### Step 1: Add stdin helper to `cli/output.py`

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/cli/output.py`

Add function:

```python
def read_input(input_arg: Optional[str], fallback: Optional[str] = None) -> Optional[str]:
    """Read input from a file path, stdin ('-'), or use fallback.

    Args:
        input_arg: File path, '-' for stdin, or None.
        fallback: Value to return if input_arg is None.

    Returns:
        The input text, or None if no input available.
    """
    if input_arg == '-':
        if sys.stdin.isatty():
            print("error: --input - requires piped input (stdin is a terminal)",
                  file=sys.stderr)
            sys.exit(2)
        return sys.stdin.read().strip()
    elif input_arg:
        path = Path(input_arg)
        if not path.exists():
            print(f"error: input file not found: {input_arg}", file=sys.stderr)
            sys.exit(3)
        return path.read_text().strip()
    return fallback
```

### Step 2: Modify `create-video` command

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

In parser setup for `create-video`, add `--input` argument:

```python
create_video_parser.add_argument('--input', '-i', default=None,
    help='Input file or - for stdin (overrides --text)')
```

In `create_video()` handler:

```python
from .cli.output import read_input

def create_video(args, manager, output):
    text = read_input(getattr(args, 'input', None), fallback=args.text)
    if not text:
        output.error("No prompt provided. Use --text or --input -")
        sys.exit(2)
    # ... rest of execution with text ...
```

### Step 3: Modify `generate-image` command

Same pattern as `create-video`:

```python
generate_image_parser.add_argument('--input', '-i', default=None,
    help='Input file or - for stdin (overrides --text)')
```

### Step 4: Modify `run-chain` to support config from stdin

```python
# In run_chain()
config_source = args.config
if config_source == '-':
    import tempfile
    stdin_content = sys.stdin.read()
    # Write to temp file since YAML loader expects a file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(stdin_content)
        config_source = f.name
```

### Step 5: Add `--output -` support

For commands that produce files, `--output -` writes the file path to stdout instead of saving to default location:

```python
# In create_video()
if getattr(args, 'output', None) == '-':
    # Print just the output path to stdout for piping
    print(str(result.output_path))
else:
    output.human(f"📁 Output: {result.output_path}")
```

### Step 6: Update provider CLIs

**File**: `packages/providers/fal/text-to-video/fal_text_to_video/cli.py`

```python
@cli.command("generate")
@click.option('--input', '-i', 'input_source', default=None,
    help='Read prompt from file or - for stdin')
def generate(prompt, input_source, **kwargs):
    if input_source == '-':
        prompt = click.get_text_stream('stdin').read().strip()
    elif input_source:
        prompt = Path(input_source).read_text().strip()
    # ...
```

### Step 7: Write tests

**File**: Add to `tests/test_cli_json_output.py` (or create separate file)

```python
class TestStdinInput:
    def test_create_video_reads_from_stdin(self):
        result = subprocess.run(
            ['ai-content-pipeline', 'create-video', '--input', '-', '--json'],
            input="cinematic drone shot over mountains",
            capture_output=True, text=True, timeout=30
        )
        # Should not fail with "no prompt" error
        assert "No prompt provided" not in result.stderr

    def test_stdin_empty_returns_error(self):
        result = subprocess.run(
            ['ai-content-pipeline', 'create-video', '--input', '-', '--json'],
            input="",
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode != 0

    def test_run_chain_reads_config_from_stdin(self):
        yaml_config = "name: test\nsteps: []"
        result = subprocess.run(
            ['ai-content-pipeline', 'run-chain', '--config', '-', '--json'],
            input=yaml_config,
            capture_output=True, text=True, timeout=30
        )
        # Should attempt to parse the YAML (may fail on empty steps, but shouldn't fail on "no config")
        assert "No config" not in result.stderr
```

---

## Usage Examples

```bash
# Read prompt from stdin
echo "cinematic drone shot over snowy mountains" | \
  aicp create-video --input - --model kling_3_standard --json

# Pipe YAML config
cat pipeline.yaml | aicp run-chain --config - --json

# Chain commands: generate image, pipe path to video
aicp generate-image --text "sunset" --output - | \
  xargs -I {} aicp create-video --input-image {} --json

# Read prompt from file
aicp create-video --input prompt.txt --model veo3

# Combined with jq
echo "abstract art" | \
  aicp generate-image --input - --json | jq -r '.data.output_path'
```

---

## Verification

```bash
# Test stdin reading
echo "test prompt" | ai-content-pipeline create-video --input - --json 2>&1 | head -5

# Test config from stdin
cat input/pipelines/example.yaml | ai-content-pipeline run-chain --config - --json

# Run tests
python -m pytest tests/test_cli_json_output.py -v -k stdin
```
