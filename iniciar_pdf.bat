@echo off
setlocal ENABLEDELAYEDEXPANSION

:: Ir para a pasta deste arquivo .bat
cd /d "%~dp0"

:: 1) Criar venv se não existir
if not exist ".venv\Scripts\activate.bat" (
  echo [Jul.IA] Criando ambiente virtual...
  python -m venv .venv
)

:: 2) Ativar venv
call .venv\Scripts\activate.bat

:: 3) Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

:: 4) Subir o servidor (porta 8011) e abrir o navegador
start "" http://127.0.0.1:8011
python -m uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload
