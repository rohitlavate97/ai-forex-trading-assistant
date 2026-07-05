# ==============================================================================
# Production Dockerfile for Gradio Frontend
# ==============================================================================

FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY app.py .

EXPOSE 7860

# Run Gradio application
CMD ["python", "app.py"]
