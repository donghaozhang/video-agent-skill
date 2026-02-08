# Setup TestPyPI Token for Publish Check CI

## Status: Pending

## Problem

The `Publish Check (TestPyPI)` workflow uses `continue-on-error` on the upload step because the `TEST_PYPI_API_TOKEN` secret is not configured. The build and twine check steps still validate the package, but the actual upload to TestPyPI and install verification are skipped.

## Steps to Add the Token

1. **Create a TestPyPI account** (if you don't have one)
   - Go to https://test.pypi.org/account/register/
   - TestPyPI is separate from PyPI -- your existing PyPI account does NOT work here

2. **Generate an API token**
   - Go to https://test.pypi.org/manage/account/token/
   - Token name: `github-actions-publish-check` (or any descriptive name)
   - Scope: `Entire account` (or scope to `video-ai-studio` if the project already exists on TestPyPI)
   - Copy the token (starts with `pypi-`)

3. **Add the token to GitHub repo secrets**
   - Go to your repo: https://github.com/donghaozhang/video-agent-skill/settings/secrets/actions
   - Click **New repository secret**
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: paste the token from step 2
   - Click **Add secret**

4. **Verify it works**
   - Push a commit or re-run the `Publish Check (TestPyPI)` workflow
   - The upload step should now succeed and the install verification step will run

## Important Notes

- **PyPI and TestPyPI are completely separate registries** with separate accounts, tokens, and packages
- Your existing `PYPI_API_TOKEN` (for real PyPI) will NOT work for TestPyPI
- The `continue-on-error` on the upload step can be removed once the token is configured (optional -- it's harmless to keep)

## Relevant Files

- Workflow: `.github/workflows/publish-check.yml`
- Token secret name: `TEST_PYPI_API_TOKEN` (line 67)
