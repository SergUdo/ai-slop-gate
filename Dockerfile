# ============================
# Stage 7 — Python dependencies
# ============================
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .

# Install Python deps into /root/.local
RUN pip install --user --no-cache-dir -r requirements.txt


# ============================
# Stage 2 — Full Static + LLM Image
# ============================
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# ----------------------------
# Install system dependencies
# ----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    jq \
    unzip \
    ca-certificates \
    gnupg \
    bash \
    make \
    gcc \
    g++ \
    openssl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ----------------------------
# Install Node.js + npm + TypeScript
# ----------------------------
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && npm install -g typescript eslint npm-audit-resolver

# ----------------------------
# Install Terraform
# ----------------------------
RUN wget https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_amd64.zip \
    && unzip terraform_1.9.8_linux_amd64.zip \
    && mv terraform /usr/local/bin/terraform \
    && rm terraform_1.9.8_linux_amd64.zip

# ----------------------------
# Install kubectl
# ----------------------------
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# ----------------------------
# Install hadolint (Dockerfile linter)
# ----------------------------
RUN wget -O /usr/local/bin/hadolint \
    https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64 \
    && chmod +x /usr/local/bin/hadolint

# ----------------------------
# Install yq (YAML processor)
# ----------------------------
RUN wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 \
    -O /usr/local/bin/yq \
    && chmod +x /usr/local/bin/yq

# ----------------------------
# Copy Python dependencies
# ----------------------------
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:${PATH}"

# ----------------------------
# Copy project code
# ----------------------------
COPY . .

# Install project in editable mode
RUN pip install --no-cache-dir -e .

# ----------------------------
# Entrypoint
# ----------------------------
ENTRYPOINT ["python", "-m", "ai_slop_gate.cli.main"]
CMD ["--help"]

# ----------------------------
# Healthcheck
# ----------------------------
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import ai_slop_gate; print('OK')" || exit 1
