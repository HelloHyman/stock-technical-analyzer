@echo off
REM ===================================================================
REM Stock Analyzer - Dependency Installation Script
REM This script installs all required dependencies for end users
REM ===================================================================

echo ====================================
echo Stock Analyzer - Setup Wizard
echo ====================================
echo.
echo This script will install all required dependencies
echo to run Stock Analyzer from Python.
echo.

REM Check Python installation
echo [Step 1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %PYTHON_VERSION% detected
echo.

REM Check pip
echo [Step 2/3] Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)
echo pip is available
echo.

REM Upgrade pip
echo Upgrading pip to latest version...
python -m pip install --upgrade pip --quiet
echo.

REM Install dependencies
echo [Step 3/3] Installing dependencies...
echo This may take a few minutes depending on your internet connection.
echo.

set /p CONFIRM="Ready to install? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Installation cancelled.
    pause
    exit /b 0
)

echo.
echo Installing packages...
echo.

REM Install each package with progress
echo [1/5] Installing pandas...
python -m pip install pandas>=2.0.0
if errorlevel 1 goto :error

echo [2/5] Installing numpy...
python -m pip install numpy>=1.24.0
if errorlevel 1 goto :error

echo [3/5] Installing yfinance...
python -m pip install yfinance>=0.2.28
if errorlevel 1 goto :error

echo [4/5] Installing matplotlib...
python -m pip install matplotlib>=3.7.0
if errorlevel 1 goto :error

echo [5/5] Installing mplfinance...
python -m pip install mplfinance>=0.12.9
if errorlevel 1 goto :error

echo.
echo ====================================
echo INSTALLATION COMPLETED SUCCESSFULLY!
echo ====================================
echo.

REM Verify installation
echo Verifying installation...
python -c "import pandas, numpy, yfinance, matplotlib, mplfinance" 2>nul
if errorlevel 1 (
    echo.
    echo WARNING: Some packages may not have installed correctly.
    echo Please run check_dependencies.bat to verify.
    echo.
) else (
    echo All packages verified successfully!
    echo.
)

echo You can now run Stock Analyzer:
echo python manual_stock_analyzer.py
echo.
echo Or run check_dependencies.bat to verify all installations.
echo.
pause
exit /b 0

:error
echo.
echo ====================================
echo INSTALLATION FAILED
echo ====================================
echo.
echo There was an error installing dependencies.
echo.
echo Common solutions:
echo 1. Check your internet connection
echo 2. Run as Administrator
echo 3. Try installing manually: pip install -r requirements.txt
echo 4. Check if antivirus is blocking pip
echo.
pause
exit /b 1

