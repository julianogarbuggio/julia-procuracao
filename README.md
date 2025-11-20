# Jul.IA – Automação de Procuração e Consignado

Sistema para geração automática de procurações e documentos de consignado em DOCX/PDF,
com layout otimizado para uso diário (desktop e celular) e pronto para deploy no Railway.

## Rodar localmente

```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Depois acesse: http://127.0.0.1:8000

## Deploy no Railway

- Crie um novo projeto a partir deste repositório (Deploy from GitHub).
- O Railway vai detectar o `Dockerfile`, instalar o LibreOffice + fontes necessárias
  e rodar automaticamente o comando com `uvicorn`.

Os arquivos gerados seguem o padrão:

- `02_Procuracao_Consig_Nome_Autor.docx`
- `02_Procuracao_Consig_Nome_Autor.pdf`
