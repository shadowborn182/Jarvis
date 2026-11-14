@echo off
title JARVIS Discord Bot - Developed by Shadow
echo ============================================
echo   Starting JARVIS Discord Management Bot
echo ============================================

if not exist ".venv\Scripts\activate.bat" (
    echo Creating Python virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo Running database migrations...
alembic upgrade head

echo Launching JARVIS...
python bot.py
pause
