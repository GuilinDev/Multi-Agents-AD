FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    chromadb sentence-transformers pymupdf

COPY api/ .

EXPOSE 8000

# Ingest at startup (before uvicorn), then serve
CMD python3 knowledge_base/ingest.py && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
