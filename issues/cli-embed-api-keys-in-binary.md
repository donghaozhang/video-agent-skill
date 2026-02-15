# CLI: Embed API Keys into Binary via `set-key` / `get-key` Commands

**Branch:** `feat/cli-embed-fal-key-in-binary`
**Estimated Time:** ~30 minutes (4 subtasks)
**Priority:** High — required for standalone binary distribution

---

## Problem

When users download the `aicp` binary (built via PyInstaller), there is no `.env` file and no way to persistently configure API keys. Currently:

- The `aicp setup` command creates a `.env` template, but this only works in a dev/source context
- API keys are read from `os.getenv()` — users must `export FAL_KEY=...` every shell session
- The binary has XDG directory support (`~/.config/video-ai-studio/`) but nothing writes credentials there
- No `set-key`, `get-key`, or `check-keys` commands exist

## Solution

Add three new CLI commands (`set-key`, `get-key`, `check-keys`) that store and retrieve API keys from a persistent credentials file at `~/.config/video-ai-studio/credentials.env`. Then wire the key resolution chain so every service checks this file before falling back to environment variables.

**Key Resolution Order (after implementation):**
1. Environment variable (e.g., `FAL_KEY`) — always wins for CI/scripting
2. Credentials file (`~/.config/video-ai-studio/credentials.env`) — persistent storage for binary users
3. `.env` file in working directory (existing dotenv behavior)

---

## Subtasks

### Subtask 1: Create `credentials.py` — Credential Store Module (~8 min)

Create a new module that handles reading/writing API keys to the XDG config directory.

**New file:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/credentials.py`

**Responsibilities:**
- `credentials_path()` → returns `config_dir() / "credentials.env"`
- `save_key(key_name, key_value)` → writes/updates a key in the credentials file
- `load_key(key_name)` → reads a specific key from the credentials file
- `load_all_keys()` → returns dict of all stored keys
- `delete_key(key_name)` → removes a key from the credentials file
- `inject_keys()` → loads all stored keys into `os.environ` (only if not already set, so env vars win)

**Key design decisions:**
- Use simple `KEY=value` format (same as `.env`) — compatible with `python-dotenv`
- File permissions: `0o600` (owner read/write only) on Unix for security
- The `inject_keys()` function is the bridge — called early in CLI startup so all downstream code works transparently

**Related files:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/paths.py` — reuse `config_dir()`, `ensure_dir()`

---

### Subtask 2: Add `set-key`, `get-key`, `check-keys` CLI Commands (~8 min)

Add a new command module for key management commands.

**New file:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/keys.py`

**Commands:**

#### `aicp set-key <KEY_NAME> <KEY_VALUE>`
```bash
# Set a single key
aicp set-key FAL_KEY fal_abc123...

# Set interactively (prompt hides input)
aicp set-key FAL_KEY --interactive
```
- Validates key name against known keys: `FAL_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `ELEVENLABS_API_KEY`
- Warns (but allows) unknown key names
- Stores to `~/.config/video-ai-studio/credentials.env`
- Sets file permissions to `0o600`
- Supports `--json` output mode

#### `aicp get-key <KEY_NAME>`
```bash
aicp get-key FAL_KEY
# Output: FAL_KEY=fal_abc1...23 (masked middle)

aicp get-key FAL_KEY --reveal
# Output: FAL_KEY=fal_abc123full_value_here
```
- Shows masked value by default (first 6 + last 3 chars)
- `--reveal` flag shows full value
- `--json` returns `{"key": "FAL_KEY", "set": true, "source": "credentials"}`

#### `aicp check-keys`
```bash
aicp check-keys
# Output:
# FAL_KEY        ✓ set (credentials)
# GEMINI_API_KEY ✓ set (environment)
# OPENROUTER_API_KEY  ✗ not set
# ELEVENLABS_API_KEY  ✗ not set

aicp check-keys --json
# {"keys": [{"name": "FAL_KEY", "set": true, "source": "credentials"}, ...]}
```
- Checks all known API keys
- Shows source: `credentials`, `environment`, or `not set`
- Supports `--json` output

**Registration:** Add `register_key_commands` to `cli/commands/__init__.py`

**Related files:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/__init__.py` — register new command group
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/click_app.py` — import registration
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/output.py` — reuse CLIOutput for json/quiet modes

---

### Subtask 3: Wire Key Injection into CLI Startup (~5 min)

Make the stored credentials available to all downstream services transparently.

**Modify:** `packages/core/ai_content_pipeline/ai_content_pipeline/cli/click_app.py`

**Changes:**
- Import `inject_keys` from `credentials.py`
- Call `inject_keys()` in the root `cli()` group callback (before any subcommand runs)
- This ensures `os.environ["FAL_KEY"]` is populated from credentials if not already set
- All existing service code (`fal_ai.py`, `google.py`, etc.) works without modification

**Why this works:**
- `inject_keys()` only sets keys that aren't already in the environment
- Environment variables from shell (`export FAL_KEY=...`) still take priority
- `.env` files loaded by individual modules can still override (existing behavior preserved)
- Zero changes needed in provider code (`fal_ai.py`, `google.py`, `openrouter.py`, `elevenlabs.py`)

**Related files:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/cli/click_app.py:50-67` — the `cli()` callback where injection happens
- `packages/core/ai_content_platform/services/fal_ai.py:34-37` — unchanged, reads from env
- `packages/core/ai_content_platform/services/google.py:43-46` — unchanged
- `packages/core/ai_content_platform/services/openrouter.py:35-38` — unchanged
- `packages/core/ai_content_platform/services/elevenlabs.py:31-34` — unchanged

---

### Subtask 4: Unit Tests (~9 min)

**New file:** `tests/test_cli_credentials.py`

**Test cases:**

1. **`test_save_and_load_key`** — save a key, load it back, verify match
2. **`test_load_missing_key`** — load a key that doesn't exist, returns `None`
3. **`test_delete_key`** — save a key, delete it, verify gone
4. **`test_inject_keys_respects_env`** — set `FAL_KEY` in env, inject from credentials, verify env value wins
5. **`test_inject_keys_fills_missing`** — don't set env, inject from credentials, verify it appears in env
6. **`test_set_key_cli_command`** — invoke `aicp set-key FAL_KEY test123` via Click test runner
7. **`test_get_key_cli_masked`** — invoke `aicp get-key FAL_KEY`, verify output is masked
8. **`test_check_keys_cli_json`** — invoke `aicp check-keys --json`, verify JSON structure
9. **`test_credentials_file_permissions`** — verify file has `0o600` permissions (Unix only)
10. **`test_set_key_unknown_warns`** — set an unknown key name, verify warning in output

**Test strategy:**
- Use `tmp_path` fixture to isolate credentials file (monkeypatch `config_dir()`)
- Use Click's `CliRunner` for CLI command tests
- Monkeypatch `os.environ` for injection tests

**Related files:**
- `tests/test_click_app.py` — reference for Click CLI test patterns
- `tests/test_core.py` — reference for env-based test patterns

---

## File Change Summary

| Action | File Path | Lines |
|--------|-----------|-------|
| **CREATE** | `packages/core/ai_content_pipeline/ai_content_pipeline/cli/credentials.py` | ~90 |
| **CREATE** | `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/keys.py` | ~120 |
| **CREATE** | `tests/test_cli_credentials.py` | ~150 |
| **MODIFY** | `packages/core/ai_content_pipeline/ai_content_pipeline/cli/commands/__init__.py` | +3 |
| **MODIFY** | `packages/core/ai_content_pipeline/ai_content_pipeline/cli/click_app.py` | +5 |

**Total:** ~370 lines added, 2 files modified, 3 files created

---

## Long-Term Considerations

- **Security:** Credentials file uses `0o600` permissions; keys are never logged or shown in `--debug` output
- **Extensibility:** New API keys can be added by updating the `KNOWN_KEYS` list in `credentials.py`
- **Backward compatible:** Zero changes to existing provider code; env vars and `.env` still work
- **Cross-platform:** Uses XDG paths module which already handles Windows (`%APPDATA%`) and Unix (`~/.config/`)
- **Binary-friendly:** No dependency on working-directory `.env` files; credentials persist in user's home directory
