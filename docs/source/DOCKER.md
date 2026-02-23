# 🐳 Docker Guide for ai-slop-gate

This guide covers all Docker-related operations for ai-slop-gate.

---

## 📦 Quick Start

### Pull Pre-built Image

```bash
docker pull ghcr.io/sergudo/ai-slop-gate:latest
```

### Run Static Analysis

```bash
docker run --rm -v $(pwd):/src \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --policy /src/policy.yml --path /src
```

> **Note:** `--policy` is required. The gate looks for `policy.yml` in the mounted directory
> (`/src/policy.yml`) automatically when `--policy` points to it. If the scanned repository
> has its own `policy.yml`, it will be used — no extra flags needed beyond `--path`.

---

## 🛠️ Build Locally

```bash
docker build -t ai-slop-gate .

docker run --rm \
  -v $(pwd):/src \
  ai-slop-gate \
  run --provider static --policy /src/policy.yml --path /src
```

---

## 🔧 Docker Arguments Explained

```bash
docker run --rm \
  -v $(pwd):/src \                # Mount your project to /src inside the container
  -e GROQ_API_KEY=$SLOPE_GATE_GROQ \ # Pass API keys as environment variables
  ghcr.io/sergudo/ai-slop-gate:latest \
  run \
    --provider groq \
    --llm-local \
    --policy /src/policy.yml \    # Required — must contain include_paths for LLM providers
    --path /src \
    --enforcement advisory        # advisory | blocking | never
```

**Key arguments:**

| Argument | Description |
|---|---|
| `--rm` | Remove container after run |
| `-v $(pwd):/src` | Mount your project directory |
| `-e VAR=value` | Pass environment variables (API keys, tokens) |
| `--policy /src/policy.yml` | **Required.** Policy file inside the container |
| `--path /src` | Directory to analyse inside the container |
| `--enforcement advisory` | Override enforcement level (never blocks CI when advisory) |

---

## ⚠️ Policy and include_paths Are Required for LLM Providers

When using LLM providers (`groq`, `gemini`, `ollama`) in local mode (`--llm-local`),
the `policy.yml` **must** define `include_paths`. Without it, the tool aborts with:

```
❌ ABORTED: LLM providers ['groq'] require 'include_paths' to be set in policy.yml.
   Without include_paths, the ENTIRE repository is sent to the API.
```

**Minimal `policy.yml` for the scanned repo:**

```yaml
version: "v1.4"
enforcement: advisory

include_paths:
  - src   # only this directory is sent to the LLM

ai_provider:
  name: groq
  models:
    groq: llama-3.3-70b-versatile
```

Place this file in the repository root. The gate discovers it automatically via `--path /src`.

---

## 💾 Persistent Cache with Docker

Cache LLM responses between runs to save tokens and time:

```bash
docker run --rm \
  -v $(pwd):/src \
  -v $HOME/.ai-slop-cache:/app/.ai-slop-cache \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider groq --llm-local --policy /src/policy.yml --path /src
```

| Run type | Time | API calls |
|---|---|---|
| First run | ~15s | Yes |
| Cached run | ~0.5s | No |
| Savings | — | ~67% of tokens |

### Clear Docker Cache

```bash
rm -rf $HOME/.ai-slop-cache/
```

---

## 🏠 Local LLM with Docker & Ollama

### Using Docker Compose

```bash
# Start the stack (ai-slop-gate + Ollama)
docker-compose up -d

# Run analysis
docker-compose run --rm gate \
  python -m ai_slop_gate.cli run \
    --provider ollama \
    --llm-local \
    --policy /workspace/policy.yml \
    --path /workspace
```

### Manual Ollama Setup

```bash
docker run --rm \
  -v $(pwd):/src \
  --network host \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider ollama --llm-local --policy /src/policy.yml --path /src
```

**Benefits of Local LLM:**
- ✅ 100% data privacy — code never leaves your infrastructure
- ✅ Zero API costs
- ✅ GDPR compliant
- ✅ Works offline

---

## 🔗 Docker in CI/CD

### GitHub Actions

```yaml
name: AI Slop Gate
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Cache AI Slop responses
        uses: actions/cache@v3
        with:
          path: .ai-slop-cache
          key: ai-slop-cache-${{ hashFiles('**/*.py', '**/*.js') }}
          restore-keys: ai-slop-cache-

      # Static analysis — never blocks CI (advisory)
      - name: Static Analysis
        run: |
          docker run --rm \
            -v $(pwd):/src \
            -v $(pwd)/.ai-slop-cache:/app/.ai-slop-cache \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run --provider static \
                --policy /src/policy.yml \
                --path /src \
                --enforcement advisory

      # LLM analysis — requires include_paths in policy.yml
      - name: LLM Analysis
        run: |
          docker run --rm \
            -v $(pwd):/src \
            -v $(pwd)/.ai-slop-cache:/app/.ai-slop-cache \
            -e GROQ_API_KEY=${{ secrets.SLOPE_GATE_GROQ }} \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run --provider groq \
                --llm-local \
                --policy /src/policy.yml \
                --path /src \
                --enforcement advisory
```

### GitLab CI

```yaml
analyze:
  image: ghcr.io/sergudo/ai-slop-gate:latest
  variables:
    GROQ_API_KEY: $SLOPE_GATE_GROQ
  script:
    - ai-slop-gate run
        --provider static
        --policy policy.yml
        --path .
        --enforcement advisory
  cache:
    paths:
      - .ai-slop-cache/
```

See [INTEGRATIONS.md](INTEGRATIONS.md) for complete CI/CD examples.

---

## 🔐 Security Best Practices

### 1. Pin Specific Versions

```bash
# Use specific version instead of :latest
docker pull ghcr.io/sergudo/ai-slop-gate:v1.2.3
```

### 2. Use Signed Images

```bash
cosign verify ghcr.io/sergudo/ai-slop-gate:latest
```

### 3. Scan Images Before Use

```bash
trivy image ghcr.io/sergudo/ai-slop-gate:latest
```

### 4. Use Read-Only Mounts

```bash
docker run --rm \
  -v $(pwd):/src:ro \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --policy /src/policy.yml --path /src
```

### 5. Never Pass API Keys via CLI Flags

```bash
# ✅ GOOD — key not in command history
-e SLOPE_GATE_GROQ=$SLOPE_GATE_GROQ

# ❌ BAD — key visible in shell history and docker inspect
run --groq-key "gsk_xxxx"
```

---

## 🧪 Docker Testing

### Test Static Analysis

```bash
docker run --rm \
  -v $(pwd):/src \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --policy /src/policy.yml --path /src --verbose
```

### Test with Demo Repository

The demo repository includes its own `policy.yml` with `include_paths` configured:

```bash
git clone https://github.com/SergUdo/slop_test

docker run --rm \
  -v $(pwd)/slop_test:/src \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --policy /src/policy.yml --path /src
```

---

## 🐛 Troubleshooting

### "policy.yml is required"

Every `run` command requires `--policy`. Pass the path to `policy.yml` inside the container:

```bash
docker run --rm -v $(pwd):/src ... \
  run --provider static --policy /src/policy.yml --path /src
```

### "LLM providers require include_paths"

Your `policy.yml` is missing `include_paths`. Add it:

```yaml
include_paths:
  - src
```

Without `include_paths`, the LLM would receive every file in the repository and exceed token limits.

### "Permission denied"

```bash
# Linux/macOS — ensure write access for cache
docker run --rm -v $(pwd):/src:rw ...

# Windows (PowerShell)
docker run --rm -v ${PWD}:/src ...
```

### "Cache not persisting"

Mount the cache directory explicitly:

```bash
docker run --rm \
  -v $HOME/.ai-slop-cache:/app/.ai-slop-cache \
  ...
```

### "Cannot connect to Ollama"

```bash
docker run --rm --network host ...
```

Or use Docker Compose with proper service networking.

### "API key not found"

```bash
docker run --rm \
  -e GROQ_API_KEY="your-key" \
  -e GEMINI_API_KEY="your-key" \
  ...
```

---

## 📊 Docker Image Details

- **Base Image:** Python 3.12-slim
- **Size:** ~300MB compressed
- **Platforms:** linux/amd64, linux/arm64
- **Registry:** GitHub Container Registry (GHCR)
- **Verification:** Signed with Cosign

### Image Tags

| Tag | Description |
|---|---|
| `latest` | Latest stable release |
| `v1.x.x` | Specific pinned version (recommended for production) |
| `develop` | Development branch (unstable) |

---

## 🔗 Related Documentation

- [CLI Reference](CLI_REFERENCE.md) — All flags and options
- [Cache Guide](CACHE.md) — Cache management
- [Integrations](INTEGRATIONS.md) — CI/CD setup guides
- [Security Policy](../docs/source/SECURITY.md) — Security best practices
