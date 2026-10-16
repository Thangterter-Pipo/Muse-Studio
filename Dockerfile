FROM python:3.11-slim-bookworm

# Muse Studio internal logic Chromium Muse Studio internal logic
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    MUSE_STUDIO_HOME=/app \
    MUSE_STUDIO_HOST=0.0.0.0 \
    MUSE_STUDIO_PORT=18610 \
    MUSE_STUDIO_CHROMIUM=/usr/bin/chromium \
    MUSE_STUDIO_CDP_PORT=19210

WORKDIR /app

# Muse Studio internal logic Chromium、Muse Studio internal logic
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fonts-wqy-zenhei \
    fonts-freefont-ttf \
    procps \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Muse Studio internal logic Python Muse Studio internal logic
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Muse Studio internal logic
COPY admin.html app.py cdp.py config.py engine.py store.py version.json ./
COPY deploy/ ./deploy/
COPY extension/ ./extension/
COPY tools/ ./tools/

# Muse Studio internal logic
RUN mkdir -p /app/data/media /app/data/downloads /root/musestudio-profiles

VOLUME ["/app/data"]

EXPOSE 18610

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "18610"]
