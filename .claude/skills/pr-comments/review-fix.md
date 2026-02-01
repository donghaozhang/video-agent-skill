# PR Review Evaluator & Fixer

Evaluate a PR review comment and either fix the issue or explain why it doesn't apply.

## Instructions

1. Read the task file provided
2. The task file contains a code review comment with:
   - The file path to check
   - The line number
   - The issue description
   - The comment ID (for resolving)
3. Read the source file mentioned in the review
4. Evaluate if the feedback is valid
5. Take action:
   - **If valid**: Fix the code using the Edit tool
   - **If invalid**: Explain in 2-3 sentences why it doesn't apply
6. **Resolve the conversation** on GitHub (if fixed)

## Resolve After Fixing

After fixing an issue, resolve the PR conversation and move task to completed:

```bash
bash .claude/skills/pr-comments/scripts/resolve-thread.sh <owner/repo> <pr-number> <comment_id> <task_file>
```

Extract from the task file:
- `owner/repo` - from the URL field
- `pr-number` - from the URL field
- `comment_id` - from the **Comment ID** field
- `task_file` - the path to the task file you just processed

**Example:**
```bash
bash .claude/skills/pr-comments/scripts/resolve-thread.sh donghaozhang/qcut 102 2742327370 docs/pr-comments/pr-102-tasks/comment.md
```

**What happens:**
1. Resolves the thread on GitHub
2. Moves task file to `pr-102-tasks_completed/`

**When to resolve:**
- ✅ FIXED → Resolve the thread
- ❌ NOT_APPLICABLE → Don't resolve (explain in PR comment instead)
- ⚠️ ALREADY_FIXED → Resolve the thread

## Output Format

After evaluation, provide a brief summary:

```
## Result: [FIXED | NOT_APPLICABLE | ALREADY_FIXED]

**File:** path/to/file.ts
**Line:** 123
**Comment ID:** 2742327370

**Action taken:** [Description of fix OR reason why not applicable]

**Thread resolved:** [Yes | No | N/A]
```

## Important Guidelines

- Be concise - don't over-explain
- Only fix what the review mentions
- Don't make unrelated changes
- If the issue is already fixed, report as ALREADY_FIXED
- Check for "Also applies to:" lines - fix those too if valid
- **Always resolve the thread after FIXED or ALREADY_FIXED**
