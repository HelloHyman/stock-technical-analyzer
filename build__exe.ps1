#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Automated Python 3.13 Setup and Stock/Crypto Analyzer Build Script
    
.DESCRIPTION
    This script automatically installs Python 3.13, sets it as default, configures the environment,
    and builds the Stock and Crypto Analyzer executable.
    
.PARAMETER SkipPythonInstall
    Skip Python installation if already installed
    
.PARAMETER SkipBuild
    Skip building the executable after setup
    
.EXAMPLE
    .\build__exe.ps1
    Full automated setup and build
    
.EXAMPLE
    .\build__exe.ps1 -SkipPythonInstall
    Skip Python installation, just build executable
#>

param(
    [switch]$SkipPythonInstall,
    [switch]$SkipBuild
)

# Set console properties for better display
$Host.UI.RawUI.WindowTitle = "Stock & Crypto Analyzer - Build Setup"
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "White"
Clear-Host

# Color scheme
$Colors = @{
    Header = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "White"
    Progress = "Magenta"
}

# Global variables
$PythonVersion = "3.13"
$PythonPath = "C:\Program Files\Python313"
$PythonScriptsPath = "$PythonPath\Scripts"
$PythonExecutable = "$PythonPath\python.exe"
$PipExecutable = "$PythonPath\Scripts\pip.exe"

# Loading animation function
function Show-LoadingAnimation {
    param(
        [string]$Message,
        [int]$DurationSeconds = 3
    )
    
    $spinner = @('⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏')
    $endTime = (Get-Date).AddSeconds($DurationSeconds)
    
    Write-Host "`n$Message" -ForegroundColor $Colors.Progress
    Write-Host "[" -NoNewline -ForegroundColor $Colors.Info
    
    while ((Get-Date) -lt $endTime) {
        foreach ($char in $spinner) {
            Write-Host $char -NoNewline -ForegroundColor $Colors.Progress
            Start-Sleep -Milliseconds 100
            Write-Host "`b" -NoNewline
        }
    }
    Write-Host "✓" -NoNewline -ForegroundColor $Colors.Success
    Write-Host "]" -ForegroundColor $Colors.Info
}

# Function to write colored output
function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Prefix = ""
    )
    
    if ($Prefix) {
        Write-Host "$Prefix " -NoNewline -ForegroundColor $Colors.Info
    }
    Write-Host $Message -ForegroundColor $Color
}

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to check if Python 3.13 is installed
function Test-Python313Installed {
    try {
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -match "Python 3\.13") {
            Write-ColoredOutput "✅ Python 3.13 is already installed: $pythonVersion" $Colors.Success
            return $true
        } else {
            Write-ColoredOutput "⚠️  Different Python version found: $pythonVersion" $Colors.Warning
            return $false
        }
    } catch {
        Write-ColoredOutput "❌ Python not found in PATH" $Colors.Error
        return $false
    }
}

# Function to install Python 3.13 using winget
function Install-Python313Winget {
    Write-ColoredOutput "📦 Attempting to install Python 3.13 using winget..." $Colors.Info
    
    try {
        # Check if winget is available
        $wingetCheck = Get-Command winget -ErrorAction SilentlyContinue
        if (-not $wingetCheck) {
            Write-ColoredOutput "❌ winget not available" $Colors.Error
            return $false
        }
        
        Write-ColoredOutput "🔍 Searching for Python 3.13..." $Colors.Info
        Show-LoadingAnimation "Installing Python 3.13 via winget" 5
        
        # Install Python 3.13
        $result = winget install Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Python 3.13 installed successfully via winget" $Colors.Success
            return $true
        } else {
            Write-ColoredOutput "❌ winget installation failed" $Colors.Error
            return $false
        }
    } catch {
        Write-ColoredOutput "❌ Error during winget installation: $_" $Colors.Error
        return $false
    }
}

# Function to install Python 3.13 using direct download
function Install-Python313Direct {
    Write-ColoredOutput "📥 Downloading Python 3.13 installer..." $Colors.Info
    
    $downloadUrl = "https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe"
    $installerPath = "$env:TEMP\python-3.13.0-amd64.exe"
    
    try {
        Show-LoadingAnimation "Downloading Python 3.13 installer" 10
        
        # Download the installer
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        
        Write-ColoredOutput "✅ Download completed" $Colors.Success
        Write-ColoredOutput "🔧 Installing Python 3.13..." $Colors.Info
        
        Show-LoadingAnimation "Running silent installation" 15
        
        # Run silent installation
        $installArgs = @(
            "/quiet",
            "InstallAllUsers=1",
            "PrependPath=1",
            "Include_test=0",
            "AssociateFiles=1",
            "Shortcuts=1",
            "Include_doc=0",
            "Include_launcher=1",
            "Include_tcltk=1"
        )
        
        $process = Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-ColoredOutput "✅ Python 3.13 installed successfully" $Colors.Success
            
            # Clean up installer
            Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
            
            return $true
        } else {
            Write-ColoredOutput "❌ Installation failed with exit code: $($process.ExitCode)" $Colors.Error
            return $false
        }
    } catch {
        Write-ColoredOutput "❌ Error during direct installation: $_" $Colors.Error
        return $false
    }
}

# Function to configure Python 3.13 as default
function Set-Python313AsDefault {
    Write-ColoredOutput "⚙️  Configuring Python 3.13 as default..." $Colors.Info
    
    try {
        # Create py.ini file
        $pyIniPath = "$env:ProgramData\py\py.ini"
        $pyIniDir = Split-Path $pyIniPath -Parent
        
        if (-not (Test-Path $pyIniDir)) {
            New-Item -ItemType Directory -Path $pyIniDir -Force | Out-Null
        }
        
        $pyIniContent = @"
[defaults]
python=3.13
"@
        
        Set-Content -Path $pyIniPath -Value $pyIniContent -Encoding UTF8
        Write-ColoredOutput "✅ py.ini configured" $Colors.Success
        
        # Refresh environment variables
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        
        return $true
    } catch {
        Write-ColoredOutput "❌ Error configuring Python default: $_" $Colors.Error
        return $false
    }
}

# Function to add Python to PATH
function Add-PythonToPath {
    Write-ColoredOutput "🛤️  Adding Python to system PATH..." $Colors.Info
    
    try {
        $currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
        $pathsToAdd = @($PythonPath, $PythonScriptsPath)
        
        foreach ($path in $pathsToAdd) {
            if ($currentPath -notlike "*$path*") {
                $currentPath += ";$path"
                Write-ColoredOutput "➕ Adding to PATH: $path" $Colors.Info
            } else {
                Write-ColoredOutput "✅ Already in PATH: $path" $Colors.Success
            }
        }
        
        # Update system PATH
        [System.Environment]::SetEnvironmentVariable("PATH", $currentPath, "Machine")
        
        # Update current session PATH
        $env:PATH = $currentPath + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        
        Write-ColoredOutput "✅ PATH updated successfully" $Colors.Success
        return $true
    } catch {
        Write-ColoredOutput "❌ Error updating PATH: $_" $Colors.Error
        return $false
    }
}

# Function to install dependencies
function Install-Dependencies {
    Write-ColoredOutput "📦 Installing project dependencies..." $Colors.Info
    
    try {
        # Check if requirements.txt exists
        if (-not (Test-Path "requirements.txt")) {
            Write-ColoredOutput "❌ requirements.txt not found in current directory" $Colors.Error
            return $false
        }
        
        # Upgrade pip first
        Write-ColoredOutput "🔄 Upgrading pip..." $Colors.Info
        Show-LoadingAnimation "Upgrading pip" 5
        & python -m pip install --upgrade pip --quiet
        
        # Install requirements
        Write-ColoredOutput "📥 Installing requirements..." $Colors.Info
        Show-LoadingAnimation "Installing dependencies from requirements.txt" 10
        
        $result = & python -m pip install -r requirements.txt --quiet
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Dependencies installed successfully" $Colors.Success
            return $true
        } else {
            Write-ColoredOutput "❌ Failed to install dependencies" $Colors.Error
            return $false
        }
    } catch {
        Write-ColoredOutput "❌ Error installing dependencies: $_" $Colors.Error
        return $false
    }
}

# Function to verify installation
function Test-Installation {
    Write-ColoredOutput "🔍 Verifying installation..." $Colors.Info
    
    try {
        # Test Python version
        $pythonVersion = & python --version 2>&1
        Write-ColoredOutput "✅ Python: $pythonVersion" $Colors.Success
        
        # Test pip
        $pipVersion = & python -m pip --version 2>&1
        Write-ColoredOutput "✅ pip: $pipVersion" $Colors.Success
        
        # Test key packages
        $packages = @("flet", "pandas", "numpy", "yfinance", "matplotlib", "mplfinance")
        foreach ($package in $packages) {
            try {
                $version = & python -c "import $package; print($package.__version__)" 2>&1
                Write-ColoredOutput "✅ $package`: $version" $Colors.Success
            } catch {
                Write-ColoredOutput "❌ $package`: Not installed or error" $Colors.Error
            }
        }
        
        return $true
    } catch {
        Write-ColoredOutput "❌ Error during verification: $_" $Colors.Error
        return $false
    }
}

# Function to build executable
function Build-Executable {
    Write-ColoredOutput "🔨 Building executable..." $Colors.Info
    
    try {
        # Check if build script exists
        if (-not (Test-Path "build_exe.py")) {
            Write-ColoredOutput "❌ build_exe.py not found" $Colors.Error
            return $false
        }
        
        Show-LoadingAnimation "Building Stock & Crypto Analyzer executable" 20
        
        $result = & python build_exe.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ Executable built successfully!" $Colors.Success
            Write-ColoredOutput "📁 Location: dist\StockCryptoAnalyzer\" $Colors.Info
            return $true
        } else {
            Write-ColoredOutput "❌ Build failed" $Colors.Error
            return $false
        }
    } catch {
        Write-ColoredOutput "❌ Error during build: $_" $Colors.Error
        return $false
    }
}

# Main execution
function Main {
    # Display header
    Write-Host "`n" -NoNewline
    Write-Host "=" * 80 -ForegroundColor $Colors.Header
    Write-Host "🚀 Stock & Crypto Analyzer - Automated Setup & Build" -ForegroundColor $Colors.Header
    Write-Host "=" * 80 -ForegroundColor $Colors.Header
    Write-Host "`n"
    
    # Check administrator privileges
    if (-not (Test-Administrator)) {
        Write-ColoredOutput "❌ This script requires administrator privileges!" $Colors.Error
        Write-ColoredOutput "Please run PowerShell as Administrator and try again." $Colors.Warning
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-ColoredOutput "🔐 Running with administrator privileges" $Colors.Success
    
    # Step 1: Check Python 3.13 installation
    Write-Host "`n" + "=" * 60 -ForegroundColor $Colors.Header
    Write-Host "🐍 STEP 1: Python 3.13 Installation Check" -ForegroundColor $Colors.Header
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    
    if (-not $SkipPythonInstall) {
        if (-not (Test-Python313Installed)) {
            Write-ColoredOutput "📥 Python 3.13 not found. Installing..." $Colors.Info
            
            # Try winget first, then direct download
            $installed = $false
            
            if (-not $installed) {
                $installed = Install-Python313Winget
            }
            
            if (-not $installed) {
                Write-ColoredOutput "🔄 winget failed, trying direct download..." $Colors.Warning
                $installed = Install-Python313Direct
            }
            
            if (-not $installed) {
                Write-ColoredOutput "❌ Failed to install Python 3.13" $Colors.Error
                Read-Host "Press Enter to exit"
                exit 1
            }
            
            # Refresh PATH and verify installation
            Add-PythonToPath
            Start-Sleep -Seconds 2
            
            if (-not (Test-Python313Installed)) {
                Write-ColoredOutput "❌ Python 3.13 installation verification failed" $Colors.Error
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
        
        # Configure as default
        Set-Python313AsDefault
        
        # Add to PATH
        Add-PythonToPath
    } else {
        Write-ColoredOutput "⏭️  Skipping Python installation (SkipPythonInstall flag)" $Colors.Info
    }
    
    # Step 2: Install dependencies
    Write-Host "`n" + "=" * 60 -ForegroundColor $Colors.Header
    Write-Host "📦 STEP 2: Dependencies Installation" -ForegroundColor $Colors.Header
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    
    if (-not (Install-Dependencies)) {
        Write-ColoredOutput "❌ Dependency installation failed" $Colors.Error
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Step 3: Verify installation
    Write-Host "`n" + "=" * 60 -ForegroundColor $Colors.Header
    Write-Host "🔍 STEP 3: Installation Verification" -ForegroundColor $Colors.Header
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    
    Test-Installation
    
    # Step 4: Build executable (optional)
    if (-not $SkipBuild) {
        Write-Host "`n" + "=" * 60 -ForegroundColor $Colors.Header
        Write-Host "🔨 STEP 4: Building Executable" -ForegroundColor $Colors.Header
        Write-Host "=" * 60 -ForegroundColor $Colors.Header
        
        if (Build-Executable) {
            Write-Host "`n" + "=" * 80 -ForegroundColor $Colors.Success
            Write-Host "🎉 SETUP COMPLETED SUCCESSFULLY!" -ForegroundColor $Colors.Success
            Write-Host "=" * 80 -ForegroundColor $Colors.Success
            Write-Host "`n"
            Write-ColoredOutput "🚀 Your Stock & Crypto Analyzer is ready!" $Colors.Success
            Write-ColoredOutput "📁 Executable location: dist\StockCryptoAnalyzer\StockCryptoAnalyzer.exe" $Colors.Info
            Write-ColoredOutput "🔧 Python 3.13 is now your default Python version" $Colors.Info
        } else {
            Write-ColoredOutput "⚠️  Setup completed but build failed" $Colors.Warning
        }
    } else {
        Write-Host "`n" + "=" * 80 -ForegroundColor $Colors.Success
        Write-Host "🎉 SETUP COMPLETED SUCCESSFULLY!" -ForegroundColor $Colors.Success
        Write-Host "=" * 80 -ForegroundColor $Colors.Success
        Write-Host "`n"
        Write-ColoredOutput "🚀 Python 3.13 setup completed!" $Colors.Success
        Write-ColoredOutput "🔧 Python 3.13 is now your default Python version" $Colors.Info
        Write-ColoredOutput "📦 All dependencies are installed" $Colors.Info
    }
    
    Write-Host "`n"
    Read-Host "Press Enter to exit"
}

# Run main function
Main
