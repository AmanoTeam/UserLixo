FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libgl1 \
        libglib2.0-0 \
        tzdata \
        git \
        ffmpeg \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do projeto
COPY . .

# Comando para rodar o bot
CMD ["python", "bot.py"]
