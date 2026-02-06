# ============================
# Stage 1 — Python dependencies
# ============================
FROM python:3.12-slim AS python-builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# ============================
# Stage 2 — Node + ESLint
# ============================
FROM node:20-slim AS node-builder
RUN npm install -g eslint


# ============================
# Stage 3 — Runtime Image
# ============================
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install minimal system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies
COPY --from=python-builder /root/.local /root/.local
ENV PATH="/root/.local/bin:${PATH}"

# Copy Node binaries (only what is needed)
COPY --from=node-builder /usr/local/bin/node /usr/local/bin/node
COPY --from=node-builder /usr/local/bin/npm /usr/local/bin/npm
COPY --from=node-builder /usr/local/bin/npx /usr/local/bin/npx
COPY --from=node-builder /usr/local/lib/node_modules /usr/local/lib/node_modules

# Copy ONLY policy.yml first (forces cache bust on policy changes)
COPY policy.yml ./policy.yml

# Copy the rest of the project
COPY . .

# Remove any old version of ai-slop-gate
RUN pip uninstall -y ai-slop-gate || true

# Install project
RUN pip install --no-cache-dir -e .

# Entrypoint
ENTRYPOINT ["ai-slop-gate"]
CMD ["--help"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import ai_slop_gate; print('OK')" || exit 1
