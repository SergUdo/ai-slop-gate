# ============================
# Stage 1 — Python dependencies
# ============================
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt


# ============================
# Stage 2 — Runtime Image
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
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:${PATH}"

# Copy project code
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
