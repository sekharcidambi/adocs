# Multi-stage Docker build for ADocS service with optimized caching
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

# Set environment variables for Python (cached layer)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building Python packages (cached layer)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment (cached layer)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy ONLY requirements first for better caching (cached layer)
COPY requirements-prod.txt /tmp/requirements.txt

# Install Python dependencies (cached layer - only rebuilds if requirements change)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim as runtime

# Set environment variables (cached layer)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies (cached layer)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage (cached layer)
COPY --from=builder /opt/venv /opt/venv

# Create non-root user for security (cached layer)
RUN groupadd -r adocs && useradd -r -g adocs adocs

# Create app directory and set ownership (cached layer)
WORKDIR /app
RUN chown -R adocs:adocs /app

# Create necessary directories (cached layer)
RUN mkdir -p /app/generated_docs /app/data /app/generated_wiki_docs && \
    chown -R adocs:adocs /app

# Copy application code LAST (this layer changes most frequently)
COPY --chown=adocs:adocs . .

# Make start.sh executable (cached layer)
RUN chmod +x /app/start.sh

# Switch to non-root user
USER adocs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["./start.sh"]
