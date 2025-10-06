@echo off
REM ===================================================================
REM Stock Analyzer - Simple Installer Builder
REM Creates an ultra-simple installer with minimal user clicks
REM ===================================================================

echo ====================================
echo Stock Analyzer - Simple Installer
echo ====================================
echo.
echo Creating a user-friendly installer with:
echo - Automatic installation
echo - Desktop shortcut (default ON)
echo - Auto-launch after install
echo - Minimal clicks needed
echo.

REM Step 1: Build the executable if needed
if not exist "dist\StockAnalyzer.exe" (
    echo [1/2] Building executable first...
    call build_exe.bat
    if errorlevel 1 (
        echo ERROR: Failed to build executable
        pause
        exit /b 1
    )
) else (
    echo [1/2] Executable exists: dist\StockAnalyzer.exe
)

echo.
echo [2/2] Building ultra-simple installer...
echo.

REM Find Inno Setup
set INNO_SETUP=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set INNO_SETUP="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    goto :found_inno
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set INNO_SETUP="C:\Program Files\Inno Setup 6\ISCC.exe"
    goto :found_inno
)

echo ERROR: Inno Setup not found!
echo Download from: https://jrsoftware.org/isdl.php
echo.
pause
exit /b 1

:found_inno
if not exist "installer_output" mkdir installer_output

%INNO_SETUP% installer_simple.iss

if errorlevel 1 (
    echo.
    echo ERROR: Installer build failed
    pause
    exit /b 1
)

echo.
echo ====================================
echo SUCCESS!
echo ====================================
echo.
echo Your ultra-simple installer is ready:
for %%F in (installer_output\*_Simple.exe) do (
    echo %%~fF
    echo Size: %%~zF bytes
)
echo.
echo This installer:
echo - Installs with just 2-3 clicks
echo - Creates desktop shortcut automatically
echo - Launches app immediately after install
echo - Perfect for non-technical users!
echo.
echo Upload this to GitHub Releases and share with users!
echo.
pause

