@echo off
REM ===================================================================
REM Stock Analyzer - Build Script for Windows
REM This script builds the .exe file using PyInstaller
REM ===================================================================

echo ====================================
echo Stock Analyzer - Build Script
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Checking Python installation... OK
echo.

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo [2/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo [2/5] Virtual environment already exists... OK
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

REM Install dependencies
echo [4/5] Installing dependencies...
echo This may take a few minutes...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Build executable
echo [5/5] Building executable...
echo This may take several minutes...
pyinstaller --clean stock_analyzer.spec
if errorlevel 1 (
    echo ERROR: Failed to build executable
    pause
    exit /b 1
)

echo.
echo ====================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ====================================
echo.
echo Your executable is located at:
echo dist\StockAnalyzer.exe
echo.
echo File size: 
for %%A in (dist\StockAnalyzer.exe) do echo %%~zA bytes
echo.
echo Next steps:
echo 1. Test the executable: dist\StockAnalyzer.exe
echo 2. (Optional) Sign the executable - see SIGNING_GUIDE.md
echo 3. Distribute to users
echo.
pause

