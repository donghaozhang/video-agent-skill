# Phase 1: Submodule & SDK Setup

**Created:** 2026-01-28
**Branch:** `feature/kimi-cli-integration`
**Status:** Pending
**Estimated Effort:** 1-2 hours

---

## Objective

Add kimi-cli as a git submodule and set up the Kimi SDK for programmatic access.

---

## Subtasks

### 1.1 Add Git Submodule

```bash
# Create external packages directory
mkdir -p packages/external

# Add kimi-cli as submodule
git submodule add https://github.com/MoonshotAI/kimi-cli.git packages/external/kimi-cli

# Initialize submodule
git submodule update --init --recursive
```

**Expected Result:**
```
packages/
└── external/
    └── kimi-cli/
        ├── sdks/kimi-sdk/
        ├── src/kimi_cli/
        └── ...
```

---

### 1.2 Update .gitmodules

Verify `.gitmodules` contains:
```ini
[submodule "packages/external/kimi-cli"]
    path = packages/external/kimi-cli
    url = https://github.com/MoonshotAI/kimi-cli.git
    branch = main
```

---

### 1.3 Install Kimi SDK

**Option A: Install from PyPI (Recommended)**
```bash
pip install kimi-sdk>=1.2.0
```

**Option B: Install from Submodule**
```bash
pip install -e packages/external/kimi-cli/sdks/kimi-sdk
```

---

### 1.4 Update requirements.txt

Add to `requirements.txt`:
```txt
# Kimi SDK for AI agent integration
kimi-sdk>=1.2.0
```

---

### 1.5 Update .env

Add to `.env.example` and document:
```bash
# Kimi API Configuration (get key from moonshot.cn)
KIMI_API_KEY=your_kimi_api_key_here
# Optional: Custom API endpoint
# KIMI_BASE_URL=https://api.moonshot.cn
```

---

### 1.6 Verify Installation

Create test script `scripts/verify_kimi_sdk.py`:
```python
#!/usr/bin/env python3
"""Verify Kimi SDK installation."""

import os
import sys

def verify_installation():
    """Check if Kimi SDK is properly installed."""
    print("Verifying Kimi SDK installation...")

    # Check import
    try:
        from kimi_sdk import Kimi, Message
        print("✓ kimi_sdk module imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import kimi_sdk: {e}")
        print("  Run: pip install kimi-sdk")
        return False

    # Check API key
    api_key = os.getenv("KIMI_API_KEY")
    if api_key:
        print("✓ KIMI_API_KEY environment variable is set")
    else:
        print("⚠ KIMI_API_KEY not set (required for API calls)")

    # Check version
    try:
        import kimi_sdk
        version = getattr(kimi_sdk, "__version__", "unknown")
        print(f"✓ Kimi SDK version: {version}")
    except Exception:
        print("⚠ Could not determine SDK version")

    print("\nInstallation verified successfully!")
    return True

if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)
```

Run verification:
```bash
python scripts/verify_kimi_sdk.py
```

---

### 1.7 Create Integration Directory Structure

```bash
mkdir -p packages/core/ai_content_pipeline/ai_content_pipeline/integrations/kimi
touch packages/core/ai_content_pipeline/ai_content_pipeline/integrations/__init__.py
touch packages/core/ai_content_pipeline/ai_content_pipeline/integrations/kimi/__init__.py
```

**Create `integrations/__init__.py`:**
```python
"""External integrations for AI Content Pipeline."""

from .kimi import KimiIntegration

__all__ = ["KimiIntegration"]
```

**Create `integrations/kimi/__init__.py`:**
```python
"""Kimi SDK integration for AI Content Pipeline."""

from .client import KimiClient, KimiIntegration

__all__ = ["KimiClient", "KimiIntegration"]
```

---

## Commit Checkpoint

After completing all subtasks:
```bash
git add .
git commit -m "feat: Add kimi-cli submodule and SDK setup"
git push origin feature/kimi-cli-integration
```

---

## Verification Checklist

- [ ] Submodule added successfully
- [ ] `.gitmodules` updated
- [ ] `kimi-sdk` installed via pip
- [ ] `requirements.txt` updated
- [ ] `.env.example` updated with KIMI_API_KEY
- [ ] Verification script passes
- [ ] Integration directory structure created
- [ ] Changes committed

---

## Troubleshooting

### Submodule Issues
```bash
# If submodule is empty after clone
git submodule update --init --recursive

# If you need to remove and re-add
git submodule deinit -f packages/external/kimi-cli
git rm -f packages/external/kimi-cli
rm -rf .git/modules/packages/external/kimi-cli
```

### SDK Installation Issues
```bash
# If pip install fails, try with specific Python version
python3.12 -m pip install kimi-sdk

# Or install from source
pip install git+https://github.com/MoonshotAI/kimi-cli.git#subdirectory=sdks/kimi-sdk
```

### Import Errors
```python
# If import fails, check Python path
import sys
print(sys.path)

# Add to path if needed
sys.path.insert(0, 'packages/external/kimi-cli/sdks/kimi-sdk')
```
