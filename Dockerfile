# ============================
# Stage 1 — Python dependencies
# ============================
FROM python:3.12-slim AS python-builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================
# Stage 2 — Security Tools & Node (External bins)
# ============================
FROM aquasec/trivy:latest AS trivy-bin
FROM anchore/syft:latest AS syft-bin
FROM node:20-slim AS node-binaries

# ============================
# Stage 3 — Runtime Image (Hardened)
# ============================
FROM python:3.12-slim

ARG BUILD_SHA
ENV APP_SHA=${BUILD_SHA}
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/root/.local/lib/python3.12/site-packages"

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && apt-get purge -y --auto-remove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=python-builder /root/.local /root/.local
COPY --from=node-binaries /usr/local/bin/node /usr/local/bin/node
COPY --from=node-binaries /usr/local/lib/node_modules /usr/local/lib/node_modules

COPY --from=trivy-bin /usr/local/bin/trivy /usr/local/bin/trivy
COPY --from=syft-bin /syft /usr/local/bin/syft
RUN chmod +x /usr/local/bin/trivy /usr/local/bin/syft

RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
    ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

COPY . .

RUN pip install --no-cache-dir --user --no-deps .

ENTRYPOINT ["ai-slop-gate"]
CMD ["--help"]

HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import ai_slop_gate; import github; print('OK')" || exit 1