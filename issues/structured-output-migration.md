# Feature: Migrate LLM Calls to Native Structured Output

## Problem

The novel2movie pipeline chains 4-5 LLM calls that each expect valid JSON responses. With kimi-k2.5 returning trailing commas, markdown fences, and truncated output, each step has a ~10-15% failure rate. Over 5 sequential steps, end-to-end success drops to ~50-60%.

Current mitigations (`parse_llm_json()`, retry loops, increased `max_tokens`) are bandaids. The root cause is **asking LLMs to produce JSON via text prompts and then regex-parsing the output**.

## Solution

Use **native structured output** (`response_format: { type: "json_schema" }`) via OpenRouter. This constrains the model at the token-generation level to only produce valid JSON matching a provided schema. The API guarantees valid JSON — no parsing, no regex, no retries needed.

## Key Finding

**Kimi K2.5 already supports structured output on OpenRouter.** Its supported params include `response_format`. No model switch required for Phase 1.

Alternative models with native structured output support (for future flexibility):
| Model | OpenRouter ID | Input $/1M | Output $/1M |
|-------|--------------|-----------|------------|
| Kimi K2.5 | `moonshotai/kimi-k2.5` | $0.50 | $2.80 |
| GPT-4o mini | `openai/gpt-4o-mini` | $0.15 | $0.60 |
| Gemini 2.5 Flash | `google/gemini-2.5-flash` | $0.30 | $2.50 |

## Implementation Estimate

**Total: ~35 minutes** — broken into 4 subtasks.

---

## Subtask 1: Add `response_format` support to LLM adapter (~10 min)

### What
Upgrade `chat_with_structured_output()` to use OpenRouter's native `response_format` parameter instead of the current prompt-injection approach. Add a `use_native_structured_output` flag to config for gradual rollout.

### Why
The existing `chat_with_structured_output()` method (line 270) appends the JSON schema to the system prompt and hopes the LLM complies. This is the prompt-based approach. We need to pass the schema as an API parameter so the provider enforces it at the token level.

### Key Detail — litellm caveat
litellm does not recognize OpenRouter as supporting structured outputs and may strip the `response_format` parameter. The workaround is passing it via `extra_body`:

```python
response = await acompletion(
    model="openrouter/moonshotai/kimi-k2.5",
    messages=formatted_messages,
    temperature=0.7,
    max_tokens=8192,
    extra_body={
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": pydantic_model.model_json_schema()
            }
        },
        "provider": {
            "require_parameters": True
        }
    }
)
```

The `require_parameters: True` ensures OpenRouter only routes to providers that actually support `json_schema` (won't silently fall back to `json_object`).

### Files
- **Modify**: `packages/core/ai_content_platform/vimax/adapters/llm_adapter.py`
  - `LLMAdapterConfig` — add `use_native_structured_output: bool = True`
  - `chat_with_structured_output()` — two code paths:
    - **Native path** (new): pass `response_format` via `extra_body`
    - **Legacy path** (existing): prompt-injection fallback for models without support
  - Response parsing: with native structured output, `json.loads()` on the response content is sufficient (no regex needed), but keep `parse_llm_json()` as safety net

### Acceptance Criteria
- `chat_with_structured_output(messages, output_model=MyPydanticModel)` uses native `response_format` by default
- Falls back to prompt-injection approach if `use_native_structured_output=False`
- Works with kimi-k2.5, gpt-4o-mini, gemini-2.5-flash via OpenRouter

---

## Subtask 2: Define Pydantic response schemas for each agent (~8 min)

### What
Create Pydantic models that define the exact JSON schema each agent expects. These will be passed to the structured output API.

### Why
Native structured output requires a JSON schema. Currently, the expected shapes are only defined in prompt text (English instructions). We need formal Pydantic models so `model_json_schema()` can generate the schema for the API.

### Schemas Needed

**A. Screenwriter — `ScreenplayResponse`**
```
title: str
logline: str
scenes: List[SceneResponse]
  scene_id: str
  title: str
  location: str
  time: str
  shots: List[ShotResponse]
    shot_id: str
    shot_type: str (enum: wide, medium, close_up, extreme_close_up, over_shoulder, pov, aerial)
    description: str
    camera_movement: str (enum: static, pan, tilt, dolly, zoom, tracking, crane, handheld)
    duration_seconds: float
    image_prompt: str
    video_prompt: str
```

**B. Character Extractor — `CharacterListResponse`**
```
characters: List[CharacterResponse]
  name: str
  description: str
  age: str
  gender: str
  appearance: str
  personality: str
  role: str (enum: protagonist, antagonist, supporting, minor)
  relationships: List[str]
```

**C. Novel Compression — `ChapterCompressionResponse`**
```
title: str
scenes: List[SceneCompression]
  title: str
  description: str
  characters: List[str]
  setting: str
```

### Files
- **Create**: `packages/core/ai_content_platform/vimax/agents/schemas.py`
  - All 3 response schemas as Pydantic `BaseModel` classes
  - Use `Literal` types for enums (structured output requires this format over Python `Enum`)
  - Include `model_config = {"extra": "forbid"}` for strict mode compatibility

### Acceptance Criteria
- Each schema's `model_json_schema()` output is valid JSON Schema
- Schemas match the current prompt instructions exactly (no new fields, no missing fields)
- Shot type and camera movement enums cover all values the screenwriter currently handles

---

## Subtask 3: Migrate agents to use structured output (~12 min)

### What
Update each agent to call `chat_with_structured_output()` with the new Pydantic schemas instead of `chat()` + `parse_llm_json()`.

### Changes Per Agent

**A. Screenwriter** (`screenwriter.py`)
- Replace `chat()` call (line ~195) with `chat_with_structured_output(messages, output_model=ScreenplayResponse)`
- Remove retry loop (lines 193-216) — native structured output eliminates parse failures
- Keep enum mapping logic (ShotType/CameraMovement conversion) since the response uses string values
- Remove `parse_llm_json()` import

**B. Character Extractor** (`character_extractor.py`)
- Replace `chat()` call (line ~90) with `chat_with_structured_output(messages, output_model=CharacterListResponse)`
- Response is now `CharacterListResponse` object, access `.characters` list directly
- Remove `parse_llm_json()` import

**C. Novel2Movie Compression** (`novel2movie.py`, `_compress_novel` method)
- Replace raw `re.search() + json.loads()` (lines 321-323) with `chat_with_structured_output(messages, output_model=ChapterCompressionResponse)`
- This is the only parsing point that doesn't use `parse_llm_json()` — it's the most fragile

### Files
- **Modify**: `packages/core/ai_content_platform/vimax/agents/screenwriter.py`
  - Import `ScreenplayResponse` from schemas
  - Replace `chat()` → `chat_with_structured_output()`
  - Remove retry loop, keep enum mapping
- **Modify**: `packages/core/ai_content_platform/vimax/agents/character_extractor.py`
  - Import `CharacterListResponse` from schemas
  - Replace `chat()` → `chat_with_structured_output()`
  - Simplify response handling
- **Modify**: `packages/core/ai_content_platform/vimax/pipelines/novel2movie.py`
  - Import `ChapterCompressionResponse` from schemas
  - Replace regex parsing in `_compress_novel()` → `chat_with_structured_output()`
- **Keep (no changes)**: `packages/core/ai_content_platform/vimax/agents/base.py`
  - `parse_llm_json()` stays as utility for any future non-structured-output use cases

### Acceptance Criteria
- All 3 JSON parsing points use native structured output
- No more `re.search()` or `parse_llm_json()` in the critical path
- Agents still produce the same output types (`Script`, `CharacterInNovel`, `ChapterSummary`)
- `parse_llm_json()` retained in `base.py` but no longer called by default

---

## Subtask 4: Tests (~5 min)

### What
Write tests verifying structured output integration works correctly.

### Test Cases

**A. Schema validation tests**
- Each Pydantic response schema produces valid `model_json_schema()` output
- Schemas can parse example JSON matching the expected format
- Schemas reject JSON missing required fields

**B. LLM adapter structured output tests**
- `chat_with_structured_output()` passes `response_format` via `extra_body` (mock litellm)
- `require_parameters: True` is included in provider config
- Falls back to prompt-injection when `use_native_structured_output=False`
- `json.loads()` on mock response produces valid Pydantic model

**C. Agent integration tests**
- Screenwriter produces valid `Script` from structured `ScreenplayResponse`
- Character extractor produces valid `CharacterInNovel` list from structured `CharacterListResponse`
- Novel compression produces valid `ChapterSummary` from structured `ChapterCompressionResponse`

### Files
- **Create**: `tests/unit/vimax/test_structured_output.py`
  - Schema validation tests
  - LLM adapter mock tests
  - Agent response mapping tests

### Acceptance Criteria
- All tests pass with mocked LLM responses
- Tests verify the `extra_body` parameter structure is correct
- Tests cover both native and fallback code paths

---

## Architecture Decision: Why Not Tool Calling?

Claude models on OpenRouter don't support `response_format` but do support `tools`/`tool_choice`. We chose `response_format` over tool calling because:

1. **Kimi K2.5 supports it** — no model change needed
2. **Simpler API** — one parameter vs defining tools + parsing tool calls
3. **Portable** — same parameter works across OpenAI, Gemini, Kimi models
4. **Tool calling is overkill** — we're not asking the model to "call a function," we're asking it to return structured data

If we ever need Claude-specific structured output, we can add a tool-calling code path later.

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| litellm strips `response_format` for OpenRouter | Medium | Use `extra_body` workaround (confirmed working) |
| Kimi K2.5 `json_schema` mode produces lower quality content | Low | Schema doesn't constrain creativity, only structure |
| OpenRouter routing changes break `require_parameters` | Low | Pin to specific provider if needed |
| Schema too strict, rejects valid creative variations | Low | Use `str` for free-text fields, enums only for controlled values |

## Rollback Plan

`use_native_structured_output=False` in `LLMAdapterConfig` reverts to prompt-injection + `parse_llm_json()` approach. No code deletion needed — both paths coexist.

---

## Expected Impact

| Metric | Before | After |
|--------|--------|-------|
| Per-step JSON parse success rate | ~85-90% | ~99.9% (API-guaranteed) |
| End-to-end pipeline success (5 steps) | ~50-60% | ~99.5% |
| Retry LLM calls needed | 1-2 per run | 0 |
| Lines of parsing/repair code in hot path | ~80 | ~10 |
| Cost per run | Same | Same (same model, same tokens) |
