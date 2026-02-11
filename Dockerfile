# ============================
# Stage 1 — Python dependencies
# ============================
FROM python:3.12-slim AS python-builder

WORKDIR /app

# Upgrade pip and install dependencies to a local folder
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================
# Stage 2 — Node binaries
# ============================
FROM node:20-slim AS node-binaries
# Just a placeholder stage to grab node assets reliably

# ============================
# Stage 3 — Runtime Image
# ============================
FROM python:3.12-slim

# Build-time argument to track image version
ARG BUILD_SHA
ENV APP_SHA=${BUILD_SHA}
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:${PATH}"

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=python-builder /root/.local /root/.local

# Safely copy Node.js and NPM from the node image
COPY --from=node-binaries /usr/local/bin/node /usr/local/bin/node
COPY --from=node-binaries /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Copy project files
COPY ai_slop_gate ./ai_slop_gate
COPY pyproject.toml ./
COPY policy.yml ./policy.yml

# Install the project in editable mode for the entrypoint to work
RUN pip install --no-cache-dir -e .

# Entrypoint configuration
ENTRYPOINT ["ai-slop-gate"]
CMD ["--help"]

# Ensure image is functional
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import ai_slop_gate; print('OK')" || exit 1