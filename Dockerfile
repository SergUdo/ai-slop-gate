FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# ----------------------------
# Install system tools + Node + Terraform + kubectl + linters
# ----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget git jq unzip ca-certificates gnupg bash make gcc g++ openssl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update && apt-get install -y nodejs \
    && npm install -g typescript eslint npm-audit-resolver \
    && wget https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_amd64.zip \
    && unzip terraform_1.9.8_linux_amd64.zip \
    && mv terraform /usr/local/bin/terraform \
    && rm terraform_1.9.8_linux_amd64.zip \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl && mv kubectl /usr/local/bin/ \
    && wget -O /usr/local/bin/hadolint \
       https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64 \
    && chmod +x /usr/local/bin/hadolint \
    && wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 \
       -O /usr/local/bin/yq \
    && chmod +x /usr/local/bin/yq \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Install Python dependencies
# ----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Copy project code
# ----------------------------
COPY . .

# Remove any old version (important!)
RUN pip uninstall -y ai-slop-gate || true

# Install project
RUN pip install --no-cache-dir -e .

# ----------------------------
# Entrypoint
# ----------------------------
ENTRYPOINT ["ai-slop-gate"]
CMD ["--help"]

# ----------------------------
# Healthcheck
# ----------------------------
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import ai_slop_gate; print('OK')" || exit 1
