# Batch PR Review Processor

Process all PR review task files in a directory, handling multiple comments per file correctly.

## Critical: Group by File

**Multiple comments often target the same file.** If you fix line 110, then line 253, then line 330 separately, line numbers shift after each fix and later fixes will be wrong.

**Solution:** Group comments by source file, process each file's comments together (bottom-up).

## Instructions

1. List all `.md` task files in the directory
2. **Group by source file** - extract the file path from each task
3. For each source file (one at a time):
   a. Collect all comments for that file
   b. Sort by line number **DESCENDING** (fix from bottom up)
   c. Read the source file ONCE
   d. Evaluate and fix each comment (bottom to top)
   e. Log results
4. Move to next source file
5. After all files processed, provide summary

## Process

```
# Step 1: Group tasks by source file
files_map = {}
for task_file in directory/*.md:
    source_file = extract_file_path(task_file)
    files_map[source_file].append(task_file)

# Step 2: Process each source file
for source_file, tasks in files_map:
    # Sort by line number descending (bottom-up)
    tasks = sort_by_line_descending(tasks)

    # Read source once
    content = read(source_file)

    # Fix each comment (bottom to top)
    for task in tasks:
        evaluate_and_fix(task)
        log_result()
```

## Why Bottom-Up?

```
File has 400 lines. Comments at lines 110, 253, 330.

❌ Top-down (WRONG):
  - Fix line 110 (adds 3 lines) → file now 403 lines
  - Fix line 253 → actually hits old line 250 (shifted!)
  - Fix line 330 → completely wrong location

✅ Bottom-up (CORRECT):
  - Fix line 330 first → lines above unchanged
  - Fix line 253 → lines above still correct
  - Fix line 110 → no problem
```

## Output Summary

```markdown
# PR Review Batch Results

## Summary
- Total: X comments
- Fixed: Y
- Not applicable: Z
- Already fixed: W

## By File

### path/to/file.ts (3 comments)
| Line | Status | Notes |
|------|--------|-------|
| 330 | FIXED | ... |
| 253 | FIXED | ... |
| 110 | NOT_APPLICABLE | ... |

### path/to/other.ts (2 comments)
...
```

## Important

- **Group by file first** - never process same file multiple times separately
- **Fix bottom-up** within each file
- Read each source file only once per batch
- Create results.md when done
