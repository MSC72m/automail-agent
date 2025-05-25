@echo off
REM AutoMail Agent - Simple Setup Script

setlocal enabledelayedexpansion

REM Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed. Please install Python 3.8+ and try again.
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=python3"
    )
) else (
    set "PYTHON_CMD=python"
)

echo [SUCCESS] Python found

REM Check if we're in project directory
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found. Please run this script from the project directory.
    pause
    exit /b 1
)

echo [INFO] Setting up virtual environment...
if exist "venv" (
    rmdir /s /q venv
)

%PYTHON_CMD% -m venv venv
call venv\Scripts\activate.bat
echo [SUCCESS] Virtual environment created

echo [INFO] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [SUCCESS] Dependencies installed

REM Create start script
(
echo @echo off
echo call venv\Scripts\activate.bat
echo python src\main.py
echo pause
) > start.bat

echo.
echo [SUCCESS] Setup complete!
echo Run: start.bat
echo API: http://localhost:8000

REM Ask to start now
set /p "START_NOW=Start now? (y/N): "

if /i "%START_NOW%"=="y" (
    python src\main.py
) else (
    pause
)

endlocal 