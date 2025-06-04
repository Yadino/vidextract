# syntax=docker/dockerfile:1

FROM python:3.10-slim AS base

# Set up working directory
WORKDIR /app

# --- Builder stage ---
FROM base AS builder

# Install system dependencies for Python packages (ffmpeg, libgl, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libavutil-dev \
        libavcodec-dev \
        libavformat-dev \
        libavdevice-dev \
        libavfilter-dev \
        libswscale-dev \
        libswresample-dev \
        libgl1 \
        libglib2.0-0 \
        git \
        && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY --link requirements.txt ./

# Install Python dependencies
RUN python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements.txt

# --- Final stage ---
FROM base AS final

# Install runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libavutil-dev \
        libavcodec-dev \
        libavformat-dev \
        libavdevice-dev \
        libavfilter-dev \
        libswscale-dev \
        libswresample-dev \
        libgl1 \
        libglib2.0-0 \
        && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m appuser

# Create necessary directories with proper permissions
RUN mkdir -p /app/output && \
    mkdir -p /app/logs && \
    chmod -R 777 /app/output && \
    chmod -R 777 /app/logs

USER appuser

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code and resources
COPY --link video_analyzer/ ./video_analyzer/
COPY --link api/ ./api/
COPY --link utils/ ./utils/
COPY --link models/ ./models/
COPY --link resources/ ./resources/
COPY --link config.py ./
COPY --link run.py ./
COPY --link event_db.py ./

# Set environment for venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Run the API server
CMD ["python", "api/run_api.py"] 