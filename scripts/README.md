# Automation Scripts

All scripts to set up, run, and manage EST Backend services.

## Overview

- **setup.sh / setup.ps1** - Initial setup (venv, dependencies, databases, migrations)
- **run.sh / run.ps1 / run.bat** - Start both Auth and Catalog services
- **stop.sh** - Stop running services (Linux/macOS only)

## Quick Start

### Linux / macOS

```bash
cd ..
chmod +x scripts/setup.sh scripts/run.sh scripts/stop.sh
scripts/setup.sh
scripts/run.sh
```

### Windows PowerShell

```powershell
cd ..
.\scripts\setup.ps1
.\scripts\run.ps1
```

### Windows Command Prompt

```cmd
cd ..
scripts\run.bat
```

## Services

After running, access services at:

- **Auth Service**: http://localhost:8001/docs
- **Catalog Service**: http://localhost:8000/docs

## Scripts Detailed

### setup.sh (Linux/macOS)

```bash
scripts/setup.sh
```

**What it does**:
1. Creates Python virtual environment (.venv)
2. Installs dependencies from requirements.txt
3. Creates .env file from .env.example
4. Creates PostgreSQL databases (est_auth, est_catalog)
5. Runs Alembic migrations
6. Creates logs directory

**Requirements**:
- Python 3.10+
- PostgreSQL running
- pip

### setup.ps1 (Windows PowerShell)

```powershell
.\scripts\setup.ps1
```

Same as setup.sh but for Windows. Options:

```powershell
.\scripts\setup.ps1 -SkipVenv    # Skip venv creation
.\scripts\setup.ps1 -SkipDeps    # Skip dependency install
.\scripts\setup.ps1 -SkipDb      # Skip database setup
```

### run.sh (Linux/macOS)

```bash
scripts/run.sh
```

**What it does**:
1. Activates virtual environment
2. Starts Auth Service on port 8001
3. Starts Catalog Service on port 8000
4. Creates log files
5. Waits for Ctrl+C to stop

**Output**:
- Auth logs: logs/auth.log
- Catalog logs: logs/catalog.log
- Services run in background
- Ctrl+C to stop

### run.ps1 (Windows PowerShell)

```powershell
.\scripts\run.ps1
```

Same as run.sh but for Windows. Options:

```powershell
.\scripts\run.ps1 -NoReload    # Production mode (no auto-reload)
.\scripts\run.ps1 -Help        # Show help
```

### run.bat (Windows Command Prompt)

```cmd
scripts\run.bat
```

Starts both services in separate windows:
- Each service in its own Command Prompt window
- Close windows to stop services
- Auto-reload enabled

### stop.sh (Linux/macOS)

```bash
scripts/stop.sh
```

**What it does**:
1. Stops Auth Service
2. Stops Catalog Service
3. Cleans up PID files

**Note**: For Windows, close the service windows or use PowerShell:
```powershell
Get-Process python | Where-Object { $_.ProcessName -like "*uvicorn*" } | Stop-Process
```

## Common Tasks

### First Time Setup

**Linux/macOS**:
```bash
cd ..
chmod +x scripts/setup.sh scripts/run.sh scripts/stop.sh
scripts/setup.sh
scripts/run.sh
```

**Windows**:
```powershell
cd ..
.\scripts\setup.ps1
.\scripts\run.ps1
```

### View Logs

**Linux/macOS**:
```bash
tail -f logs/auth.log
tail -f logs/catalog.log
```

**Windows PowerShell**:
```powershell
Get-Content ../logs/auth.log -Tail 50 -Wait
```

### Check Service Health

```bash
curl http://localhost:8001/health
curl http://localhost:8000/health
```

### Stop Services

**Linux/macOS**:
```bash
scripts/stop.sh
```

**Windows**: Close the service windows or use:
```powershell
Get-Process python | Where-Object { $_.ProcessName -like "*uvicorn*" } | Stop-Process
```

### Reset Everything

**Linux/macOS**:
```bash
scripts/stop.sh
rm -rf ../.venv ../logs ../.pids
scripts/setup.sh
scripts/run.sh
```

**Windows**:
```powershell
Remove-Item -Recurse ..\venv, ..\logs -ErrorAction SilentlyContinue
.\setup.ps1
.\run.ps1
```

## Requirements

### System Requirements
- Python 3.10+
- PostgreSQL 13+
- Git
- Bash (Linux/macOS) or PowerShell/Command Prompt (Windows)

### Python Packages
All installed via `pip install -r requirements.txt`:
- fastapi
- uvicorn
- sqlalchemy
- alembic
- pydantic
- bcrypt
- pyjwt
- httpx

### Environment Configuration
Edit `.env` file after setup:

```ini
AUTH_DATABASE_URL=postgresql://postgres:password@localhost:5432/est_auth
CATALOG_DATABASE_URL=postgresql://postgres:password@localhost:5432/est_catalog
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
SMTP_HOST=localhost
SMTP_PORT=1025
AUTH_SERVICE_URL=http://localhost:8001
CATALOG_SERVICE_URL=http://localhost:8000
ENV=dev
```

## Troubleshooting

### Virtual Environment Not Found

**Linux/macOS**:
```bash
python3 -m venv ../.venv
source ../.venv/bin/activate
```

**Windows**:
```powershell
python -m venv ..\venv
..\venv\Scripts\Activate.ps1
```

### PostgreSQL Not Running

**macOS**:
```bash
brew services start postgresql
```

**Ubuntu/Debian**:
```bash
sudo systemctl start postgresql
```

**Windows**: Use Services app or pgAdmin

### Port Already in Use

```bash
# Find process
lsof -i :8000
lsof -i :8001

# Kill process
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Dependencies Missing

```bash
pip install -r requirements.txt
```

### Database Connection Error

1. Check PostgreSQL is running
2. Verify database URLs in .env file
3. Make sure databases exist:
   ```bash
   psql -U postgres -c "CREATE DATABASE est_auth;"
   psql -U postgres -c "CREATE DATABASE est_catalog;"
   ```

### Migrations Failed

```bash
# Check alembic config
alembic current
alembic -c alembic_auth.ini current

# Rerun migrations
alembic upgrade head
alembic -c alembic_auth.ini upgrade head
```

### Permission Denied (Linux/macOS)

```bash
chmod +x setup.sh run.sh stop.sh
```

## Directory Structure

```
est-backend/
├── scripts/                  ← You are here
│   ├── README.md            ← This file
│   ├── setup.sh
│   ├── run.sh
│   ├── stop.sh
│   ├── setup.ps1
│   ├── run.ps1
│   └── run.bat
│
├── docs/                    ← Documentation
├── services/                ← Source code
└── [other files]
```

## Advanced Usage

### Production Deployment

```powershell
# No auto-reload
.\scripts\run.ps1 -NoReload

# Or on Linux/macOS, edit run.sh:
# Remove --reload flag from uvicorn commands
```

### Custom Ports

Edit the script and change port numbers:

```bash
# run.sh
uvicorn services.auth.src.main:app --port 9001      # Change 8001 to 9001
uvicorn services.catalog.src.main:app --port 9000   # Change 8000 to 9000
```

### Multiple Instances

Run services on different machines with shared database:

```bash
# Machine 1: Auth Service
.\scripts\run.ps1 -NoReload

# Machine 2: Catalog Service (update DATABASE_URL in .env)
.\scripts\run.ps1 -NoReload
```

### View All Logs

**Linux/macOS**:
```bash
logs/auth.log           # Auth service output
logs/catalog.log        # Catalog service output
```

**Find errors**:
```bash
grep ERROR logs/auth.log
grep ERROR logs/catalog.log
```

---

For full documentation, see `../docs/GETTING_STARTED.md`
