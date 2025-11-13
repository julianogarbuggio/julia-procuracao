@echo off
title Backup automático - Jul.IA Automação PDF & DOCX
cd /d "%~dp0"

echo ===============================================
echo    INICIANDO BACKUP AUTOMÁTICO DO PROJETO
echo ===============================================

set "BACKUP_FILE=julia-automacao-pdf-web-v3-backup.zip"

REM Cria o ZIP de todo o projeto exceto a pasta .venv\Lib (para não ficar enorme)
powershell -command "Compress-Archive -Path .\* -DestinationPath %BACKUP_FILE% -Force -CompressionLevel Optimal -Exclude '.venv\Lib\*'"

echo.
echo ✅ Backup concluído: %BACKUP_FILE%
echo ===============================================

REM Inicia o servidor normalmente após o backup
echo Iniciando servidor local na porta 8011...
call venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8011