# Long Code Files Report

**Generated:** 2026-01-13
**Last Updated:** 2026-01-19
**Threshold:** 800+ lines

---

## Files Exceeding 800 Lines

| # | File Path | Lines | Status |
|---|-----------|-------|--------|
| 1 | `packages/providers/fal/text-to-image/fal_text_to_image_generator.py` | 892 | Needs refactoring |

**Total:** 1 file exceeds the 800-line threshold

---

## Recently Completed Refactoring

### ✅ `ai_analysis_commands.py` (1633 → 49 lines) - COMPLETED

**Refactored on:** 2026-01-14

Split into modular components:
- `video_utils/ai_analysis_commands.py` - 49 lines (re-export layer)
- `video_utils/command_utils.py` - 355 lines (shared utilities)
- `video_utils/ai_commands/__init__.py` - 53 lines (package exports)
- `video_utils/ai_commands/video_commands.py` - 661 lines
- `video_utils/ai_commands/audio_commands.py` - 280 lines
- `video_utils/ai_commands/image_commands.py` - 274 lines
- `video_utils/analyzer_factory.py` - 221 lines
- `video_utils/analyzer_protocol.py` - 302 lines
- `video_utils/fal_video_analyzer.py` - 584 lines
- `tests/unit/test_ai_analysis_commands.py` - 405 lines (unit tests)

### ✅ `executor.py` (1411 → 467 lines) - COMPLETED

**Refactored on:** 2026-01-13

Split into modular components:
- `pipeline/executor.py` - 467 lines (orchestration only)
- `pipeline/report_generator.py` - 344 lines
- `pipeline/step_executors/base.py` - 112 lines
- `pipeline/step_executors/image_steps.py` - 208 lines
- `pipeline/step_executors/video_steps.py` - 354 lines
- `pipeline/step_executors/audio_steps.py` - 141 lines

### ✅ `video_understanding.py` (1363 lines) - DELETED

**Deleted on:** 2026-01-12

Duplicate file removed. Functionality consolidated into `gemini_analyzer.py`.

---

## Recommendations

Per project guidelines in CLAUDE.md:
> "Never create a file longer than 500 lines of code. If a file approaches this limit, refactor by splitting it into modules or helper files."

### Suggested Refactoring

#### 1. `fal_text_to_image_generator.py` (892 lines) - Priority: HIGH
- Extract individual model implementations to separate files
- Create `models/` subdirectory similar to avatar module pattern
- Move shared utilities to `utils.py`

#### 2. `command_dispatcher.py` (778 lines) - Priority: MEDIUM
- Split command handlers into separate modules
- Extract utility functions

#### 3. `video_commands.py` (661 lines) - Priority: MEDIUM
- Consider splitting into smaller command groups
- Extract common patterns to shared utilities

---

## Files Approaching Limit (500-800 lines)

| File Path | Lines | Priority |
|-----------|-------|----------|
| `video_utils/command_dispatcher.py` | 778 | Medium |
| `fal/image-to-image/examples/demo.py` | 758 | Low (demo file) |
| `fal/image-to-video/fal_image_to_video_generator.py` | 754 | Medium |
| `video_utils/gemini_analyzer.py` | 752 | Medium |
| `ai_content_pipeline/__main__.py` | 663 | Medium |
| `video_utils/ai_commands/video_commands.py` | 661 | Medium |
| `video_utils/media_processing_controller.py` | 632 | Low |
| `video_utils/enhanced_audio_processor.py` | 624 | Low |
| `video_utils/openrouter_analyzer.py` | 589 | Low |
| `video_utils/fal_video_analyzer.py` | 584 | Low |
| `ai_content_platform/core/parallel_executor.py` | 569 | Low |
| `ai_content_platform/cli/commands.py` | 563 | Low |
| `fal/text-to-video/fal_text_to_video_generator.py` | 541 | Low |
| `video_utils/ai_utils.py` | 522 | Low |
| `ai_content_platform/tests/unit/test_utils.py` | 521 | Low (test file) |
| `fal/avatar/fal_avatar_generator.py` | 516 | Low |
| `fal/image-to-image/fal_image_to_image/models/photon.py` | 514 | Low |

---

## Action Items

- [x] ~~Refactor `executor.py`~~ - **COMPLETED** (467 lines)
- [x] ~~Refactor `video_understanding.py`~~ - **DELETED** (duplicate removed)
- [x] ~~Refactor `ai_analysis_commands.py`~~ - **COMPLETED** (1633 → 49 lines re-export layer)
- [ ] Refactor `fal_text_to_image_generator.py` - Priority: High (892 lines)
- [ ] Refactor `command_dispatcher.py` - Priority: Medium (778 lines)
- [ ] Monitor files approaching 500-line limit

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Files > 800 lines | 1 |
| Files 500-800 lines | 17 |
| Total Python files scanned | 100+ |
