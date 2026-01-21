# Documentation Redundancy Cleanup Plan

**Created:** 2025-01-21
**Completed:** 2025-01-21
**Status:** COMPLETED
**Priority:** Medium-High
**Files Modified:** 12

---

## Overview

Analysis of the `docs/` folder revealed significant content duplication across 35 markdown files (~14,193 lines). This plan outlines tasks to consolidate redundant documentation while maintaining comprehensive coverage.

---

## Phase 1: HIGH Priority - API & CLI Reference Consolidation

### Task 1.1: Consolidate CLI Command References
**Files Involved:**
- `reference/cli-commands.md` (447 lines) - KEEP as authoritative
- `reference/cheat-sheet.md` (285 lines) - MODIFY to reference cli-commands.md
- `reference/api-quick-ref.md` (402 lines) - MODIFY to remove CLI duplication

**Actions:**
- [x] Review `cli-commands.md` for completeness
- [x] Remove CLI section from `api-quick-ref.md` (lines ~145-235), replace with link to `cli-commands.md`
- [x] Update `cheat-sheet.md` CLI section to be a condensed version with "See cli-commands.md for full reference" note
- [x] Ensure no broken internal links after changes

**Lines Removed:** ~150+

---

### Task 1.2: Consolidate API Documentation
**Files Involved:**
- `api/python-api.md` (484 lines) - KEEP as authoritative
- `reference/api-quick-ref.md` (402 lines) - MODIFY to be true quick reference

**Actions:**
- [x] Review `python-api.md` for completeness
- [x] Refactor `api-quick-ref.md` to contain ONLY:
  - Method signatures (no full examples)
  - Return type summaries
  - Links to `python-api.md` for detailed examples
- [x] Add clear header: "This is a condensed reference. See [Python API](../api/python-api.md) for complete documentation."

**Lines Removed:** ~100+

---

## Phase 2: MEDIUM Priority - Content Deduplication

### Task 2.1: Centralize YAML Pipeline Documentation
**Files Involved:**
- `guides/pipelines/yaml-pipelines.md` (461 lines) - KEEP as authoritative
- `reference/api-quick-ref.md` - MODIFY (remove YAML section)
- `examples/basic-examples.md` (446 lines) - MODIFY (link to yaml-pipelines.md)
- `examples/advanced-pipelines.md` (530 lines) - KEEP (advanced use cases)

**Actions:**
- [x] Remove YAML configuration section from `api-quick-ref.md` (lines ~239-303)
- [x] Condensed YAML section with link to `yaml-pipelines.md`
- [x] Keep actual example configs in example files, remove explanatory duplication

**Lines Removed:** ~80+

---

### Task 2.2: Streamline Getting Started Guides
**Files Involved:**
- `guides/getting-started/installation.md` (310 lines) - KEEP as authoritative for installation
- `guides/getting-started/quick-start.md` (152 lines) - MODIFY to link to installation.md
- `guides/getting-started/learning-path.md` (495 lines) - MODIFY to link to other guides

**Actions:**
- [x] In `quick-start.md`, replace detailed installation steps with brief summary + link to `installation.md`
- [x] In `learning-path.md`, added link to installation guide
- [x] Keep `quick-start.md` focused on "first 5 minutes" experience only

**Lines Removed:** ~60+

---

### Task 2.3: Merge Quick Reference Cards
**Files Involved:**
- `reference/cheat-sheet.md` (285 lines) - EVALUATE
- `reference/api-quick-ref.md` (402 lines) - EVALUATE

**Actions:**
- [x] Determine if both files are needed or can be merged
- [x] **Option A chosen:** Keep both with distinct purposes (cheat-sheet = patterns/tips, api-quick-ref = Python API)
- [x] Added cross-references between both files
- [x] Condensed model quick reference in both (link to models.md)

**Decision:** Option A - kept both files with cross-references

---

### Task 2.4: Centralize Model Information
**Files Involved:**
- `reference/models.md` (481 lines) - KEEP as single source of truth
- `reference/cheat-sheet.md` - MODIFY (remove model tables)
- `reference/api-quick-ref.md` - MODIFY (remove model tables)
- `guides/optimization/cost-management.md` - MODIFY (link to models.md for pricing)
- `guides/optimization/performance.md` - MODIFY (link to models.md for comparisons)

**Actions:**
- [x] Verified `models.md` has complete pricing and performance data
- [x] Added reference links to models.md in cost-management.md and performance.md
- [x] Condensed model tables in cheat-sheet.md and api-quick-ref.md with links

**Lines Removed:** ~60+

---

## Phase 3: LOW Priority - Minor Cleanup

### Task 3.1: Clarify Troubleshooting vs FAQ
**Files Involved:**
- `guides/support/troubleshooting.md` (468 lines)
- `guides/support/faq.md` (369 lines)

**Actions:**
- [x] Reviewed for duplicate Q&A entries
- [x] Files already have appropriate separation (errors vs concepts)
- [x] Added cross-references between files

**Lines Removed:** ~0 (added cross-references only)

---

### Task 3.2: Sync Navigation Files
**Files Involved:**
- `index.md` (121 lines)
- `SITEMAP.md` (241 lines)

**Actions:**
- [x] Verified both files list the same documents
- [x] Added clarifying note to SITEMAP.md with link to index.md
- [x] **Decision:** Keep SITEMAP.md - provides detailed categorization by user type

**Decision:** Keep both - index.md for overview, SITEMAP.md for detailed navigation

---

## Summary

| Phase | Tasks | Est. Lines Removed | Priority |
|-------|-------|-------------------|----------|
| Phase 1 | 2 tasks | ~250 lines | HIGH |
| Phase 2 | 4 tasks | ~200 lines | MEDIUM |
| Phase 3 | 2 tasks | ~50 lines | LOW |
| **Total** | **8 tasks** | **~500 lines** | - |

---

## Implementation Order

1. **Task 1.1** - CLI consolidation (highest duplication)
2. **Task 1.2** - API consolidation
3. **Task 2.4** - Model centralization (affects multiple files)
4. **Task 2.1** - YAML centralization
5. **Task 2.2** - Getting started streamlining
6. **Task 2.3** - Quick reference decision
7. **Task 3.1** - Troubleshooting/FAQ cleanup
8. **Task 3.2** - Navigation sync

---

## Verification Checklist

After each task:
- [x] No broken internal links
- [x] All referenced files exist
- [x] Navigation (index.md, SITEMAP.md) - no files removed, no updates needed
- [x] Content still accessible (not deleted, just consolidated with cross-references)

---

## Notes

- **Do NOT delete content** - consolidate and add cross-references
- **Preserve all unique information** - only remove true duplicates
- **Update SITEMAP.md** after any file structure changes
- **Test all internal links** after modifications
