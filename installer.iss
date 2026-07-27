; AETHER SEDC Wallet — Inno Setup Installer
; Install Inno Setup 6 (jrsoftware.org) then right-click this file → Compile

#define MyAppName "AETHER SEDC Wallet"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "AETHER SEDC"
#define MyAppURL "https://github.com/dony971/aether"
#define MyAppExeName "AETHER_Wallet.exe"

[Setup]
AppId={{B8A3C9E1-4F2D-4A6E-9C7B-8D1E2F3A4B5C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\AETHER Wallet
DefaultGroupName=AETHER SEDC
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=AETHER_Wallet_v{#MyAppVersion}_Setup
SetupIconFile=assets\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce
Name: "autostart"; Description: "Launch AETHER node on &startup"; GroupDescription: "Startup options:"; Flags: unchecked

[Files]
Source: "dist\AETHER_Wallet\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\AETHER SEDC Wallet"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\Uninstall AETHER Wallet"; Filename: "{uninstallexe}"
Name: "{autodesktop}\AETHER SEDC Wallet"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{userstartup}\AETHER Node"; Filename: "{app}\aether.exe"; Parameters: "--daemon --bootnodes 103.102.135.123:25565 --rpc-port 9933"; WorkingDir: "{app}"; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch AETHER SEDC Wallet"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\aether.exe"; Parameters: "--stop"; Flags: runhidden waituntilterminated

[Code]
function InitializeSetup: Boolean;
begin
  Result := True;
end;