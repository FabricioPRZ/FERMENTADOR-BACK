FROM python:3.11-slim

WORKDIR /app

# Evita prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Mejora caché de Docker
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000