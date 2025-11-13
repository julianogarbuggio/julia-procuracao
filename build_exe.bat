@echo off
setlocal
if not exist .venv (
  py -3 -m venv .venv
)
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller==6.10.0

REM Gera um EXE simples que chama o servidor local (janela console).
pyinstaller --noconfirm --onefile --name JulIA_Automacao start_app.py

echo.
echo EXE gerado em: dist\JulIA_Automacao.exe
echo Para iniciar, basta executar o EXE (ele abrirá na porta 8011).
