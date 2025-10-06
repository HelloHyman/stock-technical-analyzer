# Quick Start Guide - Stock Analyzer

Get up and running in minutes!

## 🚀 For End Users (Just Want to Run the App)

### Option 1: Using the .exe (Easiest)
1. Download `StockAnalyzer.exe`
2. Double-click to run
3. If Windows SmartScreen warning appears:
   - Click "More info"
   - Click "Run anyway"

**That's it! You're ready to analyze stocks!**

---

### Option 2: Running from Python

**Step 1: Install Python**
- Download from https://www.python.org/ (version 3.8 or higher)
- ✅ CHECK "Add Python to PATH" during installation

**Step 2: Install Dependencies**
- Double-click `install_dependencies.bat`
- Or manually run: `pip install pandas numpy yfinance matplotlib mplfinance`

**Step 3: Run the App**
- Double-click `manual_stock_analyzer.py`
- Or run: `python manual_stock_analyzer.py`

---

## 🛠️ For Developers (Building the .exe)

### Build Executable

**Easy Way:**
```batch
1. Double-click: build_exe.bat
2. Wait for build to complete (5-10 minutes)
3. Find your .exe in: dist\StockAnalyzer.exe
```

**Manual Way:**
```batch
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build
pyinstaller stock_analyzer.spec
```

---

## 🔐 Code Signing (Optional but Recommended)

### Quick Sign
1. Get a code signing certificate (see [SIGNING_GUIDE.md](SIGNING_GUIDE.md))
2. Run `sign_exe.bat`
3. Follow the prompts

### Manual Sign
```batch
signtool sign /f "certificate.pfx" /p "password" /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 "dist\StockAnalyzer.exe"
```

**Note**: Signing is optional but removes Windows SmartScreen warnings for users.

---

## 📊 Using the Application

### Quick Tutorial

1. **Enter a symbol**: `AAPL`, `BTC-USD`, `TSLA`
2. **Click "Analyze"**
3. **Customize**:
   - Change timeframe: 1 day to Max
   - Toggle moving averages
   - Click "Update Chart"

### Popular Symbols to Try

**Stocks:**
- `AAPL` - Apple
- `MSFT` - Microsoft
- `GOOGL` - Google
- `TSLA` - Tesla

**Crypto:**
- `BTC-USD` - Bitcoin
- `ETH-USD` - Ethereum
- `ADA-USD` - Cardano

**Indices:**
- `^GSPC` - S&P 500
- `^DJI` - Dow Jones

---

## ✅ Verification

### Check if everything is working:

**Option 1: Run the checker**
```batch
check_dependencies.bat
```

**Option 2: Manual check**
```batch
python -c "import pandas, numpy, yfinance, matplotlib, mplfinance"
```

If no errors = You're good to go! ✓

---

## 🆘 Common Issues

### "Python is not recognized"
- **Fix**: Install Python and check "Add to PATH"
- Or add Python to PATH manually

### "Module not found"
- **Fix**: Run `install_dependencies.bat`
- Or: `pip install -r requirements.txt`

### "No data found for symbol"
- **Fix**: Check symbol spelling
- Try adding `-USD` for crypto

### SmartScreen Warning
- **Fix**: Click "More info" → "Run anyway"
- Or get a code signing certificate

---

## 📁 File Structure

```
Stock_Analyzer/
├── manual_stock_analyzer.py    ← Main app
├── build_exe.bat              ← Build the .exe
├── sign_exe.bat               ← Sign the .exe
├── install_dependencies.bat   ← Install packages
├── check_dependencies.bat     ← Verify installation
├── requirements.txt           ← Package list
├── README.md                  ← Full documentation
├── USER_GUIDE.md             ← User manual
├── SIGNING_GUIDE.md          ← Code signing help
└── dist/
    └── StockAnalyzer.exe     ← Your executable
```

---

## 🎯 Next Steps

1. ✅ **Got it working?** Read [USER_GUIDE.md](USER_GUIDE.md) for tips
2. 🏗️ **Building .exe?** Run `build_exe.bat`
3. 🔐 **Want to sign?** Read [SIGNING_GUIDE.md](SIGNING_GUIDE.md)
4. 📚 **Need help?** Check [README.md](README.md)

---

## 🚀 Complete Workflow

### For Distribution:

```
1. Code → Build → Sign → Distribute
   ↓       ↓       ↓       ↓
   ✓       ✓       ✓       ✓
   Done    build   sign    Share
           _exe    _exe    .exe
           .bat    .bat    file
```

### Time Estimate:
- **Build**: 5-10 minutes
- **Sign**: 2-5 minutes (if you have certificate)
- **Total**: ~15 minutes

---

## 💡 Pro Tips

1. **Test before signing**: Run the .exe to make sure it works
2. **Keep certificate safe**: Backup your .pfx file
3. **Use same certificate**: Builds reputation faster
4. **Update regularly**: Keep dependencies current

---

## 📞 Support

- **Installation issues?** Run `check_dependencies.bat`
- **Build problems?** Check Python version (need 3.8+)
- **Signing questions?** See [SIGNING_GUIDE.md](SIGNING_GUIDE.md)
- **Usage help?** Read [USER_GUIDE.md](USER_GUIDE.md)

---

**That's it! You're ready to go. Happy analyzing! 📈**

---

### Quick Command Reference

```batch
# Install dependencies
install_dependencies.bat

# Check installation
check_dependencies.bat

# Run app from Python
python manual_stock_analyzer.py

# Build executable
build_exe.bat

# Sign executable
sign_exe.bat

# Test executable
dist\StockAnalyzer.exe
```

**Bookmark this page for quick reference!**

