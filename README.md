# 📈 Stock & Crypto Automated Analysis Tool

A comprehensive desktop application for analyzing stocks and cryptocurrencies with advanced technical and fundamental analysis capabilities, built with Python and modern GUI frameworks.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## 🚀 Quick Start

### **Option 1: Automated Setup (Recommended for Windows)**

1. **Download the ZIP file** from this repository
2. **Extract** the ZIP file to your desired location
3. **Right-click** on `build__exe.ps1` and select **"Run with PowerShell"**
   - This will automatically install Python 3.13, dependencies, and build the executable
4. **Find your executable** in: `dist\StockCryptoAnalyzer\StockCryptoAnalyzer.exe`

### **Option 2: Manual Python Setup**

1. **Download the ZIP file** and extract it
2. **Install Python 3.11+** from [python.org](https://www.python.org/downloads/)
3. **Open Command Prompt** in the extracted folder
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the application:**
   ```bash
   python main.py
   ```

## 📋 Features

### 📊 **Technical Analysis**
- **Interactive Charts** with Plotly integration
- **Moving Averages** (SMA, EMA, WMA)
- **Technical Indicators** (RSI, MACD, Bollinger Bands, Stochastic)
- **Support/Resistance Levels** with automatic detection
- **Trend Analysis** and pattern recognition
- **Multiple Timeframes** (1D, 5D, 1M, 3M, 6M, 1Y, 2Y, 5Y)

### 💼 **Fundamental Analysis**
- **5-Pillar Analysis System:**
  - Profitability metrics
  - Growth indicators
  - Balance sheet strength
  - Market position analysis
  - Forward outlook assessment
- **Financial Ratios** and key metrics
- **Earnings Calendar** integration
- **Analyst Recommendations** tracking

### 📈 **Options Analysis**
- **Options Chain** visualization
- **Implied Volatility** analysis
- **Greeks** calculation and display
- **Options Strategies** evaluation

### 📱 **Social Sentiment**
- **StockTwits Integration** for social sentiment
- **Sentiment Analysis** from social media
- **Trending Topics** and mentions tracking

### ⚡ **Performance & UX**
- **Fast Startup** with optimized loading
- **Modern GUI** built with Flet framework
- **Responsive Design** that adapts to different screen sizes
- **Real-time Data** updates
- **Caching System** for improved performance

## 🛠️ System Requirements

### **Minimum Requirements:**
- **Operating System:** Windows 10/11 (64-bit)
- **Python:** 3.11 or higher (3.13 recommended)
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB free space
- **Internet:** Required for real-time data

### **Recommended Setup:**
- **Python 3.13** (automatically installed with PowerShell script)
- **8GB+ RAM** for smooth operation
- **SSD Storage** for faster startup
- **Stable Internet Connection** for real-time data

## 📦 Installation Methods

### **Method 1: Automated PowerShell Setup (Easiest)**

1. Download the repository ZIP file
2. Extract to your desired location
3. **Right-click** on `build__exe.ps1`
4. Select **"Run with PowerShell"**
5. Follow the on-screen prompts

**What this script does:**
- ✅ Installs Python 3.13 automatically
- ✅ Sets Python 3.13 as system default
- ✅ Configures environment variables
- ✅ Installs all required dependencies
- ✅ Builds standalone executable
- ✅ Verifies installation

### **Method 2: Manual Python Installation**

```bash
# 1. Install Python 3.11+ from python.org
# 2. Open Command Prompt in project directory
# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

### **Method 3: Build Executable Only**

If you already have Python 3.11+ installed:

```bash
# Double-click BUILD_EXE.bat
# OR run manually:
python build_exe.py
```

## 🎯 How to Use

### **Getting Started:**

1. **Launch the Application**
   - Double-click `StockCryptoAnalyzer.exe` (if built)
   - OR run `python main.py`

2. **Enter Symbol**
   - Type any stock symbol (e.g., `AAPL`, `TSLA`, `MSFT`)
   - Type any crypto symbol (e.g., `BTC-USD`, `ETH-USD`, `ADA-USD`)

3. **Explore Analysis**
   - **Technical Charts:** Interactive charts with indicators
   - **Fundamental Data:** Financial metrics and ratios
   - **Options Data:** Options chains and Greeks (stocks only)
   - **Social Sentiment:** Recent mentions and sentiment
   - **Earnings Calendar:** Upcoming earnings dates

### **Navigation Tips:**
- Use **tabs** to switch between different analysis sections
- **Hover** over chart elements for detailed information
- **Click and drag** to zoom into specific time periods
- **Right-click** on charts for additional options

## 📁 Project Structure

```
Stock-and-Crypto-Analyzer/
├── 📄 main.py                    # Main application entry point
├── 📄 requirements.txt           # Python dependencies
├── 📄 setup.py                   # Package configuration
├── 📄 build_exe.py              # Automated build script
├── 📄 build__exe.ps1            # PowerShell setup script (Windows)
├── 📄 BUILD_EXE.bat             # One-click build for Windows
├── 📄 RUN_APP.bat               # Application launcher
├── 📄 StockCryptoAnalyzer.spec  # PyInstaller configuration
├── 📁 src/                      # Source code modules
│   ├── 📁 config/               # Configuration and constants
│   │   ├── constants.py         # Analysis thresholds and UI constants
│   │   └── dependencies.py      # Dependency checking
│   ├── 📁 data/                 # Data processing modules
│   │   ├── yahoo_client.py      # Yahoo Finance API client
│   │   ├── fundamental_analysis.py # Fundamental analysis functions
│   │   ├── options_analysis.py  # Options chain analysis
│   │   └── technical_analysis.py # Technical indicators
│   ├── 📁 ui/                   # User interface
│   │   └── main_app.py          # Main application class
│   └── 📁 utils/                # Utility modules
│       ├── exceptions.py        # Custom exceptions
│       ├── cache.py             # Data caching utilities
│       └── rate_limiter.py      # API rate limiting
└── 📄 README.md                 # This file
```

## 🔧 Building from Source

### **Automated Build (Recommended):**
```bash
# Windows - Double-click or run:
BUILD_EXE.bat

# PowerShell (with Python setup):
.\build__exe.ps1
```

### **Manual Build:**
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller StockCryptoAnalyzer.spec
```

### **Build Output:**
- **Location:** `dist/StockCryptoAnalyzer/`
- **Executable:** `StockCryptoAnalyzer.exe`
- **Size:** ~200MB (includes all dependencies)

## 🐛 Troubleshooting

### **Common Issues & Solutions:**

#### **"Python not found" Error**
```bash
# Solution: Install Python 3.11+ from python.org
# Make sure to check "Add Python to PATH" during installation
```

#### **"Module not found" Errors**
```bash
# Solution: Install dependencies
pip install -r requirements.txt

# Or upgrade pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### **"Permission denied" (PowerShell Script)**
```bash
# Solution: Run PowerShell as Administrator
# Right-click PowerShell → "Run as administrator"
```

#### **Executable Won't Start**
```bash
# Solution: Check Windows Defender/Antivirus
# Add exception for the executable folder
# Or run from Command Prompt to see error messages
```

#### **Slow Startup/Performance**
```bash
# Solutions:
# 1. First run is slower (loading dependencies)
# 2. Ensure stable internet connection
# 3. Close other applications
# 4. Use SSD storage for better performance
```

#### **Data Loading Issues**
```bash
# Solutions:
# 1. Check internet connection
# 2. Verify symbol is correct (e.g., BTC-USD not BTC)
# 3. Try different symbol
# 4. Restart application
```

### **Getting Help:**

1. **Check the logs** in the application directory
2. **Verify Python version:** `python --version`
3. **Check dependencies:** `pip list`
4. **Test internet connection** for data fetching
5. **Run from Command Prompt** to see detailed error messages

## 📊 Supported Symbols

### **Stocks:**
- **US Stocks:** AAPL, TSLA, MSFT, GOOGL, AMZN, etc.
- **International:** Include exchange suffix (e.g., TSX:SHOP, LON:VOD)

### **Cryptocurrencies:**
- **Major Cryptos:** BTC-USD, ETH-USD, ADA-USD, SOL-USD
- **Altcoins:** Most major cryptocurrencies supported
- **Format:** Always use "-USD" suffix for crypto symbols

### **Indices:**
- **Major Indices:** ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ)

## 🔄 Updates & Maintenance

### **Keeping Dependencies Updated:**
```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific packages
pip install --upgrade yfinance plotly pandas
```

### **Rebuilding Executable:**
```bash
# After updating dependencies, rebuild executable
python build_exe.py
```

## 📝 Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| **flet** | Modern GUI framework | ≥0.21.0 |
| **pandas** | Data manipulation | ≥2.0.0 |
| **numpy** | Numerical computing | ≥1.24.0 |
| **yfinance** | Financial data | ≥0.2.18 |
| **plotly** | Interactive charts | ≥5.15.0 |
| **matplotlib** | Additional plotting | ≥3.7.0 |
| **mplfinance** | Financial charts | ≥0.12.7 |
| **requests** | HTTP requests | ≥2.31.0 |
| **requests-cache** | Caching | ≥1.1.0 |
| **tenacity** | Retry logic | ≥8.2.0 |
| **pyinstaller** | Executable building | ≥5.13.0 |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### **Development Setup:**
```bash
# Clone the repository
git clone https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer.git

# Install development dependencies
pip install -r requirements.txt

# Run in development mode
python main.py
```

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Yahoo Finance** for providing financial data
- **Plotly** for interactive charting capabilities
- **Flet** for the modern GUI framework
- **Python Community** for excellent libraries

---

## 🎉 **Ready to Start?**

1. **Download** the ZIP file
2. **Extract** to your desired location
3. **Run** `build__exe.ps1` as Administrator
4. **Launch** your new Stock & Crypto Analyzer!

**Happy Trading! 📈🚀**

---

*Made with ❤️ for traders and investors*