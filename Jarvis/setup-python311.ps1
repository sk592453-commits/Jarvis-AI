# PowerShell script to set up Python 3.11 for Jarvis

Write-Host ""
Write-Host "========================================"
Write-Host "  JARVIS - PYTHON 3.11 SETUP"
Write-Host "========================================"
Write-Host ""

Write-Host "[1/5] Checking for active virtual environment..."
if ($env:VIRTUAL_ENV) {
    Write-Host "Deactivating current environment..."
    deactivate
}

Write-Host ""
Write-Host "[2/5] Removing old .venv directory..."
if (Test-Path ".\jarvis\.venv") {
    Remove-Item -Recurse -Force ".\jarvis\.venv"
    Write-Host "Old environment removed"
}

Write-Host ""
Write-Host "[3/5] Checking for Python 3.11..."
$pythonCheck = & py -3.11 --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python 3.11 not found. Download from:"
    Write-Host "https://www.python.org/downloads/release/python-31116/"
    exit 1
}
Write-Host "Found: $pythonCheck"

Write-Host ""
Write-Host "[4/5] Creating new .venv with Python 3.11..."
& py -3.11 -m venv jarvis\.venv

Write-Host ""
Write-Host "[5/5] Installing requirements..."
& .\jarvis\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "========================================"
Write-Host "  PYTHON 3.11 SETUP COMPLETE"
Write-Host "========================================"
Write-Host ""
python --version
Write-Host ""
