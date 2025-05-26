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

echo [INFO] Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [SUCCESS] Python dependencies installed

REM Set up basic permissions
echo [INFO] Setting up permissions...
if not exist "data" mkdir data >nul 2>&1
if not exist "logs" mkdir logs >nul 2>&1
icacls . /grant %USERNAME%:F >nul 2>&1
echo [SUCCESS] Permissions configured

REM Create simple start script
(
echo @echo off
echo call venv\Scripts\activate.bat
echo python -m main
) > start.bat

echo [SUCCESS] Setup complete!
echo Run: start.bat or python -m main (after activating venv)
pause

endlocal 