# ============================
# Stage 1 — Python dependencies
# ============================
FROM python:3.12-slim AS python-builder
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install to /opt/venv instead of user directory
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ============================
# Stage 2 — Security Tools & Node (External bins)
# ============================
FROM aquasec/trivy:latest AS trivy-bin
FROM anchore/syft:latest AS syft-bin
FROM node:20-slim AS node-binaries

# ============================
# Stage 3 — Runtime Image (Hardened, Non-Root)
# ============================
FROM python:3.12-slim

ARG BUILD_SHA
ENV APP_SHA=${BUILD_SHA}
ENV DEBIAN_FRONTEND=noninteractive

# Create non-root user early
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home-dir=/app --shell=/sbin/nologin appuser

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && apt-get purge -y --auto-remove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python virtual environment
COPY --from=python-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/opt/venv/lib/python3.12/site-packages"

# Copy Node.js binaries
COPY --from=node-binaries /usr/local/bin/node /usr/local/bin/node
COPY --from=node-binaries /usr/local/lib/node_modules /usr/local/lib/node_modules

# Copy security tools
COPY --from=trivy-bin /usr/local/bin/trivy /usr/local/bin/trivy
COPY --from=syft-bin /syft /usr/local/bin/syft
RUN chmod +x /usr/local/bin/trivy /usr/local/bin/syft

# Create symlinks for npm/npx
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
    ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Copy application code
COPY --chown=appuser:appuser . .
RUN npm ci --omit=dev

# Install application
RUN /opt/venv/bin/pip install --no-cache-dir --no-deps .

# Create cache directory for Trivy (non-root writable)
RUN mkdir -p /app/.trivy-cache && chown -R appuser:appuser /app/.trivy-cache
ENV TRIVY_CACHE_DIR=/app/.trivy-cache

# Create cache directory for AI Slop Gate
RUN mkdir -p /app/.ai-slop-cache && chown -R appuser:appuser /app/.ai-slop-cache

# Switch to non-root user
USER appuser

ENTRYPOINT ["ai-slop-gate"]
CMD ["--help"]

# HEALTHCHECK for basic sanity check of Python environment and key dependencies
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import ai_slop_gate; import github; from google.genai import Client; print('OK')" || exit 1
  