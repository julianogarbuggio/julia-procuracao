# Dockerfile para Jul.IA – Automação de Procuração
FROM python:3.11-slim

# Evitar prompt interativo do apt
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instala dependências do sistema (LibreOffice para conversão em PDF)
RUN apt-get update && \
    apt-get install -y libreoffice && \
    rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Comando de inicialização
# Railway seta a variável PORT automaticamente
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

