# ═══════════════════════════════════════════════════════════════════════════
# OMNIX VISION — Dockerfile
# ═══════════════════════════════════════════════════════════════════════════
# Build:  docker build -t omnix-vision .
# Run:    docker run -p 8501:8501 omnix-vision
# Visit:  http://localhost:8501
# ═══════════════════════════════════════════════════════════════════════════

FROM python:3.12-slim

# ── System dependencies ───────────────────────────────────────────────────
# OpenCV needs libGL + glib; FFmpeg enables audio/video conversion.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────
WORKDIR /app

# ── Python dependencies (cached layer) ────────────────────────────────────
# Copy requirements first so Docker caches the pip install layer.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Application code ───────────────────────────────────────────────────────
COPY . .

# ── Create runtime data directories ───────────────────────────────────────
RUN mkdir -p data/backups assets/uploads assets/images

# ── Streamlit configuration ────────────────────────────────────────────────
# Disable telemetry and run headless inside the container.
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ── Expose port ────────────────────────────────────────────────────────────
EXPOSE 8501

# ── Health check ───────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# ── Launch ─────────────────────────────────────────────────────────────────
ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0"]
