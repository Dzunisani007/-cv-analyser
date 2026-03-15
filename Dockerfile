FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for OCR + PDF rasterization (used by pdf2image + pytesseract)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        poppler-utils \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.runtime.txt /app/requirements.runtime.txt
RUN pip install --no-cache-dir -r /app/requirements.runtime.txt

# Copy application code
COPY app /app/app
COPY alembic.ini /app/alembic.ini
COPY migrations /app/migrations

# Create storage directory
RUN mkdir -p ./.storage

# Environment variables
ENV SERVICE_HOST=0.0.0.0 \
    SERVICE_PORT=8000

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
