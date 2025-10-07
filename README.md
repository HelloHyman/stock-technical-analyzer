# Stock and Crypto Automated Analysis Tool

A comprehensive desktop application for analyzing stocks and cryptocurrencies with both technical and fundamental analysis capabilities.

## 🚀 Quick Start - One-Click Build

**For Windows users who want to create an executable:**

1. **Double-click `BUILD_EXE.bat`** - That's it! 
   - The script will automatically install all dependencies
   - Build a standalone Windows executable
   - Create the final `.exe` file ready to distribute

2. **Find your executable** in: `dist/StockCryptoAnalyzer/StockCryptoAnalyzer.exe`

## 📋 Features

- **Interactive Charts** with moving averages and technical indicators
- **5-Pillar Fundamental Analysis** (Profitability, Growth, Balance Sheet, Market Position, Forward Outlook)
- **Social Sentiment Analysis** from StockTwits
- **Options Chain Evaluation**
- **Earnings Calendar Integration**
- **Support/Resistance Levels** and RSI analysis
- **Customizable Timeframes** and chart settings
- **Fast Startup** and optimized performance

## 🛠️ Manual Installation (Alternative Method)

If you prefer to run the Python script directly:

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or download** this repository
2. **Open Command Prompt** in the project directory
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```bash
   python SC_Automated_Analysis.py
   ```

## 📦 Dependencies

The application uses the following main libraries:

- **flet** - Modern GUI framework
- **pandas & numpy** - Data analysis
- **yfinance** - Financial data from Yahoo Finance
- **plotly** - Interactive charts
- **matplotlib** - Additional plotting capabilities
- **requests** - HTTP requests for data fetching

## 🎯 How to Use

1. **Launch the application** (either the `.exe` file or Python script)
2. **Enter a stock or crypto symbol** (e.g., AAPL, BTC-USD, TSLA)
3. **Explore the analysis:**
   - Technical charts with indicators
   - Fundamental analysis breakdown
   - Options data (for stocks)
   - Social sentiment
   - Earnings calendar

## 📁 Project Structure

```
Stock and Crypto Automated analysis/
├── SC_Automated_Analysis.py    # Main application file
├── requirements.txt            # Python dependencies
├── setup.py                   # Package setup configuration
├── build_exe.py               # Automated build script
├── BUILD_EXE.bat              # One-click build for Windows
├── README.md                  # This file
└── dist/                      # Generated executable (after build)
    └── StockCryptoAnalyzer/
        └── StockCryptoAnalyzer.exe
```

## 🔧 Building from Source

### Automated Build (Recommended)
```bash
# Windows
BUILD_EXE.bat

# Or manually run the build script
python build_exe.py
```

### Manual Build
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name StockCryptoAnalyzer SC_Automated_Analysis.py
```

## 🐛 Troubleshooting

### Common Issues

1. **"Python not found"**
   - Install Python from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH" during installation

2. **"Module not found" errors**
   - Run: `pip install -r requirements.txt`
   - Make sure you're in the correct directory

3. **Executable won't start**
   - Try running from Command Prompt to see error messages
   - Make sure all dependencies were installed correctly

4. **Slow startup**
   - First run may be slower as it loads all dependencies
   - Subsequent runs should be faster

### Getting Help

- Check the `BUILD_INFO.txt` file after building
- Ensure you have a stable internet connection for data fetching
- Make sure Windows Defender or antivirus isn't blocking the executable

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

**Made with ❤️ for traders and investors**
