# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --prefer-offline

COPY frontend/ ./
RUN npm run build
# Output: /app/frontend/dist/


# ── Stage 2: Python backend + static files ────────────────────────────────────
FROM python:3.11-slim AS backend

# System deps for Pillow, pdfplumber, pytesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Copy built frontend into backend/static/
COPY --from=frontend-builder /app/frontend/dist/ ./static/

# Persistent storage for uploaded files and SQLite DB
VOLUME ["/app/storage", "/app/data"]

# Database in /app/data so it survives restarts (mount a volume there)
ENV DATABASE_URL=sqlite:////app/data/cdms.db
ENV STORAGE_ROOT=/app/storage
ENV SECRET_KEY=change-me-in-production

EXPOSE 8000

# Run with seed on first start
CMD ["sh", "-c", "python seed_demo.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
