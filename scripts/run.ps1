# EST Backend - Run Both Services (Windows PowerShell)
# This script starts both Auth and Catalog services in new PowerShell windows

$ErrorActionPreference = "Continue"

# Get project root directory (one level up from scripts)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host ""
Write-Host "==============================================================="
Write-Host "   EST Backend - Starting Services"
Write-Host "==============================================================="
Write-Host ""
Write-Host "Project root: $ProjectRoot"
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "$ProjectRoot\.venv")) {
    Write-Host "Virtual environment not found. Creating..."
    python -m venv "$ProjectRoot\.venv"
    Write-Host "Virtual environment created."
}

# Check if .env exists
if (-not (Test-Path "$ProjectRoot\.env")) {
    Write-Host "ERROR: .env file not found. Please create one before running."
    Write-Host "You can use .env.example as a template."
    exit 1
}

# Create logs directory
if (-not (Test-Path "$ProjectRoot\logs")) {
    New-Item -ItemType Directory -Path "$ProjectRoot\logs" | Out-Null
}

Write-Host ""
Write-Host "Installing dependencies..."
& "$ProjectRoot\.venv\Scripts\pip.exe" install -q -r "$ProjectRoot\requirements.txt"

Write-Host ""
Write-Host "Starting Auth Service on port 8001..."
$AuthCmd = "cd '$ProjectRoot'; & '.\venv\Scripts\Activate.ps1'; python -m uvicorn services.auth.src.main:app --host 0.0.0.0 --port 8001 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $AuthCmd -WindowStyle Normal
Start-Sleep -Seconds 3

Write-Host "Starting Catalog Service on port 8000..."
$CatalogCmd = "cd '$ProjectRoot'; & '.\venv\Scripts\Activate.ps1'; python -m uvicorn services.catalog.src.main:app --host 0.0.0.0 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $CatalogCmd -WindowStyle Normal
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "==============================================================="
Write-Host "Services are starting in separate windows!"
Write-Host "==============================================================="
Write-Host ""
Write-Host "Auth Service:     http://localhost:8001/docs"
Write-Host "Catalog Service:  http://localhost:8000/docs"
Write-Host ""
Write-Host "Close the service windows to stop them."
Write-Host ""
$CatalogProcess.WaitForExit()
