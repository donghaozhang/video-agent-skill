# VMAX-Test Branch: Novel2Movie Pipeline Fixes

## Summary

Full end-to-end testing and fixing of `aicp vimax novel2movie --storyboard-only` pipeline on the `VMAX-test` branch. Multiple bugs discovered and fixed across 8 commits.

---

## Commits

### 1. `fix: Change default text-to-image model from flux_dev to nano_banana_pro`
- **Files**: `config/constants.py`, `docs/aicp-vimax-commands.md`
- Changed `DEFAULT_CHAIN_CONFIG` and all doc examples from `flux_dev` to `nano_banana_pro`

### 2. `fix: Update docs examples to use kimi-k2.5 instead of claude-3.5-sonnet`
- **Files**: `docs/aicp-vimax-commands.md`
- 2 example commands still referenced `claude-3.5-sonnet`, code already defaulted to `kimi-k2.5`

### 3. `feat: Add --storyboard-only flag to novel2movie (steps 1-5, skip video)`
- **Files**: `novel2movie.py`, `commands.py`, `docs/aicp-vimax-commands.md`
- New `--storyboard-only` flag skips video generation (step 6) and assembly (step 7)
- Saves significant cost by avoiding the most expensive pipeline step

### 4. `feat: Save intermediate results by default + photorealistic storyboard style`
- **Files**: `novel2movie.py`, `storyboard_artist.py`, `commands.py`, `docs/aicp-vimax-commands.md`
- **Intermediate saves**: `characters.json`, `chapters.json`, `scripts/chapter_N.json`, `portrait_registry.json`, `summary.json` — all saved by default via `save_intermediate=True`
- **Style change**: Default storyboard style changed from `"storyboard panel, cinematic composition, "` to `"photorealistic, cinematic lighting, film still, "`

### 5. `fix: Pass aspect_ratio directly for nano_banana_pro (not image_size)`
- **Files**: `image_adapter.py`
- **Root cause**: FAL API models use different parameter names. Flux models use `image_size: "landscape_16_9"`, but nano_banana_pro/imagen4/gpt_image_1_5/seedream_v3 use `aspect_ratio: "16:9"` directly
- **Symptom**: Storyboard images generated as 1:1 square instead of 16:9 widescreen
- **Fix**: Added `ASPECT_RATIO_MODELS` set and conditional argument building

### 6. `fix: Robust JSON parsing for LLM responses in character extractor and screenwriter`
- **Files**: `base.py`, `character_extractor.py`, `screenwriter.py`
- **Root cause**: kimi-k2.5 LLM returns JSON with trailing commas, markdown code fences, and extra commentary text
- **Old parser**: Used non-greedy regex `\[.*?\]` which truncated at first `]` inside nested arrays like `relationships: []`
- **Fix**: New shared `parse_llm_json()` helper in `base.py` that handles:
  - Markdown code fences
  - Trailing commas (`,]` and `,}`)
  - Extra text before/after JSON
  - Greedy matching for nested structures
  - Line-by-line repair as last resort

### 7. `fix: Add retry loop for screenwriter JSON parsing + increase max_tokens`
- **Files**: `screenwriter.py`, `llm_adapter.py`
- Screenwriter retries LLM call up to 2 times on JSON parse failure
- Increased `max_tokens` from 4096 to 8192 — screenplay JSON with detailed image/video prompts was being truncated

### 8. `fix: Add fallback prompt when LLM returns empty portrait prompt`
- **Files**: `character_portraits.py`
- **Root cause**: LLM occasionally returns empty content (`content=''`) for portrait generation prompts
- **Symptom**: FAL API 422 error (`String should have at least 3 characters`) causing portrait generation to fail for that character
- **Fix**: Check if LLM response is < 3 chars, build fallback prompt from character description + style config

---

## Bugs Found

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| Storyboard images 1:1 square | `image_size` param ignored by nano_banana_pro API | Use `aspect_ratio` param directly for non-Flux models |
| Character extraction always fails | Non-greedy regex `\[.*?\]` stops at first `]` in nested arrays | Greedy `\[[\s\S]*\]` + trailing comma removal |
| Screenplay generation fails ~50% | LLM returns malformed JSON with trailing commas | `parse_llm_json()` + retry loop |
| Screenplay truncated mid-JSON | `max_tokens: 4096` too small for detailed prompts | Increased to 8192 |
| Intermediate results lost | Pipeline only saved images to disk, not JSON data | Added `save_intermediate=True` with 5 save methods |
| Docs show wrong defaults | Examples used `flux_dev` and `claude-3.5-sonnet` | Updated to `nano_banana_pro` and `kimi-k2.5` |
| Portrait generation fails for some characters | LLM returns empty content for portrait prompts | Fallback prompt built from character description |

---

## Lessons Learned

1. **FAL API is not uniform** — different models use different parameter names (`image_size` vs `aspect_ratio`). Always check the specific model's API docs, not just one model's pattern.

2. **LLM JSON output is unreliable** — kimi-k2.5 frequently produces:
   - Trailing commas in arrays/objects
   - Markdown code fences wrapping JSON
   - Extra commentary text before/after JSON
   - Truncated output when response exceeds max_tokens
   - Never trust `json.loads()` on raw LLM output — always use a resilient parser.

3. **Non-greedy regex breaks on nested JSON** — `\[.*?\]` matches `[...]` but stops at the first `]`, which fails on `[{"relationships": []}, ...]`. Always use greedy `\[[\s\S]*\]` for JSON extraction.

4. **max_tokens matters for structured output** — screenplay JSON with 6 shots, each having `image_prompt` (200+ chars) and `video_prompt` (200+ chars), easily exceeds 4096 tokens. Default should be generous for structured generation tasks.

5. **Retry is cheap, failure is expensive** — a single LLM retry costs ~$0.001 but saves the entire pipeline from failing. Always retry on parseable errors.

6. **Save intermediate results by default** — users expect to see what the pipeline produced at each step. Without saves, a pipeline failure means all prior work is lost and must be regenerated.

7. **Guard against empty LLM responses** — LLMs can return empty content silently (no error, just `content=''`). Always validate LLM output length before passing to downstream APIs.

---

## Test Results

- **Unit tests**: 719 passed, 1 pre-existing failure (Windows cp1252 encoding)
- **Integration**: Full novel2movie pipeline runs steps 1-5 successfully with `--storyboard-only`
- **Output**: 16:9 photorealistic storyboard images + all intermediate JSON files saved

## Successful Pipeline Run (final)

```
Pipeline completed successfully!
   Chapters processed: 1
   Scripts generated: 1
   Characters found: 3
   Total cost: $0.050
   Duration: ~20 minutes
```

**Output structure:**
```
media/generated/vimax/novel2movie/
├── First_Contact/
│   ├── characters.json          (3 characters: Elena Vasquez, James Park, Sage)
│   ├── chapters.json            (1 chapter)
│   ├── portrait_registry.json   (8 portraits: James Park + Sage, 4 views each)
│   ├── scripts/
│   │   └── chapter_001.json     (2 scenes, 6 shots, 30s total)
│   └── summary.json
├── portraits/                   (23 portrait images from all runs)
└── storyboard/
    └── The_Arrival/
        ├── shot_001.png         (16:9 photorealistic, Elena silhouette + twin suns)
        ├── shot_002.png         (boots on crystal soil, violet spires)
        ├── shot_003.png         (two astronauts descending)
        ├── shot_004.png         (obsidian walls with bioluminescent symbols)
        ├── shot_005.png         (Sage the Tessari emerging, six-fingered hand)
        └── shot_006.png         (underground Tessari crystal city)
```
