## Task

Evaluate this code review comment. Read the source file and determine if the issue is valid.

**Instructions:**
1. Read the file mentioned in the review: `.github/workflows/on-merge.yml`
2. Check line 299 and surrounding context
3. Determine if the review feedback is valid
4. If valid: Fix the issue in the code
5. If invalid: Explain why the feedback doesn't apply

**Important:** Be concise. Either fix the code or explain in 2-3 sentences why it's not applicable.

---

# Review Comment

- **Author:** coderabbitai[bot]
- **File:** `.github/workflows/on-merge.yml`
- **Line:** 299
- **Date:** 2026-02-07
- **Comment ID:** 2777129363
- **URL:** https://github.com/donghaozhang/video-agent-skill/pull/20#discussion_r2777129363

---

_⚠️ Potential issue_ | _🟠 Major_

**Script injection risk with untrusted PR title in release notes.**

The PR title is interpolated directly into the inline script via `${{ github.event.pull_request.title }}`. A malicious PR title containing shell metacharacters could break the script or execute unintended commands. Pass it through an environment variable instead.
