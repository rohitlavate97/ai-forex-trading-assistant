# ==============================================================================
# Production Dockerfile for FastAPI Backend
# ==============================================================================

# --- Build Stage ---
FROM python:3.13-slim AS builder

WORKDIR /build

# Install system dependencies needed for compiling some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install virtualenv and build dependencies
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Runtime Stage ---
FROM python:3.13-slim AS runner

WORKDIR /app

# Install runtime dependencies (e.g. mysql client libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev-compat \
    libmariadb-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code
COPY src/ /app/src/

# Set Python path
ENV PYTHONPATH=/app

EXPOSE 8000

# Run FastAPI app with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
