FROM python:3.14-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY src/ /app/

# Porta do Panel
EXPOSE 5006

# Executa o dashboard
CMD ["panel", "serve", "Dashboard.ipynb", "--autoreload", "--address", "0.0.0.0", "--port", "5006"]
