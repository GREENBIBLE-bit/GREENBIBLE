[Setup]
AppName=GREENBIBLE
AppVersion=1.0.0
AppPublisher=GREENBIBLE
DefaultDirName={localappdata}\GREENBIBLE
DefaultGroupName=GREENBIBLE
OutputDir=installer
OutputBaseFilename=GREENBIBLE_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
UninstallDisplayName=GREENBIBLE
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=greenbible.ico

[Files]
Source: "dist\GREENBIBLE\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
Source: "dist\GREENBIBLE\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\GREENBIBLE"; Filename: "{app}\GREENBIBLE.exe"; WorkingDir: "{app}"
Name: "{group}\GREENBIBLE"; Filename: "{app}\GREENBIBLE.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\GREENBIBLE.exe"; Description: "Launch GREENBIBLE"; Flags: nowait postinstall skipifsilent