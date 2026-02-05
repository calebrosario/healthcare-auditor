# Multi-stage Dockerfile for Healthcare Auditor Backend
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl

# Copy requirements files
COPY backend/pyproject.toml backend/poetry.lock* ./

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install --no-root

# Copy application code
COPY backend/. .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["poetry", "run", "uvicorn", "services.main:app", "--host", "0.0.0.0", "--port", "8000"]
