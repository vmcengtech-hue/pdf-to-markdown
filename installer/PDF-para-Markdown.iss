#define AppName "PDF para Markdown"
#define AppVersion "0.1.0"
#define AppExeName "PDF para Markdown.exe"

[Setup]
AppId={{9D71B178-FE10-4DB1-AEAD-8869D3CCB084}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=PDF para Markdown contributors
DefaultDirName={localappdata}\Programs\PDF para Markdown
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
OutputDir=dist-installer
OutputBaseFilename=PDF-para-Markdown-Setup-{#AppVersion}-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\PDF para Markdown\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\PDF para Markdown"; Filename: "{app}\{#AppExeName}"

[Registry]
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.pdf\shell\PDFtoMarkdown"; ValueType: string; ValueName: ""; ValueData: "Converter para Markdown"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.pdf\shell\PDFtoMarkdown"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#AppExeName},0"
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\.pdf\shell\PDFtoMarkdown\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""
