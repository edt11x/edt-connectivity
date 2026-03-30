# setup.ps1 — Create and populate the Python venv (Windows PowerShell)
# Run with: powershell -ExecutionPolicy Bypass -File setup.ps1

param(
    [string]$Python = "python"
)

$VenvDir = ".venv"
$ErrorActionPreference = "Stop"

Write-Host "=== EDT Connectivity Checker — Environment Setup ===" -ForegroundColor Cyan

# Verify Python is available
try {
    $pyVer = & $Python --version 2>&1
}
catch {
    Write-Host "ERROR: '$Python' not found. Install Python 3.10+ and add it to PATH." -ForegroundColor Red
    exit 1
}
Write-Host "  Python  : $pyVer"

# Create venv if it does not already exist
if (-not (Test-Path $VenvDir)) {
    Write-Host "  Creating venv in $VenvDir\ ..."
    & $Python -m venv $VenvDir
}
else {
    Write-Host "  Venv already exists at $VenvDir\ — skipping creation."
}

# Activate and install dependencies
$activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Host "ERROR: Activation script not found at $activateScript" -ForegroundColor Red
    exit 1
}
. $activateScript

Write-Host "  Upgrading pip ..."
& python -m pip install --quiet --upgrade pip

Write-Host "  Installing dependencies from requirements.txt ..."
& pip install --quiet -r requirements.txt

Write-Host ""
Write-Host "Setup complete. To run the checker:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python check_connectivity.py"
Write-Host ""
