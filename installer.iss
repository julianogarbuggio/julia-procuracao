; Inno Setup stub - ajustável se quiser empacotar o EXE com instalador
[Setup]
AppName=Jul.IA Automacao
AppVersion=LEGACY V2
DefaultDirName={pf}\JulIA\Automacao
DefaultGroupName=JulIA
OutputBaseFilename=JulIA_Automacao_Installer
[Files]
Source: "dist\JulIA_Automacao.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\JulIA Automacao"; Filename: "{app}\JulIA_Automacao.exe"
