@echo off
echo =========================================
echo  Stock Analyzer - Running from Source
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Installing/Updating dependencies...
python -m pip install -r WindowsBuild\requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting Stock Analyzer...
echo.
cd ..
python manual_stock_analyzer.py
cd WindowsBuild

pause


