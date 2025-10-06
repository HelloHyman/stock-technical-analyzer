@echo off
REM ===================================================================
REM Stock Analyzer - Build ALL Distribution Packages
REM Creates both portable and installer versions automatically
REM ===================================================================

title Stock Analyzer - Package Builder
color 0B

echo ============================================
echo Stock Analyzer - Complete Package Builder
echo ============================================
echo.
echo This will create:
echo 1. Portable ZIP (one-click launcher)
echo 2. Simple Installer (minimal clicks)
echo 3. Standard Installer (more options)
echo.
pause

REM Step 1: Build the executable
echo.
echo ============================================
echo [1/4] Building Executable
echo ============================================
echo.

if exist "dist\StockAnalyzer.exe" (
    set /p REBUILD="Executable exists. Rebuild? (Y/N): "
    if /i "%REBUILD%"=="Y" (
        call build_exe.bat
        if errorlevel 1 exit /b 1
    ) else (
        echo Using existing executable
    )
) else (
    call build_exe.bat
    if errorlevel 1 exit /b 1
)

REM Step 2: Create Portable ZIP package
echo.
echo ============================================
echo [2/4] Creating Portable ZIP Package
echo ============================================
echo.

if not exist "dist\StockAnalyzer.exe" (
    echo ERROR: Executable not found!
    pause
    exit /b 1
)

echo Copying one-click launcher to dist...
copy /Y StockAnalyzer_OneClick.bat dist\ >nul

echo Creating portable ZIP package...
cd dist
powershell -Command "Compress-Archive -Path StockAnalyzer.exe,StockAnalyzer_OneClick.bat -DestinationPath ..\StockAnalyzer_Portable.zip -Force"
cd ..

if exist "StockAnalyzer_Portable.zip" (
    echo [OK] Portable package created!
    for %%F in (StockAnalyzer_Portable.zip) do echo     Size: %%~zF bytes
) else (
    echo [FAIL] Failed to create portable package
)

REM Step 3: Create Simple Installer
echo.
echo ============================================
echo [3/4] Creating Simple Installer
echo ============================================
echo.

REM Find Inno Setup
set INNO_SETUP=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set INNO_SETUP="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set INNO_SETUP="C:\Program Files\Inno Setup 6\ISCC.exe"

if %INNO_SETUP%=="" (
    echo [SKIP] Inno Setup not found
    echo        Download from: https://jrsoftware.org/isdl.php
    set INSTALLER_BUILT=NO
) else (
    if not exist "installer_output" mkdir installer_output
    
    echo Building simple installer...
    %INNO_SETUP% installer_simple.iss >nul 2>&1
    
    if errorlevel 1 (
        echo [FAIL] Simple installer build failed
    ) else (
        echo [OK] Simple installer created!
        for %%F in (installer_output\*_Simple.exe) do echo     Size: %%~zF bytes
        set INSTALLER_BUILT=YES
    )
)

REM Step 4: Create Standard Installer
echo.
echo ============================================
echo [4/4] Creating Standard Installer
echo ============================================
echo.

if %INNO_SETUP%=="" (
    echo [SKIP] Inno Setup not found
) else (
    echo Building standard installer...
    %INNO_SETUP% installer.iss >nul 2>&1
    
    if errorlevel 1 (
        echo [FAIL] Standard installer build failed
    ) else (
        echo [OK] Standard installer created!
        for %%F in (installer_output\StockAnalyzer_Setup_*.exe) do (
            if not "%%~nF"=="*_Simple" (
                echo     Size: %%~zF bytes
            )
        )
    )
)

REM Summary
echo.
echo ============================================
echo BUILD COMPLETE!
echo ============================================
echo.
echo Distribution Packages Created:
echo.

if exist "StockAnalyzer_Portable.zip" (
    echo [✓] Portable Package:
    echo     StockAnalyzer_Portable.zip
    for %%F in (StockAnalyzer_Portable.zip) do echo     Size: %%~zF bytes
    echo     Usage: Extract and run StockAnalyzer_OneClick.bat
    echo.
)

if exist "installer_output\StockAnalyzer_Setup_1.0.0_Simple.exe" (
    echo [✓] Simple Installer:
    for %%F in (installer_output\*_Simple.exe) do (
        echo     %%~nxF
        echo     Size: %%~zF bytes
    )
    echo     Usage: Run and click "Install Now"
    echo.
)

if exist "installer_output\StockAnalyzer_Setup_1.0.0.exe" (
    echo [✓] Standard Installer:
    for %%F in (installer_output\StockAnalyzer_Setup_*.exe) do (
        set "filename=%%~nxF"
        echo !filename! | findstr /C:"_Simple" >nul
        if errorlevel 1 (
            echo     %%~nxF
            echo     Size: %%~zF bytes
        )
    )
    echo     Usage: Run and follow setup wizard
    echo.
)

echo ============================================
echo NEXT STEPS
echo ============================================
echo.
echo 1. Test the packages:
echo    - Extract and run portable version
echo    - Test simple installer on clean PC
echo.
echo 2. Upload to GitHub Releases:
echo    - StockAnalyzer_Portable.zip (recommended)
echo    - StockAnalyzer_Setup_*_Simple.exe (recommended)
echo    - StockAnalyzer_Setup_*.exe (optional)
echo.
echo 3. Share with users!
echo.
echo See ONE_CLICK_GUIDE.md for user instructions
echo.
pause

