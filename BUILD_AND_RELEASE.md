# 🚀 Build and Release Guide

Quick guide for building and releasing Stock Analyzer packages.

---

## 📦 Step 1: Build All Packages

### Option A: Build Everything at Once (Recommended)

```batch
build_all_packages.bat
```

**This creates:**
- ✅ `dist\StockAnalyzer.exe` - Portable executable
- ✅ `StockAnalyzer_Portable.zip` - Portable package with one-click launcher
- ✅ `installer_output\StockAnalyzer_Setup_1.0.0_Simple.exe` - Simple installer
- ✅ `installer_output\StockAnalyzer_Setup_1.0.0.exe` - Standard installer

**Prerequisites:**
- Python 3.8+ installed
- [Inno Setup](https://jrsoftware.org/isdl.php) installed (for installers)

**Time:** ~5-10 minutes

---

### Option B: Build Individual Packages

**Just the executable:**
```batch
build_exe.bat
```
Output: `dist\StockAnalyzer.exe`

**Simple installer only:**
```batch
build_simple_installer.bat
```
Output: `installer_output\StockAnalyzer_Setup_1.0.0_Simple.exe`

**Standard installer only:**
```batch
build_installer.bat
```
Output: `installer_output\StockAnalyzer_Setup_1.0.0.exe`

---

## 🔐 Step 2: Sign the Packages (Optional but Recommended)

If you have a code signing certificate:

```batch
# Sign the executable
signtool sign /f "certificate.pfx" /p "password" /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 "dist\StockAnalyzer.exe"

# Sign the simple installer
signtool sign /f "certificate.pfx" /p "password" /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 "installer_output\StockAnalyzer_Setup_1.0.0_Simple.exe"

# Sign the standard installer
signtool sign /f "certificate.pfx" /p "password" /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 "installer_output\StockAnalyzer_Setup_1.0.0.exe"
```

Or use the signing script:
```batch
sign_exe.bat
```

See [docs/SIGNING_GUIDE.md](docs/SIGNING_GUIDE.md) for details on obtaining certificates.

---

## 📤 Step 3: Create GitHub Release

### A. Prepare Release Files

You should have:
- ✅ `StockAnalyzer_Portable.zip` (~50-80 MB)
- ✅ `installer_output\StockAnalyzer_Setup_1.0.0_Simple.exe` (~50-80 MB)
- ✅ `installer_output\StockAnalyzer_Setup_1.0.0.exe` (~50-80 MB)

### B. Create the Release on GitHub

1. **Go to your repository:**
   https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer

2. **Click "Releases"** (right sidebar)

3. **Click "Create a new release"**

4. **Fill in the details:**
   - **Tag version:** `v1.0.0`
   - **Release title:** `Stock Analyzer v1.0.0`
   - **Description:** (Copy from template below)

5. **Upload files:**
   - Drag and drop the 3 files to the upload area

6. **Click "Publish release"**

---

## 📝 Release Description Template

```markdown
# Stock Analyzer v1.0.0

Professional stock and cryptocurrency technical analysis tool for Windows.

## 📥 Download Options

### 🚀 Option 1: Portable Package (Easiest - Recommended)
**File:** `StockAnalyzer_Portable.zip`

**How to use:**
1. **Extract** the ZIP file
2. **Double-click** `StockAnalyzer_OneClick.bat` (ONE FILE - that's it!)
3. **Done!** Desktop icon created, Start Menu shortcut added, app launches automatically

✅ **Just ONE click** after extracting  
✅ No installation needed  
✅ Creates shortcuts automatically  
✅ Perfect for non-technical users  
✅ Includes user README file in the ZIP

---

### 💼 Option 2: Simple Installer (Traditional)
**File:** `StockAnalyzer_Setup_1.0.0_Simple.exe`

**How to install:**
1. Download and run the installer
2. Click "Install Now"
3. Click "Finish"
4. App launches automatically!

✅ Professional installation  
✅ Desktop icon created  
✅ Built-in uninstaller

---

### ⚙️ Option 3: Standard Installer (More Options)
**File:** `StockAnalyzer_Setup_1.0.0.exe`

**Full-featured installer with customization options.**

---

## ✨ Features

- Real-time stock and cryptocurrency data
- Interactive candlestick charts
- Moving averages (10, 20, 30, 50, 72, 100, 200, 400, 420-day)
- Technical indicators (RSI, Support/Resistance)
- Multiple timeframes (1 day to max history)
- Clean, modern interface
- No Python installation required

## 📋 System Requirements

- Windows 10 or Windows 11
- Internet connection
- 200 MB free disk space

## 🆘 Troubleshooting

**Windows SmartScreen Warning?**
1. Click "More info"
2. Click "Run anyway"
3. This is normal for new software

**Need help?** See the [User Guide](https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/blob/main/docs/USER_GUIDE.md)

## 📚 Documentation

- [User Guide](docs/USER_GUIDE.md)
- [Installation Guide](docs/INSTALL_FOR_USERS.md)
- [Quick Start](docs/QUICK_START.md)

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. Not financial advice.
Always do your own research and consult financial professionals before investing.

---

**Full Changelog:** [CHANGELOG.md](CHANGELOG.md)
```

---

## ✅ Post-Release Checklist

After publishing the release:

- [ ] Test download links work
- [ ] Verify all 3 packages download correctly
- [ ] Test portable package on clean PC
- [ ] Test simple installer on clean PC
- [ ] Update main README.md if needed
- [ ] Announce on social media (optional)
- [ ] Monitor for user feedback/issues

---

## 🔄 For Future Releases

### Update Version Numbers

**Before building next release:**

1. **Update VERSION file:**
   ```
   1.0.0 → 1.1.0
   ```

2. **Update CHANGELOG.md:**
   - Add new version section
   - List all changes

3. **Update version in installer files:**
   - `installer.iss` → Line 7: `#define MyAppVersion "1.1.0"`
   - `installer_simple.iss` → Line 7: `#define MyAppVersion "1.1.0"`

4. **Build packages:**
   ```batch
   build_all_packages.bat
   ```

5. **Create new release:**
   - Tag: `v1.1.0`
   - Upload new packages

---

## 🐛 Troubleshooting Build Issues

### "Python not found"
- Install Python 3.8+ from https://python.org
- Make sure to check "Add Python to PATH"

### "Inno Setup not found"
- Download from https://jrsoftware.org/isdl.php
- Install to default location

### "Module not found"
```batch
# Install dependencies
install_dependencies.bat
```

### "Build failed"
```batch
# Check dependencies
check_dependencies.bat
```

### "Installer build failed"
- Ensure `dist\StockAnalyzer.exe` exists
- Run `build_exe.bat` first
- Then run `build_installer.bat`

---

## 📊 Expected File Sizes

| File | Size | Type |
|------|------|------|
| `StockAnalyzer.exe` | 50-80 MB | Executable |
| `StockAnalyzer_Portable.zip` | 50-80 MB | ZIP archive |
| `StockAnalyzer_Setup_*_Simple.exe` | 50-80 MB | Installer |
| `StockAnalyzer_Setup_*.exe` | 50-80 MB | Installer |

---

## 🎯 Quick Reference

**Build everything:**
```batch
build_all_packages.bat
```

**Sign packages:**
```batch
sign_exe.bat
```

**Create release:**
1. Go to GitHub → Releases → New Release
2. Tag: `v1.0.0`
3. Upload 3 files
4. Publish

**Update version:**
1. Edit `VERSION` file
2. Update `installer.iss` and `installer_simple.iss`
3. Update `CHANGELOG.md`
4. Rebuild and release

---

## 📞 Need Help?

- Build issues? Check `check_dependencies.bat`
- Signing issues? See [docs/SIGNING_GUIDE.md](docs/SIGNING_GUIDE.md)
- Installer issues? See [docs/INSTALLER_GUIDE.md](docs/INSTALLER_GUIDE.md)

---

**Ready to build and release? Run `build_all_packages.bat` now!** 🚀

