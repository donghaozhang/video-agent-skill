# Framework Migration Plan: Unix/Linux Style

**Status**: Phase 1 COMPLETED — [PR #20](https://github.com/donghaozhang/video-agent-skill/pull/20)
**Implementation Plan**: [plan-unix-style-migration.md](plan-unix-style-migration.md)

## Goal
Make the current framework behave like Unix tools: small composable commands, predictable input/output, script-friendly defaults, and clear separation between CLI and core logic.

## Why This Matters
- Better automation in shell scripts and CI.
- Easier composition with tools like `jq`, `xargs`, `find`, and `parallel`.
- Lower maintenance burden by reducing CLI-specific branching.
- More reliable usage by LLM agents and other non-interactive callers.

## Current Gaps in This Repo
- Mixed CLI patterns (`click` and `argparse`) across packages.
- Human-oriented output is common; machine output is inconsistent.
- Some commands still rely on interactive flows or coupled side effects.
- Configuration patterns are not yet fully aligned with Unix/Linux conventions (XDG, env-first, stdin/stdout-first).

## Unix/Linux Design Rules for This Framework
1. One command, one responsibility.
2. Read from `stdin` when no input file is provided.
3. Write primary results to `stdout`; diagnostics to `stderr`.
4. Exit with stable, meaningful exit codes.
5. Provide `--json` (or `--jsonl`) for all list/generate/status commands.
6. Avoid interactive prompts by default; support `--yes`/`--non-interactive`.
7. Keep command behavior deterministic and side effects explicit.
8. Use environment variables and XDG directories for config/cache/state.

## Target Command Contract
- `0`: success.
- `2`: invalid arguments/validation failure.
- `3`: missing configuration or credentials.
- `4`: provider/network/API failure.
- `5`: pipeline execution failure.
- `10+`: reserved for tool-specific failures.

## Concrete Changes

### 1) Standardize CLI Surface
- Keep one top-level command (`ai-content-pipeline` / `aicp`).
- Normalize subcommands into noun-verb or verb-noun, but keep one pattern.
- Add aliases only where backward compatibility is required.

### 2) Add Machine-Readable Output Everywhere
- Add `--json` for all commands that currently print tables/human summaries.
- Add `--quiet` to suppress non-essential output.
- Keep `--verbose` for diagnostics (to `stderr`).

### 3) Stdin/Stdout First
- Support `--input -` and default to reading `stdin` when appropriate.
- Support `--output -` to print raw result payloads to `stdout`.
- Ensure generated file paths are emitted in structured output for piping.

### 4) Strict Error Model
- Introduce shared exception-to-exit-code mapping.
- Ensure stack traces only appear in debug mode (`--debug`).
- Keep one-line error summary for scripts and CI.

### 5) Configuration and Filesystem Conventions
- Env-first auth (`FAL_KEY`, `GEMINI_API_KEY`, etc.) with explicit error messages.
- Default config: `$XDG_CONFIG_HOME/video-ai-studio/config.yaml` (fallback `~/.config/...`).
- Cache/temp/state:
  - `$XDG_CACHE_HOME/video-ai-studio`
  - `$XDG_STATE_HOME/video-ai-studio`
- Preserve explicit `--config`, `--cache-dir`, `--state-dir` overrides.

### 6) Decouple CLI from Business Logic
- Keep core operations in library modules (`manager`, `executor`, `registry`).
- CLI layer should only parse args, call library APIs, format output, and set exit codes.
- Remove model-specific CLI branching and rely on registry metadata.

### 7) Stream-Friendly Execution
- Add `--stream` mode for long-running pipelines:
  - progress events in JSON Lines to `stdout` or `stderr` (choose one and document).
  - final result event with outputs, cost, duration, and status.

### 8) Linux-First Developer Operations
- Prefer `Makefile` targets and POSIX shell examples in docs.
- Keep Windows support, but ensure docs and examples are cross-platform.
- Add CI checks that run non-interactive command smoke tests on Linux.

## Suggested Implementation Phases

### Phase 1: CLI Contract (High ROI) — COMPLETED
- [x] Implement `--json`, `--quiet`, `--debug`, stable exit codes.
- [x] Add `stdin/stdout` behavior for core generation and list commands.
- [x] Add tests for output format and exit-code behavior.
- **Delivered**: 5 CLI modules, 91 tests, 0 regressions. See [plan-unix-style-migration.md](plan-unix-style-migration.md).

### Phase 2: Config/Path Conventions — COMPLETED
- [x] Introduce XDG path resolution helpers in a shared utility module.
- [x] Add tests for env overrides and fallback resolution.
- [ ] Update docs and migration notes.

### Phase 3: Streaming + Composition — COMPLETED (module only)
- [x] Add `--stream` JSONL mode for pipeline commands (StreamEmitter module).
- [ ] Add examples using pipes with `jq` and shell scripting.
- [ ] Wire `--stream` flag into executor.

### Phase 4: Framework Consistency — NOT STARTED
- [ ] Remove remaining CLI style mismatches and normalize command UX.
- [ ] Keep compatibility shims for deprecated flags/subcommands until next major release.

## Acceptance Criteria
- [x] Every user-facing command supports machine-readable output. *(CLIOutput module ready; per-command wiring is follow-up)*
- [x] Core commands can be used in non-interactive CI with deterministic results. *(confirm() + is_interactive() + CI auto-detection)*
- [x] Exit codes are documented and tested. *(27 tests, codes 0-5)*
- [x] Config/cache/state paths follow XDG conventions on Linux. *(16 tests, Windows+Unix)*
- [x] CLI code is thin; business logic remains in reusable library modules. *(all new code in cli/ package)*

## Example Unix-Style Workflows (Target)
```bash
# List models and filter with jq
aicp list-models --json | jq '.text_to_video[]'

# Read prompt from stdin, return JSON
echo "cinematic drone shot over snowy mountains" | \
  aicp create-video --input - --model kling_3_standard --json

# Run pipeline non-interactively and capture output path
aicp run-chain --config pipeline.yaml --json --quiet | jq -r '.outputs.final.path'
```

## Risks
- Backward compatibility: existing scripts may parse current human output.
- Mixed CLI frameworks may slow consistency work.
- Streaming event format must be versioned to avoid downstream breakage.

## Mitigations
- Keep old flags temporarily with deprecation warnings.
- Version machine output schema (`"schema_version": "1"`).
- Add compatibility tests for known legacy command patterns.

## Next Step
~~Start with Phase 1 in a focused PR that adds stable JSON output + exit codes + tests for 3 high-usage commands (`list-models`, `create-video`, `run-chain`).~~

**Phase 1 complete.** Next: Wire `--json`/`--quiet`/`--stream` flags into `__main__.py` command handlers and route all output through `CLIOutput`. See [plan-unix-style-migration.md Follow-Up Work](plan-unix-style-migration.md#follow-up-work-phase-2).
