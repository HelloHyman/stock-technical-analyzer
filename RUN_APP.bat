@echo off
title Stock and Crypto Analyzer
color 0B

echo.
echo ================================================================
echo    Stock and Crypto Automated Analysis Tool
echo ================================================================
echo.
echo Starting the application...
echo.

REM Try to run the Python script directly
python main.py

REM If that fails, show error message
if errorlevel 1 (
    echo.
    echo ================================================================
    echo ERROR: Could not start the application
    echo ================================================================
    echo.
    echo Possible solutions:
    echo 1. Make sure Python is installed
    echo 2. Install dependencies: pip install -r requirements.txt
    echo 3. Try running: BUILD_EXE.bat to create an executable
    echo.
    echo Press any key to exit...
    pause >nul
)
