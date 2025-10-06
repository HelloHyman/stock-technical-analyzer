@echo off
REM ===================================================================
REM Stock Analyzer - Code Signing Script
REM This script signs the executable with a digital certificate
REM ===================================================================

echo ====================================
echo Stock Analyzer - Code Signing
echo ====================================
echo.

REM Check if executable exists
if not exist "dist\StockAnalyzer.exe" (
    echo ERROR: StockAnalyzer.exe not found!
    echo Please run build_exe.bat first to create the executable.
    echo.
    pause
    exit /b 1
)

echo Found: dist\StockAnalyzer.exe
echo.

REM Find SignTool
set SIGNTOOL=""
for /f "delims=" %%i in ('dir /b /s "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe" 2^>nul') do set SIGNTOOL="%%i" & goto :found
for /f "delims=" %%i in ('dir /b /s "C:\Program Files\Windows Kits\10\bin\*\x64\signtool.exe" 2^>nul') do set SIGNTOOL="%%i" & goto :found

echo ERROR: SignTool not found!
echo.
echo Please install Windows SDK from:
echo https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
echo.
echo Or specify the SignTool path manually in this script.
pause
exit /b 1

:found
echo Found SignTool: %SIGNTOOL%
echo.

REM Prompt for certificate information
echo ====================================
echo Certificate Configuration
echo ====================================
echo.
echo You need a code signing certificate (.pfx or .p12 file)
echo If you don't have one, see SIGNING_GUIDE.md for instructions.
echo.

set /p CERT_PATH="Enter the full path to your certificate file: "
if not exist "%CERT_PATH%" (
    echo ERROR: Certificate file not found: %CERT_PATH%
    pause
    exit /b 1
)

echo.
set /p CERT_PASSWORD="Enter certificate password (input hidden for security): "
echo.

REM Choose timestamp server
echo.
echo Select timestamp server:
echo 1. DigiCert (recommended)
echo 2. GlobalSign
echo 3. Sectigo
echo 4. Custom URL
echo.
set /p TS_CHOICE="Enter choice (1-4): "

if "%TS_CHOICE%"=="1" set TIMESTAMP_URL=http://timestamp.digicert.com
if "%TS_CHOICE%"=="2" set TIMESTAMP_URL=http://timestamp.globalsign.com/scripts/timstamp.dll
if "%TS_CHOICE%"=="3" set TIMESTAMP_URL=http://timestamp.sectigo.com
if "%TS_CHOICE%"=="4" (
    set /p TIMESTAMP_URL="Enter timestamp server URL: "
)

echo.
echo ====================================
echo Signing Configuration
echo ====================================
echo Certificate: %CERT_PATH%
echo Timestamp: %TIMESTAMP_URL%
echo Executable: dist\StockAnalyzer.exe
echo ====================================
echo.

set /p CONFIRM="Proceed with signing? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Signing cancelled.
    pause
    exit /b 0
)

echo.
echo Signing executable...
echo.

REM Sign the executable
%SIGNTOOL% sign /f "%CERT_PATH%" /p "%CERT_PASSWORD%" /tr "%TIMESTAMP_URL%" /td SHA256 /fd SHA256 /v "dist\StockAnalyzer.exe"

if errorlevel 1 (
    echo.
    echo ====================================
    echo SIGNING FAILED!
    echo ====================================
    echo.
    echo Common issues:
    echo - Wrong certificate password
    echo - Certificate not valid for code signing
    echo - Timestamp server unreachable
    echo - Certificate expired
    echo.
    echo See SIGNING_GUIDE.md for troubleshooting.
    pause
    exit /b 1
)

echo.
echo ====================================
echo Verifying signature...
echo ====================================
echo.

%SIGNTOOL% verify /pa /v "dist\StockAnalyzer.exe"

if errorlevel 1 (
    echo.
    echo WARNING: Signature verification failed!
    echo The file was signed but verification failed.
    echo This might indicate an issue with the certificate chain.
    pause
    exit /b 1
)

echo.
echo ====================================
echo SIGNING COMPLETED SUCCESSFULLY!
echo ====================================
echo.
echo Your signed executable is ready:
echo dist\StockAnalyzer.exe
echo.
echo You can verify the signature by:
echo 1. Right-click the file ^> Properties ^> Digital Signatures
echo 2. Or run: signtool verify /pa /v "dist\StockAnalyzer.exe"
echo.
echo Note: New certificates may still trigger SmartScreen warnings
echo until reputation is built. See SIGNING_GUIDE.md for details.
echo.
pause

