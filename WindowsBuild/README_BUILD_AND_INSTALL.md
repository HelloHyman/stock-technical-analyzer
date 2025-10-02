# Stock Technical Analyzer - Windows Installation Guide

## 📦 For End Users (Download and Run)

### Quick Start
1. Download the `StockAnalyzer.exe` file
2. Double-click to run - **No installation required!**
3. Enter any stock symbol (e.g., AAPL, MSFT, TSLA) and click "Analyze Stock"

### System Requirements
- Windows 10 or later
- Internet connection (to fetch stock data)
- No Python installation needed

### Features
- ✅ Real-time stock data analysis
- ✅ Interactive candlestick charts
- ✅ Multiple moving averages (10, 20, 30, 50, 72, 100, 200, 400-day)
- ✅ Support and Resistance levels
- ✅ RSI (Relative Strength Index) indicator
- ✅ Customizable timeframes (1 day to max history)
- ✅ Base price calculation for entry points

### How to Use
1. **Enter a stock symbol** in the input field (e.g., AAPL for Apple Inc.)
2. **Click "Analyze Stock"** or press Enter
3. **View stock information** - Company details, market cap, P/E ratio, etc.
4. **Customize the chart**:
   - Select different timeframes (1 day to max)
   - Toggle moving averages
   - Click "Update Chart" to apply changes
5. **Analyze the chart**:
   - Green dashed line = Support level
   - Red dashed line = Resistance level
   - Orange dashed line = Base price (potential entry)
   - Purple dashed line = 5% below base price
   - RSI indicator shown in the title

---

## 🛠️ For Developers (Building the Executable)

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Build Instructions

#### Option 1: Automated Build (Recommended)
1. Open Command Prompt or PowerShell
2. Navigate to the project directory:
   ```bash
   cd path\to\Stock_Profile\RedPanda
   ```
3. Run the build script (either one):
   ```bash
   BUILD.bat
   ```
   or
   ```bash
   WindowsBuild\build_windows.bat
   ```
4. Wait for the build to complete
5. Find your executable at: `WindowsBuild\dist\StockAnalyzer.exe`

#### Option 2: Manual Build
1. Install dependencies:
   ```bash
   pip install -r WindowsBuild\requirements.txt
   ```
2. Navigate to WindowsBuild folder and build:
   ```bash
   cd WindowsBuild
   pyinstaller --clean stock_analyzer.spec
   cd ..
   ```
3. Find your executable at: `WindowsBuild\dist\StockAnalyzer.exe`

### Distribution
After building, you can distribute the `StockAnalyzer.exe` file to anyone with Windows.
The executable is self-contained and includes all dependencies.

**File size:** Approximately 100-150 MB (includes Python runtime and all libraries)

### Optional: Add an Icon
1. Create or download an `.ico` file for your application
2. Save it as `icon.ico` in the WindowsBuild directory
3. Edit `WindowsBuild\stock_analyzer.spec` and change:
   ```python
   icon=None,
   ```
   to:
   ```python
   icon='icon.ico',
   ```
4. Rebuild the executable

### Troubleshooting

#### Build Fails
- **Error: "Python not found"**
  - Ensure Python is installed and added to PATH
  - Reinstall Python with "Add to PATH" option checked

- **Error: "Module not found"**
  - Run: `pip install -r requirements.txt`
  - Ensure you're using the correct Python environment

#### Runtime Issues
- **"Failed to execute script"**
  - Build with console enabled for debugging:
    - Edit `stock_analyzer.spec`: change `console=False` to `console=True`
    - Rebuild to see error messages

- **Antivirus blocking the .exe**
  - This is common with PyInstaller executables
  - Add an exception in your antivirus software
  - Consider code signing the executable (requires certificate)

### Advanced Configuration

#### Reduce File Size
Edit `stock_analyzer.spec`:
- Change `upx=True` to enable UPX compression (if installed)
- Add excludes for unused modules

#### Single Folder vs Single File
Current configuration creates a single .exe file (easier to distribute).
For faster startup, you can create a folder-based distribution:
- Change `a.binaries` collection method in the spec file

---

## 📝 Technical Details

### Dependencies
- **yfinance**: Real-time stock data from Yahoo Finance
- **mplfinance**: Financial chart visualization
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **matplotlib**: Plotting library
- **tkinter**: GUI framework (included with Python)

### Data Source
Stock data is fetched from Yahoo Finance API via the yfinance library.
Requires an active internet connection.

### Privacy
- No data is collected or sent anywhere except Yahoo Finance for stock data
- No user tracking or analytics
- All processing is done locally on your computer

---

## 🐛 Issues and Support

If you encounter any issues:
1. Check that you have an active internet connection
2. Verify the stock symbol is correct
3. Try a different timeframe if data doesn't load
4. For build issues, ensure all dependencies are installed

---

## 📜 License

This is a free tool for personal use. Stock data is provided by Yahoo Finance.
Always verify information and do your own research before making investment decisions.

**Disclaimer:** This tool is for informational purposes only and does not constitute financial advice.


