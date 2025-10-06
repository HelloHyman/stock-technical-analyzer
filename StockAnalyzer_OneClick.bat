@echo off
REM ===================================================================
REM Stock Analyzer - One-Click Portable Launcher
REM This script sets up shortcuts and launches the app automatically
REM NO INSTALLATION NEEDED - Just click and go!
REM ===================================================================

title Stock Analyzer - One-Click Setup
color 0A

REM Get the directory where this script is located
set "APP_DIR=%~dp0"
set "EXE_PATH=%APP_DIR%dist\StockAnalyzer.exe"

REM Check if executable exists
if not exist "%EXE_PATH%" (
    echo ============================================
    echo ERROR: StockAnalyzer.exe not found!
    echo ============================================
    echo.
    echo Expected location: %EXE_PATH%
    echo.
    echo Please ensure the executable is in the 'dist' folder
    echo or run this from the correct directory.
    echo.
    pause
    exit /b 1
)

echo ============================================
echo Stock Analyzer - One-Click Setup
echo ============================================
echo.
echo Setting up your Stock Analyzer...
echo.

REM Create Desktop shortcut
echo [1/3] Creating Desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Stock Analyzer.lnk'); $Shortcut.TargetPath = '%EXE_PATH%'; $Shortcut.WorkingDirectory = '%APP_DIR%dist'; $Shortcut.Description = 'Stock and Crypto Technical Analyzer'; $Shortcut.Save()" >nul 2>&1

if errorlevel 1 (
    echo    [SKIP] Could not create desktop shortcut
) else (
    echo    [OK] Desktop shortcut created!
)

REM Create Start Menu shortcut
echo [2/3] Creating Start Menu shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Programs') + '\Stock Analyzer.lnk'); $Shortcut.TargetPath = '%EXE_PATH%'; $Shortcut.WorkingDirectory = '%APP_DIR%dist'; $Shortcut.Description = 'Stock and Crypto Technical Analyzer'; $Shortcut.Save()" >nul 2>&1

if errorlevel 1 (
    echo    [SKIP] Could not create Start Menu shortcut
) else (
    echo    [OK] Start Menu shortcut created!
)

REM Launch the application
echo [3/3] Launching Stock Analyzer...
echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Shortcuts created:
echo - Desktop: Stock Analyzer
echo - Start Menu: Stock Analyzer
echo.
echo Stock Analyzer is now launching...
echo.
echo Next time, just double-click the Desktop icon!
echo.

REM Wait a moment for user to see the message
timeout /t 2 /nobreak >nul

REM Launch the app
start "" "%EXE_PATH%"

REM Close this window after 3 seconds
echo This window will close in 3 seconds...
timeout /t 3 /nobreak >nul

exit

