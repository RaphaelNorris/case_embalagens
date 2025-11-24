# Multi-stage Dockerfile for ADAMI Production Optimization
# Optimized for production deployment

# ============================================================================
# Stage 1: Builder - Install dependencies
# ============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY project_data_science/pyproject.toml .
COPY project_data_science/README.md .
COPY project_data_science/src ./src

# Install Python dependencies
# Using pip instead of uv for broader compatibility
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# ============================================================================
# Stage 2: Runtime - Lean production image
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# Copy Python environment from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY project_data_science/src ./src
COPY project_data_science/models ./models
COPY project_data_science/data ./data

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
    PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import sys; from src.config import get_config; get_config(); sys.exit(0)" || exit 1

# Expose port for API (if applicable)
EXPOSE 8000

# Default command (can be overridden)
# For batch inference:
CMD ["python", "-m", "src.pipelines.inference.predict"]

# For API service (uncomment if using FastAPI):
# CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
