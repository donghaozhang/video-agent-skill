## Task

Evaluate this code review comment. Read the source file and determine if the issue is valid.

**Instructions:**
1. Read the file mentioned in the review: `.github/workflows/publish-check.yml`
2. Check line 41 and surrounding context
3. Determine if the review feedback is valid
4. If valid: Fix the issue in the code
5. If invalid: Explain why the feedback doesn't apply

**Important:** Be concise. Either fix the code or explain in 2-3 sentences why it's not applicable.

---

# Review Comment

- **Author:** coderabbitai[bot]
- **File:** `.github/workflows/publish-check.yml`
- **Line:** 41
- **Date:** 2026-02-07
- **Comment ID:** 2777124694
- **URL:** https://github.com/donghaozhang/video-agent-skill/pull/20#discussion_r2777124694

---

_⚠️ Potential issue_ | _🔴 Critical_

**Fix Python `-c` quoting that breaks version extraction.**

Line 36’s inline Python uses nested quotes that trigger a SyntaxError (matches the pipeline failure). Use a heredoc to avoid shell-escaping issues.
