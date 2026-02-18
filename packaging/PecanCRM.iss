#define AppName "Pecan CRM"
#define AppVersion "0.1.0"
#define AppPublisher "Pecan Company"
#define AppExeName "PecanCRM.exe"

[Setup]
AppId={{A56D2D28-801F-4D74-9A31-2D392B587F77}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\PecanCRM
DefaultGroupName=Pecan CRM
OutputDir=dist
OutputBaseFilename=PecanCRM-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#AppExeName}

[Files]
Source: "dist\PecanCRM\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Pecan CRM"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\Pecan CRM"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch Pecan CRM"; Flags: nowait postinstall skipifsilent

[Code]
function HasOdbc18(): Boolean;
begin
  Result := RegKeyExists(HKLM64, 'SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 18 for SQL Server')
    or RegKeyExists(HKLM32, 'SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 18 for SQL Server');
end;

function InitializeSetup(): Boolean;
begin
  if not HasOdbc18() then
  begin
    MsgBox('ODBC Driver 18 for SQL Server is required before installing Pecan CRM.'#13#10 +
      'Install the driver and re-run setup.', mbCriticalError, MB_OK);
    Result := False;
  end
  else
  begin
    Result := True;
  end;
end;