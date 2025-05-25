@echo off
REM AutoMail Agent - Windows Setup Script
REM This script will set up the AutoMail Agent project and start the application

setlocal enabledelayedexpansion

REM Colors for output (using echo with special characters)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

echo.
echo %BLUE%🚀 AutoMail Agent Setup Script%NC%
echo ================================
echo.

REM Function to check if command exists
where python >nul 2>&1
if %errorlevel% neq 0 (
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo %RED%[ERROR]%NC% Python is not installed. Please install Python 3.8+ and try again.
        echo Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=python3"
    )
) else (
    set "PYTHON_CMD=python"
)

echo %BLUE%[INFO]%NC% Checking Python version...

REM Check Python version
for /f "tokens=*" %%i in ('%PYTHON_CMD% -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%i

REM Simple version check (assuming 3.8+ requirement)
if "%PYTHON_VERSION:~0,1%" lss "3" (
    echo %RED%[ERROR]%NC% Python 3.8 or higher is required. Found: %PYTHON_VERSION%
    pause
    exit /b 1
)

if "%PYTHON_VERSION:~0,3%" == "3.7" (
    echo %RED%[ERROR]%NC% Python 3.8 or higher is required. Found: %PYTHON_VERSION%
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Python %PYTHON_VERSION% found

REM Check if git is installed
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Git is not installed. Please install Git and try again.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% Git found

REM Check for browsers
echo %BLUE%[INFO]%NC% Checking for supported browsers...

set "CHROME_FOUND=false"
set "FIREFOX_FOUND=false"

REM Check for Chrome
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME_FOUND=true"
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME_FOUND=true"
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME_FOUND=true"

if "%CHROME_FOUND%"=="true" (
    echo %GREEN%[SUCCESS]%NC% Chrome browser found
)

REM Check for Firefox
if exist "%ProgramFiles%\Mozilla Firefox\firefox.exe" set "FIREFOX_FOUND=true"
if exist "%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe" set "FIREFOX_FOUND=true"

if "%FIREFOX_FOUND%"=="true" (
    echo %GREEN%[SUCCESS]%NC% Firefox browser found
)

if "%CHROME_FOUND%"=="false" if "%FIREFOX_FOUND%"=="false" (
    echo %YELLOW%[WARNING]%NC% No supported browsers found. Please install Chrome or Firefox.
    echo %YELLOW%[WARNING]%NC% The application will still start, but browser automation may not work.
)

echo.

REM Check if we're already in the project directory
if not exist "requirements.txt" (
    echo %BLUE%[INFO]%NC% Repository not found in current directory.
    set /p "REPO_URL=Enter the repository URL (or press Enter to skip cloning): "
    
    if not "!REPO_URL!"=="" (
        echo %BLUE%[INFO]%NC% Cloning repository...
        git clone "!REPO_URL!" automail-agent
        if %errorlevel% neq 0 (
            echo %RED%[ERROR]%NC% Failed to clone repository
            pause
            exit /b 1
        )
        cd automail-agent
        echo %GREEN%[SUCCESS]%NC% Repository cloned successfully
    ) else (
        echo %RED%[ERROR]%NC% No repository URL provided and requirements.txt not found in current directory.
        pause
        exit /b 1
    )
) else (
    echo %GREEN%[SUCCESS]%NC% Found existing project in current directory
)

REM Create virtual environment
echo %BLUE%[INFO]%NC% Creating Python virtual environment...
if exist "venv" (
    echo %YELLOW%[WARNING]%NC% Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

%PYTHON_CMD% -m venv venv
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Failed to create virtual environment
    pause
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% Virtual environment created

REM Activate virtual environment
echo %BLUE%[INFO]%NC% Activating virtual environment...
call venv\Scripts\activate.bat
echo %GREEN%[SUCCESS]%NC% Virtual environment activated

REM Upgrade pip
echo %BLUE%[INFO]%NC% Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo %BLUE%[INFO]%NC% Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Failed to install Python dependencies
    pause
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% Python dependencies installed

REM Install Playwright browsers
echo %BLUE%[INFO]%NC% Installing Playwright browsers (this may take a few minutes)...
playwright install
if %errorlevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% Playwright browser installation had issues, but continuing...
) else (
    echo %GREEN%[SUCCESS]%NC% Playwright browsers installed
)

REM Create a simple start script
echo %BLUE%[INFO]%NC% Creating start script...
(
echo @echo off
echo REM AutoMail Agent Start Script
echo.
echo REM Activate virtual environment
echo call venv\Scripts\activate.bat
echo.
echo REM Start the application
echo echo 🚀 Starting AutoMail Agent...
echo python src\main.py
echo.
echo pause
) > start.bat

echo %GREEN%[SUCCESS]%NC% Start script created (start.bat)

echo.
echo %GREEN%🎉 Setup completed successfully!%NC%
echo ================================
echo.
echo 📋 Next steps:
echo 1. Run the application:
echo    start.bat
echo.
echo    OR manually:
echo    venv\Scripts\activate.bat
echo    python src\main.py
echo.
echo 2. Open your browser and go to:
echo    🌐 Web Interface: http://localhost:8000
echo    📚 API Documentation: http://localhost:8000/api/docs
echo    🔍 Health Check: http://localhost:8000/health
echo.
echo 3. For email automation, make sure you're logged into Gmail in your browser
echo.

REM Ask if user wants to start the application now
set /p "START_NOW=Would you like to start the application now? (y/N): "

if /i "%START_NOW%"=="y" (
    echo.
    echo %BLUE%[INFO]%NC% Starting AutoMail Agent...
    python src\main.py
) else (
    echo.
    echo %GREEN%[SUCCESS]%NC% Setup complete! Run 'start.bat' when you're ready to start the application.
    pause
)

endlocal 