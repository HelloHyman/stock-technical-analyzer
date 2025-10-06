@echo off
REM ===================================================================
REM Stock Analyzer - Dependency Checker
REM This script checks if all required dependencies are installed
REM ===================================================================

echo ====================================
echo Stock Analyzer - Dependency Check
echo ====================================
echo.

REM Check Python installation
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo    [FAIL] Python is not installed or not in PATH
    echo    Please install Python 3.8+ from https://www.python.org/
    set ERRORS=1
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo    [OK] %PYTHON_VERSION%
)
echo.

REM Check pip
echo [2/7] Checking pip installation...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo    [FAIL] pip is not available
    echo    Please reinstall Python with pip
    set ERRORS=1
) else (
    for /f "tokens=*" %%i in ('python -m pip --version 2^>^&1') do set PIP_VERSION=%%i
    echo    [OK] %PIP_VERSION%
)
echo.

REM Check pandas
echo [3/7] Checking pandas...
python -c "import pandas; print(f'pandas {pandas.__version__}')" 2>nul
if errorlevel 1 (
    echo    [FAIL] pandas not installed
    echo    Install with: pip install pandas
    set ERRORS=1
) else (
    for /f "tokens=*" %%i in ('python -c "import pandas; print(f'pandas {pandas.__version__}')"') do echo    [OK] %%i
)
echo.

REM Check numpy
echo [4/7] Checking numpy...
python -c "import numpy; print(f'numpy {numpy.__version__}')" 2>nul
if errorlevel 1 (
    echo    [FAIL] numpy not installed
    echo    Install with: pip install numpy
    set ERRORS=1
) else (
    for /f "tokens=*" %%i in ('python -c "import numpy; print(f'numpy {numpy.__version__}')"') do echo    [OK] %%i
)
echo.

REM Check yfinance
echo [5/7] Checking yfinance...
python -c "import yfinance; print(f'yfinance {yfinance.__version__}')" 2>nul
if errorlevel 1 (
    echo    [FAIL] yfinance not installed
    echo    Install with: pip install yfinance
    set ERRORS=1
) else (
    for /f "tokens=*" %%i in ('python -c "import yfinance; print(f'yfinance {yfinance.__version__}')"') do echo    [OK] %%i
)
echo.

REM Check matplotlib
echo [6/7] Checking matplotlib...
python -c "import matplotlib; print(f'matplotlib {matplotlib.__version__}')" 2>nul
if errorlevel 1 (
    echo    [FAIL] matplotlib not installed
    echo    Install with: pip install matplotlib
    set ERRORS=1
) else (
    for /f "tokens=*" %%i in ('python -c "import matplotlib; print(f'matplotlib {matplotlib.__version__}')"') do echo    [OK] %%i
)
echo.

REM Check mplfinance
echo [7/7] Checking mplfinance...
python -c "import mplfinance; print(f'mplfinance {mplfinance.__version__}')" 2>nul
if errorlevel 1 (
    echo    [FAIL] mplfinance not installed
    echo    Install with: pip install mplfinance
    set ERRORS=1
) else (
    for /f "tokens=*" %%i in ('python -c "import mplfinance; print(f'mplfinance {mplfinance.__version__}')"') do echo    [OK] %%i
)
echo.

REM Summary
echo ====================================
if defined ERRORS (
    echo STATUS: SOME DEPENDENCIES MISSING
    echo ====================================
    echo.
    echo To install all dependencies at once, run:
    echo pip install pandas numpy yfinance matplotlib mplfinance
    echo.
    echo Or use the requirements file:
    echo pip install -r requirements.txt
    echo.
) else (
    echo STATUS: ALL DEPENDENCIES OK!
    echo ====================================
    echo.
    echo You're ready to run Stock Analyzer!
    echo.
    echo To run the application:
    echo python manual_stock_analyzer.py
    echo.
    echo To build the executable:
    echo build_exe.bat
    echo.
)

pause

