# JARVIS Windows PowerShell Startup Script
# Developer: Shadow

$ErrorActionPreference = "Stop"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  JARVIS - Advanced Discord Management Bot  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    & .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
} else {
    & .\.venv\Scripts\Activate.ps1
}

Write-Host "Applying Alembic database migrations..." -ForegroundColor Yellow
alembic upgrade head

Write-Host "Launching JARVIS..." -ForegroundColor Green
python bot.py
