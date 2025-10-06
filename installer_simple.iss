; Stock Analyzer - ULTRA-SIMPLE Installer
; Minimal clicks, maximum automation - perfect for non-technical users

#define MyAppName "Stock Analyzer"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Stock Analyzer Team"
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
DisableDirPage=yes

; Output
OutputDir=installer_output
OutputBaseFilename=StockAnalyzer_Setup_{#MyAppVersion}_Simple
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Visual Appearance
DisableWelcomePage=yes
DisableReadyPage=yes
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

; Compatibility
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Uninstaller
UninstallDisplayIcon={app}\{#MyAppExeName}

; Silent options - fewer prompts
AlwaysShowDirOnReadyPage=no
AlwaysShowGroupOnReadyPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "Create a Quick Launch shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Documentation files (optional)
Source: "USER_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "QUICK_START.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "INSTALL_FOR_USERS.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\User Guide"; Filename: "{app}\USER_GUIDE.md"; Flags: createonlyiffileexists
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut (checked by default)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch shortcut
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Automatically launch after installation (checked by default)
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent

[Messages]
; Custom welcome message (shown very briefly)
WelcomeLabel2=Stock Analyzer will be installed on your computer.%n%nClick Install to continue, or Cancel to exit.
; Simplified button text
ButtonInstall=&Install Now
ButtonNext=&Continue
ClickInstall=Click Install Now to begin installation.
SelectDirLabel3=Stock Analyzer will be installed in the following folder.
SelectDirBrowseLabel=To continue, click Install Now. To select a different folder, click Browse.
; Installation progress
InstallingLabel=Please wait while Stock Analyzer is being installed...
; Finish messages
FinishedLabel=Stock Analyzer has been successfully installed!%n%nYou can now launch the application.
FinishedLabelNoIcons=Stock Analyzer has been successfully installed!

[Code]
var
  ProgressPage: TOutputProgressWizardPage;

procedure InitializeWizard();
begin
  // Create a simple progress page
  ProgressPage := CreateOutputProgressPage('Installing Stock Analyzer', 
    'Please wait while Stock Analyzer is being set up on your computer.');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    ProgressPage.SetText('Installing files...', '');
    ProgressPage.SetProgress(0, 100);
  end;
  
  if CurStep = ssPostInstall then
  begin
    ProgressPage.SetText('Finalizing installation...', '');
    ProgressPage.SetProgress(100, 100);
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Show info about internet requirement
  if CurPageID = wpSelectTasks then
  begin
    MsgBox('Stock Analyzer requires an internet connection to fetch stock data.' + #13#10#13#10 + 
           'Make sure you''re connected to the internet when using the app.', 
           mbInformation, MB_OK);
  end;
end;

