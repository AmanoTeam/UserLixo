FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalação de dependências do sistema
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

# Diretório de trabalho
WORKDIR /app

# Instalação de dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 600 -r requirements.txt

# Cópia do código
COPY . .

CMD ["python3", "bot.py"]
