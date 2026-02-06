# CLI Redesign: Unix-Style Architecture for LLM Agent Reliability (Partially Complete)

## Current State Assessment

**Short answer: The pipeline works, but it's fragile for LLM agents.**

The AI Content Pipeline supports 53 models across 11 categories with YAML chaining, parallel execution, and cost estimation. However, the model registration pattern creates significant maintenance burden and error risk.

---

## Problem 1: Adding One Model Requires 60-90 Edits Across 18+ Files

When Kling O3 was added, the commit touched **18 files with +2,873 lines**. Breakdown:

| Layer | Files | Edits per model |
|---|---|---|
| `config/constants.py` | 4 files (one per provider) | 10-12 dicts each |
| `models/__init__.py` | 4 files | import + `__all__` |
| `models/[model].py` | 1-4 new files | class implementation |
| `generator.py` | 4 files | import + registry dict |
| `cli.py` | 2 files | `choices=[]` x3-4 + `if/elif` x2 |
| `ai_content_pipeline/constants.py` | 1 file | 4 more dicts |

An LLM agent will **inevitably miss one** of these locations, causing silent breakage or runtime errors. Example: duration options were `["5", "10", "12"]` when the FAL API actually supports `3-15`.

---

## Problem 2: Hardcoded `if/elif` Chains in CLI

The CLI has model-specific logic scattered everywhere:

```python
# cli.py lines 29-64 — this grows with EVERY new model
if args.model == "kling_2_6_pro":
    kwargs["duration"] = int(args.duration)    # int!
elif args.model in ["kling_3_standard", "kling_3_pro"]:
    kwargs["duration"] = args.duration          # string!
elif args.model == "kling_o3_pro_t2v":
    kwargs["duration"] = args.duration          # string!
elif args.model in ["sora_2", "sora_2_pro"]:
    kwargs["duration"] = int(args.duration)    # int again!
```

**Duration is `int` for some models and `str` for others.** This is a bug waiting to happen. Each model also appears in `choices=[]` **3-4 times** in the same file.

---

## Problem 3: Two CLI Frameworks Mixed Together

| Component | Framework | Style |
|---|---|---|
| Unified CLI (`ai-content-pipeline`) | Click | `@click.group()` decorators |
| Provider CLIs (`fal-text-to-video`) | argparse | `add_argument()` + subparsers |

An LLM agent has to understand two different patterns to work with the codebase.

---

## Problem 4: No Single Source of Truth

The same model metadata lives in **3+ independent places**:

- `fal_text_to_video/config/constants.py` - pricing, durations, endpoints
- `fal_image_to_video/config/constants.py` - same model, different copy
- `ai_content_pipeline/config/constants.py` - yet another copy

If pricing changes, all 3 must be updated independently.

---

## Proposed Solution: Unix-Style CLI Redesign

The Unix philosophy: **"each tool does one thing well"** + **composable interfaces** + **convention over configuration**.

### Recommendation 1: Single Model Registry (DRY) ✅ DONE

Instead of 60+ locations, one file:

```python
# registry.py - THE single source of truth
MODELS = {
    "kling_3_standard": {
        "endpoint": "fal-ai/kling-video/v3/standard/text-to-video",
        "name": "Kling Video v3 Standard",
        "categories": ["text_to_video", "image_to_video"],
        "pricing": {"no_audio": 0.168, "audio": 0.252},
        "duration": list(range(3, 16)),
        "aspects": ["16:9", "9:16", "1:1"],
        "defaults": {"duration": 5, "aspect_ratio": "16:9"},
    }
}
```

Adding a new model = **1 dict entry + 1 model class file**. Down from 60-90 edits.

### Recommendation 2: Dynamic CLI (No Hardcoded Choices) ✅ DONE

Unix tools don't hardcode options - they discover them:

```python
# Instead of choices=["kling_2_6_pro", "kling_3_standard", ...]
from .registry import MODELS
parser.add_argument("--model", choices=MODELS.keys())
```

```python
# Instead of if/elif chains for parameter handling:
def cmd_generate(args):
    model_config = MODELS[args.model]
    kwargs = build_kwargs_from_config(args, model_config)
    generator.generate_video(prompt=args.prompt, model=args.model, **kwargs)
```

This eliminates **all** the `if/elif` chains and duplicate `choices=[]` lists.

### Recommendation 3: Consistent Type Handling ✅ DONE

Unix convention - everything is a string until the consumer decides:

```python
# Let the model class handle type conversion, not the CLI
# CLI just passes through:
kwargs["duration"] = args.duration  # always string from argparse

# Model class converts as needed:
class KlingModel:
    def validate(self, **kwargs):
        self.duration = str(kwargs.get("duration", self.defaults["duration"]))
```

### Recommendation 4: One CLI Framework

Pick one (Click is better for complex CLIs) and use it everywhere. Remove the argparse provider CLIs or make them thin wrappers around the unified interface.

### Recommendation 5: Pipe-Friendly Output

Unix tools output structured data for composition:

```bash
# Current: emoji-heavy human output only
ai-content-pipeline list-models  # prints fancy tables

# Better: add --json flag for LLM/script consumption
ai-content-pipeline list-models --json
ai-content-pipeline generate --model kling_3_standard --json | jq '.video_url'
```

---

## Impact Summary

| Aspect | Current | With Unix Redesign |
|---|---|---|
| Files to edit for new model | 18+ files, 60-90 locations | 2 files (registry + model class) |
| Risk of missed edit | **High** | **Near zero** |
| LLM agent reliability | Fragile | Robust |
| CLI consistency | Mixed (Click + argparse) | Single framework |
| Type safety | `int` vs `str` confusion | Consistent handling |
| Scriptability | Human output only | `--json` for piping |
| Model discovery | Works via `list-models` | Same, plus `--json` |

---

## What Works Well (Keep These)

- **Generator pattern with MODEL_CLASSES dict** - Good model dispatch
- **StepFactory registration** - Pipeline step dispatch is clean
- **Parallel execution** - Threading-based parallelization
- **YAML configuration** - Flexible pipeline definitions
- **Cost estimation** - Integrated cost tracking across models
- **Unified CLI entry point** - Single `ai-content-pipeline` / `aicp` command

---

## Implementation Priority

1. ✅ **High**: Single model registry (`registry.py`) - biggest ROI — *Implemented in PR #19*
2. ✅ **High**: Dynamic CLI choices from registry - eliminates duplication — *Implemented in PR #19*
3. ✅ **Medium**: Remove `if/elif` chains - use registry defaults — *Implemented in PR #19*
4. **Medium**: Add `--json` output flag - enables LLM/script consumption
5. **Low**: Unify CLI framework (Click everywhere) - polish

---

## References

- FAL API docs: https://fal.ai/models
- Current model count: 53 models across 11 categories
- Recent commit adding Kling O3: `e2727ea` (18 files, +2,873 lines)
- Duration fix example: Kling v3 Standard `["5", "10", "12"]` -> `range(3, 16)`
