# PowerShell build script for aicp standalone binary (Windows)
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoDir = Split-Path -Parent $ScriptDir
$VenvDir = Join-Path $ScriptDir ".venv"
$DistDir = Join-Path $ScriptDir "dist"

Write-Host "[build] Building aicp standalone binary"
Write-Host "[build] Repo: $RepoDir"

# Use python from PATH or PYTHON env var
$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
$PyVersion = & $Python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "[build] Using Python $PyVersion"

$versionParts = $PyVersion.Split('.')
$PyMajor = [int]$versionParts[0]
$PyMinor = [int]$versionParts[1]
if ([int]$PyMajor -lt 3 -or ([int]$PyMajor -eq 3 -and [int]$PyMinor -lt 10)) {
    Write-Error "[build] ERROR: Python >= 3.10 required, got $PyVersion"
    exit 1
}

# Create isolated venv
Write-Host "[build] Creating virtual environment at $VenvDir"
& $Python -m venv $VenvDir
if ($LASTEXITCODE -ne 0) { throw "[build] ERROR: venv creation failed" }
. "$VenvDir\Scripts\Activate.ps1"

# Install the package + pyinstaller
Write-Host "[build] Installing package and PyInstaller"
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "[build] ERROR: pip upgrade failed" }
python -m pip install -e "$RepoDir"
if ($LASTEXITCODE -ne 0) { throw "[build] ERROR: package install failed" }
python -m pip install pyinstaller
if ($LASTEXITCODE -ne 0) { throw "[build] ERROR: PyInstaller install failed" }

# Build standalone binary using spec at repo root
Write-Host "[build] Running PyInstaller"
python -m PyInstaller "$RepoDir\aicp.spec" `
    --distpath $DistDir `
    --workpath "$ScriptDir\build-temp" `
    --clean
if ($LASTEXITCODE -ne 0) { throw "[build] ERROR: PyInstaller build failed" }

# Verify the binary works
Write-Host "[build] Verifying binary"
& "$DistDir\aicp.exe" --version
if ($LASTEXITCODE -ne 0) {
    throw "[build] ERROR: aicp --version failed"
}

$null = & "$DistDir\aicp.exe" --json list-models
if ($LASTEXITCODE -ne 0) {
    throw "[build] ERROR: aicp list-models failed"
}

# Report
$BinaryPath = Join-Path $DistDir "aicp.exe"
$BinarySize = (Get-Item $BinaryPath).Length
$BinarySizeMB = [math]::Round($BinarySize / 1MB, 1)
$BinarySha256 = (Get-FileHash -Algorithm SHA256 $BinaryPath).Hash.ToLower()

Write-Host ""
Write-Host "========================================"
Write-Host "Build complete!"
Write-Host "Binary:   $BinaryPath"
Write-Host "Platform: windows-x64"
Write-Host "Size:     ${BinarySizeMB}MB ($BinarySize bytes)"
Write-Host "SHA256:   $BinarySha256"
Write-Host "========================================"
