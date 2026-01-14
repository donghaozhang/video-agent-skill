# Long Code Files Report

**Generated:** 2026-01-13
**Last Updated:** 2026-01-13
**Threshold:** 800+ lines

---

## Files Exceeding 800 Lines

| # | File Path | Lines | Status |
|---|-----------|-------|--------|
| 1 | `packages/services/video-tools/video_utils/ai_analysis_commands.py` | 1633 | Needs refactoring |
| 2 | `packages/providers/fal/text-to-image/fal_text_to_image_generator.py` | 892 | Needs refactoring |

**Total:** 2 files exceed the 800-line threshold

---

## Recently Completed Refactoring

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

#### 1. `ai_analysis_commands.py` (1633 lines)
- Split into separate command modules by functionality
- Create `commands/` subdirectory with individual command files
- Extract shared utilities to `command_utils.py`

#### 2. `fal_text_to_image_generator.py` (892 lines)
- Extract individual model implementations to separate files
- Create `models/` subdirectory similar to avatar module pattern
- Move shared utilities to `utils.py`

---

## Files Approaching Limit (500-800 lines)

| File Path | Lines |
|-----------|-------|
| `video_utils/command_dispatcher.py` | 769 |
| `fal/image-to-image/examples/demo.py` | 758 |
| `fal/image-to-video/fal_image_to_video_generator.py` | 754 |
| `video_utils/gemini_analyzer.py` | 752 |
| `video_utils/media_processing_controller.py` | 632 |
| `video_utils/enhanced_audio_processor.py` | 624 |
| `ai_content_pipeline/__main__.py` | 602 |
| `video_utils/openrouter_analyzer.py` | 589 |
| `ai_content_platform/core/parallel_executor.py` | 569 |
| `ai_content_platform/cli/commands.py` | 563 |

---

## Action Items

- [x] ~~Refactor `executor.py`~~ - **COMPLETED** (467 lines)
- [x] ~~Refactor `video_understanding.py`~~ - **DELETED** (duplicate removed)
- [ ] Refactor `ai_analysis_commands.py` - Priority: High
- [ ] Refactor `fal_text_to_image_generator.py` - Priority: Medium
- [ ] Monitor files approaching 500-line limit
