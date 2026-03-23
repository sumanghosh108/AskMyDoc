# ============================================
# AskMyDoc Backend - Production Dockerfile
# FastAPI + ChromaDB (persistent) + Groq LLM
# Deploy on Render with a mounted disk at /data
# ============================================

FROM python:3.12-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy application code
COPY . .

# Create /data directory for ChromaDB persistence (Render mounts disk here)
RUN mkdir -p /data/chroma_db

# No local ML models to pre-download — embeddings use ChromaDB's built-in
# default (onnxruntime), and reranking uses Groq LLM API

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start FastAPI server
CMD ["python", "-m", "uvicorn", "src.api.router:app", "--host", "0.0.0.0", "--port", "8000"]
