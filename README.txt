🧠 Jul.IA – Automação de Procuração e Consignado

Sistema completo para geração instantânea de procurações e documentos relacionados a contratos de empréstimo consignado.

Baseado em template DOCX 100% personalizável e totalmente automatizado, com saída em DOCX e PDF, já com a nomenclatura padrão:

02_Procuracao_Consig_Nome_Autor.docx
02_Procuracao_Consig_Nome_Autor.pdf


Desenvolvido para escritórios jurídicos que precisam de velocidade, padronização e escala na criação de documentos recorrentes.

✅ Funcionalidades
🔎 Entrada e processamento do bloco de dados

A aplicação recebe um bloco de texto no formato:

Nome completo: Marcia de Sá
Nacionalidade: Brasileira
Data de nascimento: 18/07/1986
Estado civil: Solteira
Profissão: Médica veterinária
RG: 87422194 - ESTADO: PR
CPF: 051.754.589-65
ENDEREÇO COMPLETO: Rua Miyo Tamura, nº: 70, complemento:
Bairro: Bom Jardim
CEP: 87047-732
CIDADE: Maringá, ESTADO: PR
WhatsApp COM DDD: 44 99142-0020
E-mail: ma.de.sa@hotmail.com


E automaticamente separa e organiza para preencher o documento.

✔ Quebra automática do endereço

Logradouro

Número

Complemento

Bairro

CEP

Cidade

Estado

✔ Padronização inteligente

RG → número - UF

Cidade/Estado → separados corretamente

Formatação de datas

WhatsApp limpo

Tratamento básico de acentos

📄 Geração de documentos (DOCX + PDF)
✔ Templates DOCX personalizados

O modelo base deve estar em:

app/documentos/documentos acao.docx


Ou qualquer .docx dentro da pasta documentos/.

✔ Preenchimento automático (docxtpl)

O sistema preenche o modelo com todos os dados parseados.

✔ Negrito inteligente no nome do cliente

O nome do cliente é deixado em negrito automaticamente em todo o documento, sem alterar a fonte do template (ex.: Montserrat).

✔ Nome dos arquivos (padrão obrigatório)

Sempre gerado como:

02_Procuracao_Consig_Nome_Autor.docx
02_Procuracao_Consig_Nome_Autor.pdf

✔ Conversão PDF

Ordem de tentativa:

docx2pdf

LibreOffice (soffice --headless)

Se ambos falharem, o sistema retorna o DOCX no padrão definido.

⚙ Tecnologias Utilizadas
Backend

🐍 Python 3.11

⚡ FastAPI

📦 Uvicorn

📝 docxtpl

📄 python-docx

🔄 docx2pdf

Frontend

🌐 HTML + CSS + JavaScript

Templates Jinja2 em app/templates/

PDF

🖥️ LibreOffice headless dentro do container Docker

🌍 Endpoints
Método	Rota	Descrição
GET	/	Interface principal
GET	/docx	Tela para geração de DOCX
GET	/pdf	Tela para geração de PDF
POST	/gerar-docx	Retorna DOCX com nome padronizado
POST	/gerar-pdf	Retorna PDF com nome padronizado (ou DOCX como fallback)
🛠 Como rodar localmente
1. Clone o repositório
git clone https://github.com/julianogarbuggio/julia-procuracao.git
cd julia-procuracao

2. Crie o ambiente virtual
python -m venv .venv


Ativar:

Windows:
.venv\Scripts\activate

Linux/macOS:
source .venv/bin/activate

3. Instale as dependências
pip install -r requirements.txt

4. Rode o servidor local
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


Acesse:

http://127.0.0.1:8000

☁ Deploy no Railway (Docker – recomendado)
1. O Dockerfile já está incluso no repositório:
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libreoffice && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

2. Deploy

Abra o Railway

Crie um novo projeto

Escolha Deploy from GitHub

Selecione julianogarbuggio/julia-procuracao

Railway detecta o Dockerfile automaticamente

Build → Deploy

Em Networking, habilite domínio público

Acesse

Pronto.

Sem variáveis de ambiente.
Tudo funciona out-of-the-box.

📂 Estrutura do Projeto
julia-procuracao/
│
├── app/
│   ├── documentos/
│   │   └── documentos acao.docx
│   ├── static/
│   │   └── styles.css
│   ├── templates/
│   │   ├── index.html
│   │   ├── docx.html
│   │   └── pdf.html
│   └── main.py
│
├── requirements.txt
├── Dockerfile
├── start_app.py (opcional)
└── README.md

📄 Licença

Este projeto é de propriedade de
Juliano Garbuggio – Advocacia & Consultoria

Powered by Jul.IA – Inteligência Jurídica Automatizada

👨‍💻 Autor

Juliano Garbuggio
Advogado & Desenvolvedor
📧 juliano@garbuggio.com.br

🌐 https://julianogarbuggio.adv.br

© 2025 Juliano Garbuggio - Advocacia & Consultoria | Powered by Jul.IA
