# Changelog

All notable changes to Stock Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Mobile version support
- Additional technical indicators (MACD, Bollinger Bands)
- Portfolio tracking features
- Export chart images functionality
- Dark mode theme option
- Customizable alert system
- Multi-symbol comparison view

---

## [1.0.0] - 2025-01-06

### Added

#### Core Features
- **Real-time stock and cryptocurrency analysis** using Yahoo Finance API
- **Interactive candlestick charts** with zoom and pan capabilities
- **Multiple timeframe support** (1 day, 5 days, 1 month, 3 months, 6 months, 1 year, 2 years, 5 years, 10 years, Max)
- **Moving averages** (10, 20, 30, 50, 72, 100, 200, 400, 420-day)
- **Technical indicators:**
  - RSI (Relative Strength Index)
  - Support levels (20-day rolling low)
  - Resistance levels (20-day rolling high)
  - Base price calculation for entry points
  - 5% below base price indicator

#### Performance & Optimization
- **Data caching system** with 5-minute TTL for improved performance
- **Asynchronous data fetching** for non-blocking UI
- **Thread pool executor** for concurrent operations
- **Lazy loading** of heavy libraries
- **Optimized chart rendering**

#### User Interface
- **Clean, modern Tkinter GUI** with intuitive controls
- **Symbol information panel** showing:
  - Company name
  - Sector and industry (for stocks)
  - Market cap
  - P/E ratio (for stocks)
  - 52-week high/low
- **Customizable chart controls:**
  - Timeframe selector
  - Moving average toggles
  - Update chart functionality
- **Symbol validation** with user-friendly error messages
- **Progress indicators** during data loading

#### Distribution & Packaging

**Build Scripts:**
- `build_exe.bat` - Build standalone executable using PyInstaller
- `build_installer.bat` - Create professional Windows installer
- `build_simple_installer.bat` - Create ultra-simple installer with minimal clicks
- `build_all_packages.bat` - Build all distribution packages at once
- `sign_exe.bat` - Code signing script for executables

**Installer Configurations:**
- `installer.iss` - Standard Inno Setup installer configuration
- `installer_simple.iss` - Simplified installer with auto-launch and minimal prompts
- `stock_analyzer.spec` - PyInstaller specification file

**User Tools:**
- `StockAnalyzer_OneClick.bat` - One-click portable launcher that:
  - Auto-creates Desktop shortcut
  - Auto-creates Start Menu shortcut
  - Launches app automatically
  - No installation required

**Dependency Management:**
- `install_dependencies.bat` - Automated dependency installation
- `check_dependencies.bat` - Dependency verification tool
- `requirements.txt` - Pinned dependency versions

#### Documentation

**User Documentation:**
- `README.md` - Comprehensive project documentation
- `USER_GUIDE.md` - Detailed user manual with tutorials and tips
- `INSTALL_FOR_USERS.md` - Simple installation guide for non-technical users
- `QUICK_START.md` - Fast-track setup and usage guide
- `ONE_CLICK_GUIDE.md` - Guide for one-click installation options

**Developer Documentation:**
- `INSTALLER_GUIDE.md` - Complete guide for creating Windows installers
- `SIGNING_GUIDE.md` - Code signing guide with CA options and pricing
- `CONTRIBUTING.md` - Contribution guidelines and workflow
- `CHANGELOG.md` - This file

**Legal & Administrative:**
- `LICENSE` - MIT License with disclaimer
- `VERSION` - Version tracking file
- `.gitignore` - Comprehensive ignore patterns

### Technical Details

**Dependencies:**
- Python 3.8+
- pandas >= 2.0.0
- numpy >= 1.24.0
- yfinance >= 0.2.28
- matplotlib >= 3.7.0
- mplfinance >= 0.12.9
- pyinstaller >= 5.13.0 (for building)

**Platform Support:**
- Windows 10/11 (64-bit)
- Python 3.8, 3.9, 3.10, 3.11, 3.12

**Architecture:**
- GUI: Tkinter (built into Python)
- Data source: Yahoo Finance via yfinance
- Charting: matplotlib + mplfinance
- Data processing: pandas, numpy
- Async operations: threading, concurrent.futures
- Packaging: PyInstaller + Inno Setup

### Distribution Options

**For End Users:**

1. **Portable Package** (`StockAnalyzer_Portable.zip`)
   - Extract and run `StockAnalyzer_OneClick.bat`
   - Auto-creates shortcuts
   - No installation needed
   - Perfect for quick testing

2. **Simple Installer** (`StockAnalyzer_Setup_Simple.exe`)
   - 2-3 click installation
   - Auto-launches after install
   - Creates Desktop shortcut automatically
   - Built-in uninstaller

3. **Standard Installer** (`StockAnalyzer_Setup.exe`)
   - Traditional setup wizard
   - More customization options
   - Professional installation experience

**For Developers:**
- Source code with complete build scripts
- Comprehensive documentation
- Example configurations

### Known Limitations

- Requires internet connection for stock data
- Data availability depends on Yahoo Finance
- Some historical data may be limited for newer symbols
- Windows-only executable (cross-platform via Python)

### Security

- No user data collection
- No external API keys required
- Local data caching only
- Open source code for transparency

---

## Version History Summary

- **1.0.0** (2025-01-06) - Initial release with full feature set

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Suggesting features
- Submitting pull requests
- Development setup

---

## Links

- **Repository:** https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer
- **Issues:** https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/issues
- **Releases:** https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/releases

---

## Acknowledgments

- **yfinance** - Yahoo Finance API wrapper
- **mplfinance** - Financial charting library  
- **matplotlib** - Plotting library
- **pandas** - Data analysis library
- **PyInstaller** - Python packaging tool
- **Inno Setup** - Windows installer creator

---

[Unreleased]: https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/releases/tag/v1.0.0

