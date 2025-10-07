@echo off
title Stock and Crypto Analyzer - Build Executable
color 0A

echo.
echo ================================================================
echo    Stock and Crypto Automated Analysis - Build Executable
echo ================================================================
echo.
echo This script will automatically:
echo 1. Check Python installation
echo 2. Install all required dependencies
echo 3. Build a standalone Windows executable
echo.
echo Press any key to start the build process...
pause >nul

echo.
echo Starting build process...
echo.

REM Run the Python build script
python build_exe.py

echo.
echo ================================================================
echo Build process completed!
echo ================================================================
echo.
echo Your executable should be in: dist\StockCryptoAnalyzer\
echo.
echo Press any key to exit...
pause >nul
