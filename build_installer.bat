@echo off
REM ===================================================================
REM Stock Analyzer - Complete Installer Build Script
REM This script builds the .exe AND creates a professional installer
REM ===================================================================

echo ====================================
echo Stock Analyzer - Installer Builder
echo ====================================
echo.

REM Step 1: Build the executable first
echo [Step 1/2] Building executable...
echo.

if not exist "dist\StockAnalyzer.exe" (
    echo Executable not found. Building now...
    call build_exe.bat
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to build executable
        pause
        exit /b 1
    )
) else (
    echo Executable already exists: dist\StockAnalyzer.exe
    set /p REBUILD="Rebuild executable? (Y/N): "
    if /i "%REBUILD%"=="Y" (
        call build_exe.bat
        if errorlevel 1 (
            echo ERROR: Failed to build executable
            pause
            exit /b 1
        )
    )
)

echo.
echo ====================================
echo [Step 2/2] Creating Installer
echo ====================================
echo.

REM Check if Inno Setup is installed
set INNO_SETUP=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set INNO_SETUP="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    goto :found_inno
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set INNO_SETUP="C:\Program Files\Inno Setup 6\ISCC.exe"
    goto :found_inno
)

REM Inno Setup not found
echo ERROR: Inno Setup not found!
echo.
echo Please install Inno Setup (free) from:
echo https://jrsoftware.org/isdl.php
echo.
echo Download: innosetup-6.x.x.exe
echo Install with default settings
echo Then run this script again
echo.
echo Alternative: Use the .exe directly from dist\StockAnalyzer.exe
echo.
pause
exit /b 1

:found_inno
echo Found Inno Setup: %INNO_SETUP%
echo.

REM Create output directory
if not exist "installer_output" mkdir installer_output

REM Build the installer
echo Building installer...
echo.
%INNO_SETUP% installer.iss

if errorlevel 1 (
    echo.
    echo ====================================
    echo INSTALLER BUILD FAILED!
    echo ====================================
    echo.
    echo Please check:
    echo 1. dist\StockAnalyzer.exe exists
    echo 2. installer.iss is correctly configured
    echo 3. Inno Setup is properly installed
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================
echo INSTALLER BUILD COMPLETED!
echo ====================================
echo.

REM Find and display the installer
for %%F in (installer_output\*.exe) do (
    echo Your installer is ready:
    echo %%~fF
    echo.
    echo File size: %%~zF bytes
    echo.
)

echo ====================================
echo NEXT STEPS
echo ====================================
echo.
echo 1. TEST the installer on a clean Windows PC
echo 2. (Optional) Sign the installer - see SIGNING_GUIDE.md
echo 3. Upload to GitHub Releases or your website
echo 4. Users can now download and install with one click!
echo.
echo The installer includes:
echo - Professional setup wizard
echo - Start menu shortcuts
echo - Optional desktop shortcut
echo - Automatic uninstaller
echo - User documentation
echo.
pause

