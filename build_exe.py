#!/usr/bin/env python3
"""
Automated build script for creating Windows executable
This script handles everything needed to create a standalone .exe file
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        return False

def check_python():
    """Check if Python is installed and accessible"""
    print("🐍 Checking Python installation...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python found: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Python not found or not accessible: {e}")
        return False

def install_dependencies():
    """Install all required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def create_spec_file():
    """Create PyInstaller spec file for better control"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['SC_Automated_Analysis.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'flet',
        'pandas',
        'numpy',
        'yfinance',
        'plotly',
        'matplotlib',
        'mplfinance',
        'requests',
        'requests_cache',
        'tenacity',
        'plotly.graph_objects',
        'plotly.subplots',
        'plotly.io',
        'matplotlib.pyplot',
        'matplotlib.lines',
        'mplfinance',
        'base64',
        'io',
        'threading',
        'asyncio',
        'concurrent.futures',
        'dataclasses',
        'datetime',
        'functools',
        'typing',
        'json',
        'urllib',
        'ssl',
        'certifi'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StockCryptoAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StockCryptoAnalyzer'
)
'''
    
    with open('SC_Automated_Analysis.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n🔨 Building executable...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🧹 Cleaned build directory")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🧹 Cleaned dist directory")
    
    # Create spec file
    create_spec_file()
    
    # Build with PyInstaller
    if not run_command(f"{sys.executable} -m PyInstaller SC_Automated_Analysis.spec", "Building executable"):
        return False
    
    return True

def create_installer_info():
    """Create information file for the built executable"""
    info_content = """
Stock and Crypto Automated Analysis - Executable Build Info
===========================================================

Build Date: {build_date}
Python Version: {python_version}
PyInstaller Version: {pyinstaller_version}

Installation Instructions:
1. The executable has been created in the 'dist/StockCryptoAnalyzer' folder
2. You can run 'StockCryptoAnalyzer.exe' directly from that folder
3. No additional installation is required - it's a standalone executable

Files included:
- StockCryptoAnalyzer.exe (main application)
- All required libraries and dependencies

Note: The first run might take a few seconds to load all dependencies.

For support or issues, please check the README.md file.
""".format(
        build_date=subprocess.run(['date'], capture_output=True, text=True).stdout.strip() if os.name != 'nt' else subprocess.run(['powershell', 'Get-Date'], capture_output=True, text=True).stdout.strip(),
        python_version=sys.version.split()[0],
        pyinstaller_version=subprocess.run([sys.executable, '-m', 'pip', 'show', 'pyinstaller'], capture_output=True, text=True).stdout.split('\n')[1].split(': ')[1] if 'pyinstaller' in subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True).stdout else 'Unknown'
    )
    
    with open('BUILD_INFO.txt', 'w') as f:
        f.write(info_content)
    
    print("✅ Created build information file")

def main():
    """Main build process"""
    print("🚀 Starting Stock and Crypto Analyzer Build Process")
    print("=" * 60)
    
    # Check Python
    if not check_python():
        print("\n❌ Build failed: Python not found")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Build failed: Could not install dependencies")
        return False
    
    # Build executable
    if not build_executable():
        print("\n❌ Build failed: Could not create executable")
        return False
    
    # Create info file
    create_installer_info()
    
    print("\n" + "=" * 60)
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📁 Your executable is ready in: dist/StockCryptoAnalyzer/")
    print("🚀 Run: dist/StockCryptoAnalyzer/StockCryptoAnalyzer.exe")
    print("\n📋 Check BUILD_INFO.txt for more details")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
