@echo off
REM EST Backend - Run Both Services (Windows Command Prompt)
REM This script starts both Auth and Catalog services

setlocal enabledelayedexpansion

REM Get project root directory (one level up from scripts)
set SCRIPT_DIR=%~dp0
for %%A in ("%SCRIPT_DIR%..") do set PROJECT_ROOT=%%~fA
cd /d "%PROJECT_ROOT%"

echo.
echo ===============================================================
echo   EST Backend - Starting Services
echo ===============================================================
echo.
echo Project root: %PROJECT_ROOT%
echo.

REM Check if virtual environment exists
if not exist "%PROJECT_ROOT%\.venv" (
    echo Virtual environment not found. Creating...
    python -m venv "%PROJECT_ROOT%\.venv"
    echo Virtual environment created.
)

REM Check if .env exists
if not exist "%PROJECT_ROOT%\.env" (
    echo .env file not found. Please create one before running.
    echo You can use .env.example as a template.
    exit /b 1
)

REM Create logs directory
if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"

echo.
echo Installing dependencies...
call "%PROJECT_ROOT%\.venv\Scripts\pip.exe" install -q -r "%PROJECT_ROOT%\requirements.txt"

echo.
echo Starting Auth Service on port 8001...
start "EST Auth Service" cmd /k "cd /d "%PROJECT_ROOT%" && call .venv\Scripts\activate.bat && python -m uvicorn services.auth.src.main:app --host 0.0.0.0 --port 8001 --reload"

timeout /t 3 /nobreak

echo Starting Catalog Service on port 8000...
start "EST Catalog Service" cmd /k "cd /d "%PROJECT_ROOT%" && call .venv\Scripts\activate.bat && python -m uvicorn services.catalog.src.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak

echo.
echo ===============================================================
echo Services are starting in separate windows!
echo ===============================================================
echo.
echo Auth Service:     http://localhost:8001/docs
echo Catalog Service:  http://localhost:8000/docs
echo.
echo Close the service windows to stop them.
echo.

pause
