FROM python:3.11-slim AS builder
WORKDIR /app

#dependencies 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

ENV PYTHONUNBUFFERED=1

CMD ['./docker-entrypoint.sh']