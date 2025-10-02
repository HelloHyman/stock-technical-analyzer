@echo off
echo =========================================
echo  Stock Analyzer - Windows Build Script
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

echo Step 1: Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r WindowsBuild\requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Building Windows executable...
cd WindowsBuild
pyinstaller --clean stock_analyzer.spec
cd ..

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo =========================================
echo  Build Complete!
echo =========================================
echo.
echo Your executable is located at:
echo   dist\StockAnalyzer.exe
echo.
echo You can now distribute this .exe file to users.
echo They can run it without installing Python!
echo.
pause


