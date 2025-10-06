# Stock Analyzer - Automated Stock and Crypto Technical Analyzer

A professional desktop application for technical analysis of stocks and cryptocurrencies with interactive charts, moving averages, and technical indicators.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey)

## Features

✅ **Real-time Data**: Fetch live stock and cryptocurrency data  
✅ **Interactive Charts**: Professional candlestick charts with zoom and pan  
✅ **Technical Indicators**: RSI, Support/Resistance levels, Base price calculation  
✅ **Moving Averages**: 10, 20, 30, 50, 72, 100, 200, 400, and 420-day MAs  
✅ **Multiple Timeframes**: 1 day to Max historical data  
✅ **Fast Performance**: Async data fetching and caching  
✅ **User-Friendly**: Clean, modern interface with intuitive controls  

## Screenshots

[Add screenshots of your application here]

---

## For Developers - Building from Source

### Prerequisites

- **Python 3.8 or higher**
- **Windows 10/11** (for .exe building)
- **Internet connection** (for downloading dependencies)
- **Inno Setup** (optional, for installer creation) - [Download](https://jrsoftware.org/isdl.php)

### Quick Start

1. **Clone or download this repository**

2. **Build Options:**

   **Option A: Build Portable .exe Only**
   ```batch
   build_exe.bat
   ```
   
   **Option B: Build Professional Installer (Recommended)**
   ```batch
   build_installer.bat
   ```
   
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Build the executable using PyInstaller
   - Create a professional Windows installer (if Inno Setup installed)

3. **Test the output**:
   ```batch
   # Portable exe
   dist\StockAnalyzer.exe
   
   # Or installer
   installer_output\StockAnalyzer_Setup_1.0.0.exe
   ```

4. **(Optional) Sign the executable/installer**:
   ```batch
   sign_exe.bat
   ```
   See [SIGNING_GUIDE.md](SIGNING_GUIDE.md) for details on code signing.

📖 **Installer creation guide**: See [INSTALLER_GUIDE.md](INSTALLER_GUIDE.md)

### Manual Setup

If you prefer to set up manually:

```batch
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python manual_stock_analyzer.py

# Build executable
pyinstaller stock_analyzer.spec
```

### Dependencies

All dependencies are listed in `requirements.txt`:
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **yfinance** - Stock/crypto data
- **matplotlib** - Charting
- **mplfinance** - Financial charts
- **pyinstaller** - Executable building

---

## For End Users - Installation

### 🚀 ONE-CLICK OPTIONS (Recommended for Non-Technical Users)

#### **Option 1: Portable Package (EASIEST!)** 

**Just ONE click to set up everything!**

1. Download `StockAnalyzer_Portable.zip` from [Releases](https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/releases)
2. Extract the ZIP file
3. Double-click `StockAnalyzer_OneClick.bat`
4. **Done!** App launches, Desktop icon created automatically!

**Features:**
- ✅ No installation needed
- ✅ Desktop shortcut auto-created
- ✅ Start Menu shortcut auto-created
- ✅ App launches immediately
- ✅ Just 1 click to set everything up!
- ✅ No Python needed!

#### **Option 2: Simple Installer (2-3 clicks!)**

**Traditional installation with minimal clicks!**

1. Download `StockAnalyzer_Setup_Simple.exe` from [Releases](https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/releases)
2. Double-click the installer
3. Click "Install Now"
4. Click "Finish"
5. **Done!** App launches automatically!

**Features:**
- ✅ Installs to Program Files
- ✅ Desktop icon created automatically
- ✅ Launches immediately after install
- ✅ Built-in uninstaller
- ✅ Only 2-3 clicks needed!

📖 **Detailed guide**: See [ONE_CLICK_GUIDE.md](ONE_CLICK_GUIDE.md) | [INSTALL_FOR_USERS.md](INSTALL_FOR_USERS.md)

---

### 🔧 Option 3: Portable .exe (For Advanced Users)

1. Download `StockAnalyzer.exe`
2. Double-click to run
3. If Windows SmartScreen appears:
   - Click "More info"
   - Click "Run anyway"
   
   *(Note: SmartScreen warnings will disappear once the developer establishes reputation)*

### Option 3: Running from Python (For Developers)

1. **Install Python**: Download from https://www.python.org/ (3.8 or higher)

2. **Install dependencies**:
   ```batch
   pip install pandas numpy yfinance matplotlib mplfinance
   ```

3. **Run the application**:
   ```batch
   python manual_stock_analyzer.py
   ```

---

## How to Use

### Basic Usage

1. **Enter a Symbol**: Type a stock symbol (e.g., `AAPL`, `TSLA`) or crypto symbol (e.g., `BTC-USD`, `ETH-USD`)

2. **Click Analyze**: The app will fetch data and display the chart

3. **Customize View**:
   - Select different timeframes (1 day to Max)
   - Toggle moving averages (10, 20, 30, 50, 72, 100, 200, 400, 420-day)
   - Click "Update Chart" to apply changes

### Understanding the Chart

**Indicators shown:**
- 🟢 **Green dashed line**: Support level (20-day low)
- 🔴 **Red dashed line**: Resistance level (20-day high)
- 🟠 **Orange dashed line**: Calculated base price (entry point suggestion)
- 🟣 **Purple dashed line**: 5% below base price
- 📊 **RSI**: Displayed in title (Overbought >70, Oversold <30)

**Moving Averages:**
- Colored lines showing price trends over different periods
- Crossovers can indicate trend changes

### Example Symbols

**Stocks:**
- `AAPL` - Apple Inc.
- `MSFT` - Microsoft
- `GOOGL` - Google
- `TSLA` - Tesla
- `NVDA` - NVIDIA

**Cryptocurrencies:**
- `BTC-USD` - Bitcoin
- `ETH-USD` - Ethereum
- `ADA-USD` - Cardano
- `SOL-USD` - Solana

**Indices:**
- `^GSPC` - S&P 500
- `^DJI` - Dow Jones
- `^IXIC` - NASDAQ

---

## Troubleshooting

### "yfinance is required but not installed"
- **Solution**: Install with `pip install yfinance`

### "Charting libraries are required but not installed"
- **Solution**: Install with `pip install matplotlib mplfinance`

### "No data found for symbol"
- Check symbol spelling
- Try adding `-USD` for cryptocurrencies
- Some symbols may not have data for long timeframes

### Application won't start
- Ensure Python 3.8+ is installed
- Run `check_dependencies.bat` to verify installation
- Check console output for error messages

### SmartScreen Warning
- This is normal for new executables
- Click "More info" → "Run anyway"
- Once signed and distributed, warnings will disappear

---

## Building and Distribution

### Files Structure

```
Stock_Analyzer/
├── manual_stock_analyzer.py    # Main application
├── requirements.txt             # Python dependencies
├── stock_analyzer.spec          # PyInstaller config
├── build_exe.bat               # Build script
├── sign_exe.bat                # Signing script
├── check_dependencies.bat      # Dependency checker
├── README.md                   # This file
├── SIGNING_GUIDE.md            # Code signing guide
├── USER_GUIDE.md               # User documentation
└── dist/
    └── StockAnalyzer.exe       # Built executable
```

### Building Process

1. **Build**: `build_exe.bat` → Creates unsigned .exe
2. **Sign**: `sign_exe.bat` → Adds digital signature
3. **Distribute**: Share `StockAnalyzer.exe` with users

See [SIGNING_GUIDE.md](SIGNING_GUIDE.md) for details on obtaining and using code signing certificates.

---

## System Requirements

**Minimum:**
- Windows 10 or higher
- 4 GB RAM
- 500 MB free disk space
- Internet connection

**Recommended:**
- Windows 10/11
- 8 GB RAM
- 1 GB free disk space
- Stable internet connection

---

## Technical Details

### Architecture
- **GUI Framework**: tkinter (built into Python)
- **Data Source**: Yahoo Finance API via yfinance
- **Charting**: matplotlib + mplfinance
- **Data Processing**: pandas, numpy
- **Async**: Threading and concurrent.futures for non-blocking UI

### Performance Optimizations
- **Data Caching**: 5-minute TTL cache for API responses
- **Lazy Loading**: Heavy libraries loaded on-demand
- **Async Fetching**: Non-blocking data downloads
- **Thread Pool**: Concurrent processing for better responsiveness

---

## Development

### Project Structure

```python
manual_stock_analyzer.py
├── DataCache              # Caching system
├── calculate_indicators() # Technical indicators
├── get_base_price()      # Base price calculation
├── StockAnalyzerApp      # Main application class
│   ├── setup_ui()        # UI initialization
│   ├── analyze_stock()   # Stock analysis
│   ├── update_chart()    # Chart rendering
│   └── cleanup()         # Resource cleanup
└── main()                # Entry point
```

### Adding Features

To add new indicators or features:

1. Add calculation function in indicators section
2. Update `calculate_indicators()` to include new indicator
3. Modify `_on_chart_success()` to display the indicator
4. Update UI controls if needed

### Testing

```batch
# Run directly with Python for testing
python manual_stock_analyzer.py

# Check for import errors
python -c "import manual_stock_analyzer"

# Verify dependencies
python check_dependencies.bat
```

---

## License

This project is provided as-is for educational and commercial use.

---

## Disclaimer

⚠️ **Investment Disclaimer**: This tool is for educational and informational purposes only. It is not financial advice. Always do your own research and consult with financial professionals before making investment decisions. Past performance does not guarantee future results.

---

## Support

**Issues?**
- Check the [Troubleshooting](#troubleshooting) section
- Read [USER_GUIDE.md](USER_GUIDE.md)
- Review [SIGNING_GUIDE.md](SIGNING_GUIDE.md) for signing issues

**Questions about code signing?**
- See [SIGNING_GUIDE.md](SIGNING_GUIDE.md)
- Contact your certificate provider

---

## Changelog

### Version 1.0.0
- Initial release
- Stock and crypto technical analysis
- Interactive charts with MA support
- RSI and support/resistance indicators
- Multiple timeframe support
- Data caching for performance
- Professional UI with modern design

---

## Acknowledgments

- **yfinance**: Yahoo Finance API wrapper
- **mplfinance**: Financial charting library
- **matplotlib**: Plotting library
- **pandas**: Data analysis library

---

**Made with ❤️ for traders and investors**

