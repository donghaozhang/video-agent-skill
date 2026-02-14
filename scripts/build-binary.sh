#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SCRIPT_DIR/.venv"
DIST_DIR="$SCRIPT_DIR/dist"

echo "[build] Building aicp standalone binary"
echo "[build] Repo: $REPO_DIR"

# Require Python 3.10+
PYTHON="${PYTHON:-python3}"
PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[build] Using Python $PY_VERSION ($("$PYTHON" --version 2>&1))"

IFS='.' read -r PY_MAJOR PY_MINOR <<< "$PY_VERSION"
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo "[build] ERROR: Python >= 3.10 required, got $PY_VERSION"
    exit 1
fi

# Create isolated venv
echo "[build] Creating virtual environment at $VENV_DIR"
"$PYTHON" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install the package + pyinstaller
echo "[build] Installing package and PyInstaller"
pip install --upgrade pip
pip install -e "$REPO_DIR"
pip install pyinstaller

# Build standalone binary using spec at repo root
echo "[build] Running PyInstaller"
pyinstaller "$REPO_DIR/aicp.spec" \
    --distpath "$DIST_DIR" \
    --workpath "$SCRIPT_DIR/build-temp" \
    --clean

# Verify the binary works
echo "[build] Verifying binary"
"$DIST_DIR/aicp" --version
"$DIST_DIR/aicp" --json list-models > /dev/null

# Report
PLATFORM="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"
[ "$ARCH" = "x86_64" ] && ARCH="x64"
[ "$ARCH" = "aarch64" ] && ARCH="arm64"

BINARY_BYTES=$(wc -c < "$DIST_DIR/aicp" | tr -d ' ')
BINARY_SIZE_MB=$(awk "BEGIN {printf \"%.1f\", $BINARY_BYTES / 1048576}")
if command -v sha256sum >/dev/null; then
    BINARY_SHA256=$(sha256sum "$DIST_DIR/aicp" | cut -d' ' -f1)
else
    BINARY_SHA256=$(shasum -a 256 "$DIST_DIR/aicp" | cut -d' ' -f1)
fi

echo ""
echo "========================================"
echo "Build complete!"
echo "Binary:   $DIST_DIR/aicp"
echo "Platform: $PLATFORM-$ARCH"
echo "Size:     ${BINARY_SIZE_MB}MB ($BINARY_BYTES bytes)"
echo "SHA256:   $BINARY_SHA256"
echo "========================================"
