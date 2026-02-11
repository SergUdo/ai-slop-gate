# ============================
# Stage 1 — Python dependencies
# ============================
FROM python:3.12-slim AS python-builder

WORKDIR /app

# Install build-essential if any of your dependencies need to compile C extensions
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

COPY requirements.txt .
# Install dependencies to a specific prefix to avoid path issues
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================
# Stage 2 — Node binaries
# ============================
FROM node:20-slim AS node-binaries

# ============================
# Stage 3 — Runtime Image
# ============================
FROM python:3.12-slim

ARG BUILD_SHA
ENV APP_SHA=${BUILD_SHA}
ENV DEBIAN_FRONTEND=noninteractive
# Set Python path to include our installed packages
ENV PYTHONPATH="/usr/local/lib/python3.12/site-packages"

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all installed dependencies from builder directly to /usr/local
COPY --from=python-builder /install /usr/local

# Copy Node.js from the node image
COPY --from=node-binaries /usr/local/bin/node /usr/local/bin/node
COPY --from=node-binaries /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Copy project files - explicitly copy what is needed
COPY ai_slop_gate/ ./ai_slop_gate/
COPY pyproject.toml .
COPY policy.yml .
# If you have a README or other files required by pyproject.toml, copy them:
# COPY README.md . 

# Regular install (NOT editable) for production stability
RUN pip install --no-cache-dir .

# Final environment cleanup
RUN apt-get purge -y --auto-remove && apt-get clean

ENTRYPOINT ["ai-slop-gate"]
CMD ["--help"]

HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import ai_slop_gate; import github; print('OK')" || exit 1