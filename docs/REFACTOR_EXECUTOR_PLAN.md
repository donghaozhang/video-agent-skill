# Refactoring Plan: executor.py (1411 lines)

## Overview

The `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/executor.py` file has grown to **1411 lines** and violates the project guideline of maximum 500 lines per file. This plan outlines a systematic refactoring to improve maintainability, testability, and code organization.

## Current State Analysis

### File Structure (executor.py)
- **Lines 1-70**: Imports and class initialization
- **Lines 71-291**: Main `execute()` method - chain orchestration
- **Lines 293-349**: `_execute_step()` - step type dispatcher
- **Lines 351-628**: Step execution methods (text-to-image, image understanding, etc.)
- **Lines 630-768**: Legacy video generation methods (hailuo, veo, kling)
- **Lines 770-944**: Audio and video processing methods
- **Lines 946-1097**: Subtitle generation and helper methods
- **Lines 1099-1368**: Report generation and file management
- **Lines 1370-1412**: Replicate MultiTalk execution

### Identified Concerns
1. **Single Responsibility Violation**: One class handles execution, step dispatching, file management, and reporting
2. **Duplicate Logic**: Similar patterns in each `_execute_*` method
3. **Legacy Code**: Unused methods like `_execute_hailuo_video`, `_execute_veo_video`, `_execute_kling_video`
4. **Tight Coupling**: Direct imports and sys.path manipulation in methods

---

## Refactoring Plan

### Subtask 1: Create Step Executor Module

**Goal**: Extract individual step execution methods into a dedicated module

**Files to create**:
- `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/__init__.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/base.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/image_steps.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/video_steps.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/audio_steps.py`

**Details**:
1. Create `BaseStepExecutor` class with common interface
2. Move `_execute_text_to_image`, `_execute_image_understanding`, `_execute_prompt_generation`, `_execute_image_to_image` to `image_steps.py`
3. Move `_execute_image_to_video`, `_execute_add_audio`, `_execute_upscale_video`, `_execute_generate_subtitles` to `video_steps.py`
4. Move `_execute_text_to_speech`, `_execute_replicate_multitalk` to `audio_steps.py`
5. Delete unused legacy methods: `_execute_hailuo_video`, `_execute_veo_video`, `_execute_kling_video`

**Estimated reduction**: ~600 lines from executor.py

---

### Subtask 2: Extract Report Generator Module

**Goal**: Move all report generation logic to a dedicated module

**Files to create**:
- `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/report_generator.py`

**Methods to extract**:
- `_create_execution_report()` (lines 1099-1215)
- `_save_execution_report()` (lines 1217-1240)
- `_create_intermediate_report()` (lines 1242-1292)
- `_save_intermediate_report()` (lines 1294-1320)
- `_download_intermediate_image()` (lines 1322-1368)

**Estimated reduction**: ~270 lines from executor.py

---

### Subtask 3: Simplify Main Executor

**Goal**: Reduce ChainExecutor to orchestration logic only

**File to modify**:
- `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/executor.py`

**Changes**:
1. Import step executors from new module
2. Import report generator from new module
3. Simplify `_execute_step()` to use step executor registry
4. Remove duplicated helper methods (keep `_get_step_output_type` in chain.py)
5. Reduce class to ~200-250 lines

---

### Subtask 4: Update Module Exports

**Goal**: Ensure backwards compatibility

**Files to modify**:
- `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/__init__.py`

**Changes**:
1. Keep existing exports unchanged
2. Add internal imports from new modules
3. Ensure ChainExecutor maintains same public interface

---

### Subtask 5: Add Unit Tests

**Goal**: Ensure refactored code works correctly

**Files to create**:
- `tests/unit/test_step_executors.py`
- `tests/unit/test_report_generator.py`

**Test coverage**:
1. Test each step executor can be instantiated
2. Test report generation creates valid JSON
3. Test step dispatcher routes correctly
4. Test backwards compatibility of ChainExecutor public methods

---

## Final File Structure

```
packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/
├── __init__.py              # Module exports (updated)
├── chain.py                 # ContentCreationChain (unchanged)
├── executor.py              # ChainExecutor (~250 lines, orchestration only)
├── manager.py               # AIPipelineManager (unchanged)
├── parallel_extension.py    # Parallel execution (unchanged)
├── report_generator.py      # NEW: Report generation (~150 lines)
└── step_executors/          # NEW: Step execution modules
    ├── __init__.py          # Step executor exports
    ├── base.py              # BaseStepExecutor (~50 lines)
    ├── image_steps.py       # Image-related executors (~200 lines)
    ├── video_steps.py       # Video-related executors (~200 lines)
    └── audio_steps.py       # Audio-related executors (~100 lines)
```

---

## Line Count Summary

| File | Before | After |
|------|--------|-------|
| executor.py | 1411 | ~250 |
| step_executors/base.py | 0 | ~50 |
| step_executors/image_steps.py | 0 | ~200 |
| step_executors/video_steps.py | 0 | ~200 |
| step_executors/audio_steps.py | 0 | ~100 |
| report_generator.py | 0 | ~150 |

**Total lines**: ~950 (down from 1411, better organized)

---

## Implementation Order

1. **Subtask 1**: Create step executors module (highest impact)
2. **Subtask 2**: Extract report generator
3. **Subtask 3**: Simplify main executor
4. **Subtask 4**: Update module exports
5. **Subtask 5**: Add unit tests

---

## Risk Mitigation

1. **Backwards Compatibility**: ChainExecutor public interface remains unchanged
2. **Incremental Approach**: Each subtask can be tested independently
3. **Test First**: Existing integration tests should pass after each subtask
4. **Git Workflow**: Commit after each successful subtask

---

## Success Criteria

- [ ] All files under 500 lines
- [ ] Existing tests pass
- [ ] New unit tests for extracted modules
- [ ] ChainExecutor public API unchanged
- [ ] No duplicate code between modules
