# EST Backend - Setup Script (PowerShell)
# Automates initial setup: venv, dependencies, databases, migrations

param(
    [switch]$SkipVenv = $false,
    [switch]$SkipDeps = $false,
    [switch]$SkipDb = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "EST Backend - Setup Script"
    Write-Host ""
    Write-Host "Usage: .\setup.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -SkipVenv   Skip virtual environment setup"
    Write-Host "  -SkipDeps   Skip dependency installation"
    Write-Host "  -SkipDb     Skip database and migration setup"
    Write-Host "  -Help       Show this help message"
    Write-Host ""
    exit 0
}

$ErrorActionPreference = "Stop"

# Get project directory
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

# Colors
$Green = "`e[32m"
$Blue = "`e[34m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Reset = "`e[0m"

Write-Host ""
Write-Host "${Blue}═══════════════════════════════════════════════════════${Reset}"
Write-Host "${Blue}  EST Backend - Setup Script${Reset}"
Write-Host "${Blue}═══════════════════════════════════════════════════════${Reset}"
Write-Host ""

# Step 1: Create virtual environment
if (-not $SkipVenv) {
    Write-Host "${Blue}Step 1: Setting up Python virtual environment...${Reset}"
    if (Test-Path ".venv") {
        Write-Host "${Green}✓ Virtual environment already exists${Reset}"
    }
    else {
        python -m venv .venv
        Write-Host "${Green}✓ Virtual environment created${Reset}"
    }
}

# Activate virtual environment
& .\`.venv\Scripts\Activate.ps1

# Step 2: Install dependencies
if (-not $SkipDeps) {
    Write-Host ""
    Write-Host "${Blue}Step 2: Installing dependencies...${Reset}"
    pip install -q -r requirements.txt
    Write-Host "${Green}✓ Dependencies installed${Reset}"
}

# Step 3: Setup .env file
Write-Host ""
Write-Host "${Blue}Step 3: Setting up .env file...${Reset}"
if (Test-Path ".env") {
    Write-Host "${Green}✓ .env file already exists${Reset}"
}
else {
    Copy-Item .env.example .env
    Write-Host "${Green}✓ .env file created from template${Reset}"
    Write-Host "${Yellow}⚠ Please update .env file with your database URLs${Reset}"
}

# Step 4: Create logs directory
Write-Host ""
Write-Host "${Blue}Step 4: Creating logs directory...${Reset}"
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}
Write-Host "${Green}✓ Logs directory created${Reset}"

# Step 5: Run migrations (if databases are configured)
if (-not $SkipDb) {
    Write-Host ""
    Write-Host "${Blue}Step 5: Running database migrations...${Reset}"

    # Try to run migrations
    try {
        alembic upgrade head 2>$null
        Write-Host "${Green}✓ Catalog migrations applied${Reset}"
    }
    catch {
        Write-Host "${Yellow}⚠ Catalog migrations failed (database may not be set up)${Reset}"
    }

    try {
        alembic -c alembic_auth.ini upgrade head 2>$null
        Write-Host "${Green}✓ Auth migrations applied${Reset}"
    }
    catch {
        Write-Host "${Yellow}⚠ Auth migrations failed (database may not be set up)${Reset}"
    }
}

Write-Host ""
Write-Host "${Blue}═══════════════════════════════════════════════════════${Reset}"
Write-Host "${Green}✓ Setup complete!${Reset}"
Write-Host "${Blue}═══════════════════════════════════════════════════════${Reset}"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Update .env file if needed"
Write-Host "  2. Run: .\run.ps1 (PowerShell) or run.bat (Command Prompt)"
Write-Host "  3. Visit: http://localhost:8001/docs and http://localhost:8000/docs"
Write-Host ""
