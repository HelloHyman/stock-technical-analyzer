# Code Signing Guide for Stock Analyzer

This guide explains how to digitally sign your executable to prevent Windows SmartScreen warnings and establish trust with users.

## Table of Contents
1. [Why Sign Your Executable?](#why-sign-your-executable)
2. [Obtaining a Code Signing Certificate](#obtaining-a-code-signing-certificate)
3. [Signing Your Executable](#signing-your-executable)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Why Sign Your Executable?

Digital signatures provide:
- **Trust**: Users know the software comes from you and hasn't been tampered with
- **No SmartScreen Warnings**: Windows won't show scary warnings
- **Professional Appearance**: Shows you're a legitimate developer
- **Required for Distribution**: Many platforms require signed executables

---

## Obtaining a Code Signing Certificate

### Option 1: Commercial Certificate Authorities (Recommended for Commercial Use)

**Popular Providers:**
1. **DigiCert** (https://www.digicert.com/)
   - Cost: ~$400-600/year
   - EV Code Signing: ~$400-600/year
   - Most trusted, fastest reputation building

2. **Sectigo (formerly Comodo)** (https://sectigo.com/)
   - Cost: ~$200-400/year
   - Good balance of price and trust

3. **GlobalSign** (https://www.globalsign.com/)
   - Cost: ~$250-500/year
   - Good international presence

**Steps to Purchase:**
1. Visit provider website
2. Select "Code Signing Certificate" (for Windows applications)
3. Complete identity verification (business documents, personal ID)
4. Wait 3-7 days for approval
5. Receive certificate file (.pfx or .p12 format)

### Option 2: Self-Signed Certificate (For Testing/Internal Use ONLY)

⚠️ **WARNING**: Self-signed certificates will NOT remove SmartScreen warnings. Use only for testing.

**Create a self-signed certificate:**

```powershell
# Open PowerShell as Administrator
New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=Your Name" -CertStoreLocation "Cert:\CurrentUser\My" -NotAfter (Get-Date).AddYears(5)
```

**Export the certificate:**

```powershell
# Get the certificate thumbprint
Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert

# Export (replace THUMBPRINT with actual value)
$cert = Get-ChildItem Cert:\CurrentUser\My\THUMBPRINT
$pwd = ConvertTo-SecureString -String "YourPassword123" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath ".\mycert.pfx" -Password $pwd
```

---

## Signing Your Executable

### Method 1: Using SignTool (Windows SDK) - Recommended

**1. Install Windows SDK**
   - Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
   - Or install Visual Studio (includes SDK)
   - SignTool location: `C:\Program Files (x86)\Windows Kits\10\bin\<version>\x64\signtool.exe`

**2. Add SignTool to PATH** (Optional but convenient)
   ```batch
   set PATH=%PATH%;C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64
   ```

**3. Sign the executable:**

   **With PFX file:**
   ```batch
   signtool sign /f "path\to\certificate.pfx" /p "certificate_password" /t http://timestamp.digicert.com /fd SHA256 /v "dist\StockAnalyzer.exe"
   ```

   **With certificate in store:**
   ```batch
   signtool sign /n "Certificate Common Name" /t http://timestamp.digicert.com /fd SHA256 /v "dist\StockAnalyzer.exe"
   ```

   **Parameters explained:**
   - `/f`: Certificate file path
   - `/p`: Certificate password
   - `/n`: Certificate name (when using cert store)
   - `/t`: Timestamp server (important! certificates expire, timestamps don't)
   - `/fd SHA256`: Use SHA256 hash algorithm
   - `/v`: Verbose output

**4. Timestamp Servers** (Choose one):
   - DigiCert: `http://timestamp.digicert.com`
   - GlobalSign: `http://timestamp.globalsign.com/scripts/timstamp.dll`
   - Sectigo: `http://timestamp.sectigo.com`

### Method 2: Using Our Automated Script

**1. Create a signing configuration file** (`sign_config.txt`):
   ```
   CERT_FILE=path\to\your\certificate.pfx
   CERT_PASSWORD=your_certificate_password
   TIMESTAMP_URL=http://timestamp.digicert.com
   ```

**2. Run the signing script:**
   ```batch
   sign_exe.bat
   ```

**We've created this script for you** (see `sign_exe.bat` in project folder)

---

## Verification

### Verify the signature was applied:

**Using SignTool:**
```batch
signtool verify /pa /v "dist\StockAnalyzer.exe"
```

**Using Windows Explorer:**
1. Right-click `StockAnalyzer.exe`
2. Select "Properties"
3. Go to "Digital Signatures" tab
4. You should see your signature listed

**Using PowerShell:**
```powershell
Get-AuthenticodeSignature -FilePath "dist\StockAnalyzer.exe" | Format-List
```

---

## Building Reputation with SmartScreen

Even with a valid certificate, new certificates may trigger SmartScreen warnings initially. To build reputation:

1. **Use the same certificate** for all releases
2. **Consistent naming**: Keep the same executable name
3. **Distribution**: The more users download and run your app, the faster reputation builds
4. **Time**: Can take weeks to months depending on download volume
5. **EV Certificates**: Extended Validation certificates get instant reputation

---

## Complete Workflow

Here's the complete process from code to signed executable:

```batch
# 1. Build the executable
build_exe.bat

# 2. Sign the executable
signtool sign /f "mycert.pfx" /p "password" /t http://timestamp.digicert.com /fd SHA256 /v "dist\StockAnalyzer.exe"

# 3. Verify the signature
signtool verify /pa /v "dist\StockAnalyzer.exe"

# 4. Test the executable
dist\StockAnalyzer.exe

# 5. Distribute to users
```

---

## Troubleshooting

### "SignTool not found"
- Install Windows SDK
- Add SignTool to PATH
- Use full path to signtool.exe

### "Certificate not valid for signing"
- Ensure certificate has "Code Signing" extended key usage
- Check certificate hasn't expired

### "Timestamp server unavailable"
- Try different timestamp server
- Check internet connection
- Retry after a few minutes

### Still getting SmartScreen warnings
- Verify signature is present and valid
- Check certificate is from trusted CA (not self-signed)
- Wait for reputation to build
- Consider EV certificate for instant reputation

### Password prompt when signing
- Use `/p` parameter to provide password
- Or use certificate without password protection

---

## Cost Summary

| Option | Cost | SmartScreen Protection | Best For |
|--------|------|----------------------|----------|
| **Self-Signed** | Free | ❌ No | Testing only |
| **Standard Code Signing** | $200-600/year | ✅ Yes (after reputation) | Commercial software |
| **EV Code Signing** | $400-600/year | ✅ Yes (immediate) | Professional software |

---

## Alternative: Azure Key Vault Code Signing

For organizations, Azure provides cloud-based signing:
- No local certificate file needed
- Better security (keys never leave Azure)
- ~$50/month + certificate cost
- Requires Azure subscription

See: https://docs.microsoft.com/en-us/azure/key-vault/

---

## Additional Resources

- Microsoft SignTool Documentation: https://docs.microsoft.com/en-us/windows/win32/seccrypto/signtool
- Code Signing Best Practices: https://docs.microsoft.com/en-us/windows-hardware/drivers/dashboard/code-signing-best-practices
- SmartScreen FAQ: https://docs.microsoft.com/en-us/windows/security/threat-protection/microsoft-defender-smartscreen/

---

## Quick Reference: Sign Command

**Most common command:**
```batch
signtool sign /f "certificate.pfx" /p "password" /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 /v "dist\StockAnalyzer.exe"
```

Save this command with your certificate details for easy reuse!

---

**Need Help?** 
- Check that your certificate is valid and not expired
- Ensure the certificate purpose is "Code Signing"
- Verify the timestamp server is reachable
- Contact your certificate provider for support

