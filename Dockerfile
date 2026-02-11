# ============================
# Stage 1 — Python dependencies
# ============================
FROM python:3.12-slim AS python-builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev
COPY requirements.txt .
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
ENV PYTHONPATH="/usr/local/lib/python3.12/site-packages"

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# Install Python dependencies and Node.js from the previous stages
COPY --from=python-builder /install /usr/local
COPY --from=node-binaries /usr/local/bin/node /usr/local/bin/node
COPY --from=node-binaries /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Copying the project files. Make sure to include all necessary files for the application to run, such as the main package directory, pyproject.toml, and any configuration files.
COPY ai_slop_gate/ ./ai_slop_gate/
COPY pyproject.toml .
COPY policy.yml .

# Check that prompt files are present in the image (for debugging purposes)
RUN echo "Checking for prompt files:" && find ai_slop_gate -name "*.prompt"

# Install the package. This will also install the dependencies from requirements.txt, as they are specified in pyproject.toml
RUN pip install --no-cache-dir .

RUN apt-get purge -y --auto-remove && apt-get clean

ENTRYPOINT ["ai-slop-gate"]
CMD ["--help"]

# Healthcheck to ensure the container is running and can import the necessary modules
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import ai_slop_gate; import github; print('OK')" || exit 1