# Stock Technical Analyzer 📈

A Windows desktop application for analyzing stock technical indicators with interactive charts.

## 🚀 Quick Start

### For Users (Download & Run)
1. Download `StockAnalyzer.exe` from the releases
2. Double-click to run - **No installation needed!**
3. Enter any stock symbol (e.g., AAPL, MSFT, TSLA)
4. Click "Analyze Stock"

### For Developers (Build from Source)
Simply run in the project root:
```bash
BUILD.bat
```

The executable will be created at: `WindowsBuild\dist\StockAnalyzer.exe`

📖 **Full documentation**: See `WindowsBuild\README_BUILD_AND_INSTALL.md`

## ✨ Features

- ✅ Real-time stock data from Yahoo Finance
- ✅ Interactive candlestick charts
- ✅ Multiple moving averages (10, 20, 30, 50, 72, 100, 200, 400-day)
- ✅ Support/Resistance levels (20-day)
- ✅ RSI (Relative Strength Index) indicator
- ✅ Base price calculation for entry points
- ✅ Customizable timeframes (1 day to max history)
- ✅ Clean, modern UI

## 📋 Requirements

### End Users
- Windows 10 or later
- Internet connection

### Developers
- Python 3.8 or higher
- Dependencies in `WindowsBuild\requirements.txt`

## 📂 Project Structure

```
RedPanda/
├── manual_stock_analyzer.py    # Main application code
├── BUILD.bat                    # Quick build launcher
├── WindowsBuild/                # Packaging files
│   ├── requirements.txt         # Python dependencies
│   ├── stock_analyzer.spec      # PyInstaller config
│   ├── build_windows.bat        # Detailed build script
│   ├── run_source.bat           # Run from source
│   ├── README_BUILD_AND_INSTALL.md  # Full docs
│   └── QUICK_START.txt          # Quick reference
└── README.md                    # This file
```

## 🛠️ Technical Stack

- **GUI**: Tkinter
- **Data**: yfinance (Yahoo Finance API)
- **Charts**: mplfinance, matplotlib
- **Analysis**: pandas, numpy
- **Packaging**: PyInstaller

## 📊 How to Use

1. **Enter Stock Symbol**: Type any valid stock ticker (e.g., AAPL, GOOGL, TSLA)
2. **View Information**: Company details, market cap, P/E ratio, 52-week highs/lows
3. **Customize Chart**:
   - Select timeframe (1 day to max history)
   - Toggle moving averages
   - Click "Update Chart" to refresh
4. **Analyze Indicators**:
   - 🟢 Green dashed line = Support level
   - 🔴 Red dashed line = Resistance level  
   - 🟠 Orange dashed line = Base price (potential entry point)
   - 🟣 Purple dashed line = 5% below base price
   - RSI shown in chart title (>70 = overbought, <30 = oversold)

## ⚠️ Disclaimer

This tool is for informational and educational purposes only. It does not constitute financial advice. Always do your own research and consult with financial professionals before making investment decisions.

## 📜 License

Free for personal use. Stock data provided by Yahoo Finance.

---

**Questions?** Check the full documentation in `WindowsBuild\README_BUILD_AND_INSTALL.md`

