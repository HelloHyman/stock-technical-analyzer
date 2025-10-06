; Stock Analyzer - Inno Setup Installer Script
; This creates a professional Windows installer for non-technical users

#define MyAppName "Stock Analyzer"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://github.com/HelloHyman/Automated-Stock-and-Crypto-Analyzer"
#define MyAppExeName "StockAnalyzer.exe"

[Setup]
; Basic Information
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation Directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=installer_output
OutputBaseFilename=StockAnalyzer_Setup_{#MyAppVersion}
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Visual Appearance
DisableWelcomePage=no
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

; Compatibility
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Uninstaller
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Documentation files (optional, include if they exist)
Source: "USER_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: ConvertToTxt('USER_GUIDE.md', 'User_Guide.txt')
Source: "QUICK_START.md"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: ConvertToTxt('QUICK_START.md', 'Quick_Start.txt')
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: ConvertToTxt('README.md', 'Readme.txt')

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\User Guide"; Filename: "{app}\User_Guide.txt"; Flags: createonlyiffileexists
Name: "{group}\Quick Start Guide"; Filename: "{app}\Quick_Start.txt"; Flags: createonlyiffileexists
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch shortcut (optional)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to launch after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Convert markdown files to txt for better Windows compatibility
procedure ConvertToTxt(SourceFile, DestFile: String);
var
  SourcePath, DestPath: String;
begin
  SourcePath := ExpandConstant('{app}\' + SourceFile);
  DestPath := ExpandConstant('{app}\' + DestFile);
  
  if FileExists(SourcePath) then
  begin
    FileCopy(SourcePath, DestPath, False);
    DeleteFile(SourcePath);
  end;
end;

// Custom welcome message
procedure InitializeWizard();
var
  WelcomePage: TWizardPage;
begin
  // You can customize the welcome message here
end;

// Check for internet connection (optional)
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = wpWelcome then
  begin
    MsgBox('Stock Analyzer requires an internet connection to fetch real-time stock data.' + #13#10#13#10 + 
           'Please ensure you have an active internet connection when using the application.', 
           mbInformation, MB_OK);
  end;
end;

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nStock Analyzer is a professional technical analysis tool for stocks and cryptocurrencies.%n%nFeatures:%n• Real-time stock and crypto data%n• Interactive charts with technical indicators%n• Multiple moving averages%n• RSI, Support/Resistance levels%n• Easy-to-use interface%n%nIt is recommended that you close all other applications before continuing.

