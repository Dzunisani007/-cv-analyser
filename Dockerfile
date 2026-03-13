FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for OCR + PDF rasterization (used by pdf2image + pytesseract)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.runtime.txt /app/requirements.runtime.txt
RUN pip install --no-cache-dir -r /app/requirements.runtime.txt

COPY app /app/app
COPY alembic.ini /app/alembic.ini
COPY migrations /app/migrations

ENV SERVICE_HOST=0.0.0.0 \
    SERVICE_PORT=8000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
