# USANDO VERSÃO FIXA (Recomendado para estabilidade)
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalação de dependências do sistema
# build-essential: Compiladores GCC/G++ para pacotes nativos (tgcrypto, etc.)
# python3-dev: Headers para compilar pacotes C que se ligam ao Python (opencv, Pillow)
# libgl1: necessário para OpenCV/Pillow
# libglib2.0-0: CRÍTICO - Adicionado para resolver o ImportError do libgthread-2.0.so.0
# git: necessário para instalar dependências do GitHub (EdgeGPT, Gemini-API)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libgl1 \
        libglib2.0-0 \
        git \
        tzdata \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Instalação de dependências Python
# Esta etapa agora deve ser bem-sucedida, pois todas as ferramentas de compilação estão presentes.
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 600 -r requirements.txt

# Cópia do código
COPY . .

CMD ["python3", "bot.py"]
