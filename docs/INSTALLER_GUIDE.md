# Creating a Windows Installer for Stock Analyzer

This guide shows you how to create a professional Windows installer that non-technical users can simply download and run.

## 🎯 What This Creates

A professional `StockAnalyzer_Setup_1.0.0.exe` installer that:
- ✅ Installs the app with a setup wizard
- ✅ Creates Start Menu shortcuts
- ✅ Optional Desktop shortcut
- ✅ Includes an uninstaller
- ✅ Bundles user documentation
- ✅ Works on any Windows 10/11 PC
- ✅ No Python or dependencies needed

**Users just download and double-click!**

---

## 📋 Prerequisites

### 1. Install Inno Setup (Free)

**Download:** https://jrsoftware.org/isdl.php

1. Download **innosetup-6.x.x.exe** (latest version)
2. Run the installer
3. Accept default settings
4. Click "Install"

**That's it!** Inno Setup is free, open-source, and trusted by thousands of developers.

---

## 🚀 Quick Start - Build the Installer

### One-Command Method (Easiest)

```batch
build_installer.bat
```

This will:
1. Build the .exe (if needed)
2. Create the installer
3. Output: `installer_output\StockAnalyzer_Setup_1.0.0.exe`

### Manual Method

```batch
# 1. Build the executable
build_exe.bat

# 2. Create the installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

---

## 📦 What Gets Installed

When users run your installer:

1. **Welcome Screen** - Professional introduction
2. **License Agreement** - (Optional, if you add one)
3. **Installation Location** - Default: `C:\Program Files\Stock Analyzer`
4. **Start Menu Shortcuts** - Launch app, guides, uninstall
5. **Desktop Icon** - Optional checkbox
6. **Installation Progress** - Progress bar
7. **Finish** - Option to launch immediately

### Installed Files

```
C:\Program Files\Stock Analyzer\
├── StockAnalyzer.exe       # Main application
├── User_Guide.txt          # User manual
├── Quick_Start.txt         # Quick reference
├── Readme.txt              # Documentation
└── unins000.exe            # Uninstaller
```

### Start Menu

```
Start Menu > Stock Analyzer >
├── Stock Analyzer          # Launch app
├── User Guide              # Open guide
├── Quick Start Guide       # Quick reference
└── Uninstall Stock Analyzer
```

---

## 🎨 Customizing the Installer

### Edit `installer.iss`

**Change Company Name:**
```iss
#define MyAppPublisher "Your Company Name"
```

**Change Version:**
```iss
#define MyAppVersion "1.0.0"
```

**Add a Custom Icon:**
```iss
SetupIconFile=myicon.ico
```

**Change Default Install Location:**
```iss
DefaultDirName={autopf}\My Custom Folder\{#MyAppName}
```

**Add More Files:**
```iss
[Files]
Source: "myfile.pdf"; DestDir: "{app}"; Flags: ignoreversion
```

---

## 🔐 Signing the Installer

**Why sign?** Remove SmartScreen warnings and build trust.

### Sign Both .exe and Installer

```batch
# 1. Build unsigned .exe
build_exe.bat

# 2. Sign the .exe
signtool sign /f "cert.pfx" /p "password" /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 "dist\StockAnalyzer.exe"

# 3. Build installer (includes signed .exe)
build_installer.bat

# 4. Sign the installer too
signtool sign /f "cert.pfx" /p "password" /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 "installer_output\StockAnalyzer_Setup_1.0.0.exe"
```

**See [SIGNING_GUIDE.md](SIGNING_GUIDE.md) for certificate details.**

---

## 📤 Distribution

### Option 1: GitHub Releases (Free)

1. Go to your repository: https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Title: `Stock Analyzer v1.0.0`
5. Upload: `StockAnalyzer_Setup_1.0.0.exe`
6. Publish release

**Users download from:**
`https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer/releases`

### Option 2: Your Website

Upload the installer and provide a download link:
```html
<a href="StockAnalyzer_Setup_1.0.0.exe" download>
  Download Stock Analyzer for Windows
</a>
```

### Option 3: Cloud Storage

- Google Drive
- Dropbox
- OneDrive
- Share the download link

---

## 📝 For End Users - Installation Instructions

**Simple instructions for your users:**

### How to Install

1. **Download** `StockAnalyzer_Setup_1.0.0.exe`
2. **Double-click** the downloaded file
3. If you see a SmartScreen warning:
   - Click **"More info"**
   - Click **"Run anyway"**
4. Follow the **setup wizard**
5. Click **"Install"**
6. **Done!** Launch from Start Menu

### System Requirements

- Windows 10 or Windows 11
- Internet connection (for stock data)
- 200 MB free disk space

### How to Uninstall

**Method 1:**
- Start Menu → Stock Analyzer → Uninstall Stock Analyzer

**Method 2:**
- Settings → Apps → Stock Analyzer → Uninstall

**Method 3:**
- Control Panel → Programs → Uninstall a program → Stock Analyzer

---

## 🧪 Testing Checklist

Before distributing, test on a clean PC:

- [ ] Installer runs without errors
- [ ] Files installed to correct location
- [ ] Start Menu shortcuts work
- [ ] Desktop shortcut works (if selected)
- [ ] Application launches successfully
- [ ] Can analyze stocks (internet required)
- [ ] Documentation files accessible
- [ ] Uninstaller works properly
- [ ] No leftover files after uninstall

---

## 🆚 Installer vs Standalone .exe

| Feature | Installer | Standalone .exe |
|---------|-----------|-----------------|
| **Ease of Use** | ✅ Professional setup | ⚠️ Manual placement |
| **Start Menu** | ✅ Automatic | ❌ No |
| **Uninstaller** | ✅ Included | ❌ Manual delete |
| **Updates** | ✅ Can detect old version | ⚠️ Manual |
| **Documentation** | ✅ Bundled | ⚠️ Separate download |
| **User Trust** | ✅✅ Looks professional | ⚠️ Less polished |
| **Distribution** | Single .exe file | Single .exe file |
| **File Size** | +2MB overhead | Smaller |

**Recommendation:** Use installer for general public distribution.

---

## 🔧 Advanced Options

### Add License Agreement

1. Create `LICENSE.txt`
2. Add to `installer.iss`:
```iss
[Setup]
LicenseFile=LICENSE.txt
```

### Silent Installation (for IT)

Users can install silently:
```batch
StockAnalyzer_Setup_1.0.0.exe /VERYSILENT /NORESTART
```

### Custom Install Directory

Let users choose installation path (already enabled in default config).

### Update Detection

Installer can detect and upgrade existing installations automatically.

---

## 📊 File Size Comparison

Typical sizes:
- **StockAnalyzer.exe**: ~50-80 MB (standalone)
- **Installer**: ~52-82 MB (includes .exe + Inno Setup overhead)

Inno Setup compresses files, so installer might be similar size or even smaller!

---

## ❓ Troubleshooting

### "ISCC.exe not found"
**Solution:** Install Inno Setup from https://jrsoftware.org/isdl.php

### "Unable to open file dist\StockAnalyzer.exe"
**Solution:** Run `build_exe.bat` first to create the .exe

### "Installer won't run"
**Solution:** Check that you're running on Windows 10+ (64-bit)

### "Files not included in installer"
**Solution:** Check paths in `[Files]` section of `installer.iss`

### "Start Menu shortcuts missing"
**Solution:** Run installer as Administrator

### Users get SmartScreen warning
**Solution:** 
- Expected for unsigned software
- Get a code signing certificate (see SIGNING_GUIDE.md)
- Or instruct users: "More info" → "Run anyway"

---

## 🎓 Learning Resources

**Inno Setup Documentation:**
- Official Docs: https://jrsoftware.org/ishelp/
- Examples: `C:\Program Files (x86)\Inno Setup 6\Examples\`
- Script Reference: https://jrsoftware.org/ishelp/index.php?topic=scriptcode

**Video Tutorials:**
- Search YouTube for "Inno Setup tutorial"
- Many step-by-step guides available

---

## 🔄 Update Workflow

When releasing updates:

```batch
# 1. Update version in installer.iss
#define MyAppVersion "1.1.0"

# 2. Rebuild everything
build_installer.bat

# 3. Output: StockAnalyzer_Setup_1.1.0.exe

# 4. Upload to GitHub Releases as new version
```

Inno Setup can detect older installations and upgrade them automatically.

---

## 📋 Complete Workflow

### For First Release

```batch
1. Edit installer.iss (set your company name, etc.)
2. Run: build_installer.bat
3. Test installer on clean PC
4. (Optional) Sign installer
5. Upload to GitHub Releases
6. Share download link with users
```

### Time Estimate
- Setup Inno Setup: 5 minutes
- Build installer: 2-5 minutes
- Testing: 10 minutes
- **Total: ~20 minutes**

---

## ✅ Checklist: Ready to Distribute?

Before sharing with users:

- [ ] Inno Setup installed
- [ ] Ran `build_installer.bat` successfully
- [ ] Tested installer on clean Windows PC
- [ ] Application launches and works
- [ ] Start Menu shortcuts work
- [ ] Uninstaller works
- [ ] (Optional) Signed with certificate
- [ ] Uploaded to GitHub Releases or website
- [ ] Created download instructions for users

---

## 🎉 Success!

You now have a **professional Windows installer** that anyone can use!

**Users no longer need:**
- ❌ Python installation
- ❌ Pip commands
- ❌ Technical knowledge
- ❌ Command line

**They just:**
1. ✅ Download
2. ✅ Double-click
3. ✅ Next → Next → Install
4. ✅ Done!

---

## 💡 Pro Tips

1. **Version Numbers**: Keep version in sync across:
   - `installer.iss`
   - GitHub release tags
   - Your documentation

2. **Test Thoroughly**: Always test on a clean PC before public release

3. **Sign Everything**: If you have a certificate, sign both .exe and installer

4. **Update Regularly**: Keep dependencies current and release updates

5. **User Feedback**: Include a way for users to contact you (GitHub issues, email)

---

**Need Help?**
- Check Inno Setup docs: https://jrsoftware.org/ishelp/
- Review example scripts in Inno Setup installation folder
- See SIGNING_GUIDE.md for code signing

**Ready to build your installer? Run `build_installer.bat` now!** 🚀

