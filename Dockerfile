FROM python:3.11-slim

# Instala dependências do sistema para o Z3
RUN apt-get update && apt-get install -y \
    z3 \
    libz3-dev \
    && rm -rf /var/lib/apt/lists/*

# Cria um usuário para o Hugging Face (segurança)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
ENV PYTHONPATH="/app"

WORKDIR /app

# Instala requisitos do Python
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copia o restante do código
COPY --chown=user . .

# Comando para rodar a API da Aethel
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
