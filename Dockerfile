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
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade "pip>=26.2.0" && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ============================
# Stage 2 — Security Tools & Node (External bins)
# ============================
FROM aquasec/trivy:0.74.0 AS trivy-bin
FROM ghcr.io/anchore/syft:v1.51.1 AS syft-bin
FROM node:22-slim AS node-binaries

# ============================
# Stage 3 — Runtime Image (Hardened, Non-Root)
# ============================
FROM python:3.12-slim

ARG BUILD_SHA
ENV APP_SHA=${BUILD_SHA}
ENV DEBIAN_FRONTEND=noninteractive

# OCI Labels
LABEL org.opencontainers.image.source="https://github.com/SergUdo/ai-slop-gate"
LABEL org.opencontainers.image.description="Policy-driven AI, supply-chain and compliance gate"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.revision="${BUILD_SHA}"

# Create non-root user early
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home-dir=/app --shell=/sbin/nologin appuser

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tar \
    && apt-get purge -y --auto-remove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- NEW: remove base image's own system pip (CVE-2026-8643, HIGH) ---
# Unused at runtime: the app and its deps are installed exclusively via
# /opt/venv/bin/pip (see Stage 1 and the `pip install -e ".[dev]"` step below).
RUN /usr/local/bin/python3 -m pip uninstall -y pip setuptools wheel 2>/dev/null || true && \
    rm -rf /usr/local/lib/python3.12/site-packages/pip* \
           /usr/local/lib/python3.12/site-packages/setuptools* \
           /usr/local/lib/python3.12/site-packages/wheel* \
           /usr/local/lib/python3.12/site-packages/pkg_resources \
           /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.12
# --- END NEW ---

WORKDIR /app

# Copy Python virtual environment
COPY --from=python-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/opt/venv/lib/python3.12/site-packages"

# Copy Node.js binaries
COPY --from=node-binaries /usr/local/bin/node /usr/local/bin/node
COPY --from=node-binaries /usr/local/lib/node_modules /usr/local/lib/node_modules

# Create symlinks for npm/npx
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
    ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Update npm to latest
RUN npm install -g npm@latest tar@7.5.22 && \
    npm install -g ts-prune && \
    npm cache clean --force

# Verify npm/npx work
RUN node --version && npm --version && npx --version && (ts-prune -v || true)

# Copy security tools
COPY --from=trivy-bin /usr/local/bin/trivy /usr/local/bin/trivy
COPY --from=syft-bin /syft /usr/local/bin/syft
RUN chmod +x /usr/local/bin/trivy /usr/local/bin/syft

# Copy application code
COPY --chown=appuser:appuser . .

# Install project dependencies with updated packages
RUN npm ci --omit=dev && \
    npm cache clean --force

# Install application
RUN /opt/venv/bin/pip install --no-cache-dir -e ".[dev]"

# Create cache directories
RUN mkdir -p /app/.trivy-cache /app/.ai-slop-cache && \
    chown -R appuser:appuser /app/.trivy-cache /app/.ai-slop-cache

ENV TRIVY_CACHE_DIR=/app/.trivy-cache

# Switch to non-root user
USER appuser

ENTRYPOINT ["ai-slop-gate"]
CMD ["--help"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import ai_slop_gate; import github; from google.genai import Client; print('OK')" || exit 1
  