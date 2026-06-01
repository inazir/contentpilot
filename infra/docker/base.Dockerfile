FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl git ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir requests Pillow>=10.0.0 Pillow>=10.0.0
