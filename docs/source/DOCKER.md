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
docker run --rm -v $(pwd):/src ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --policy /src/policy.yml --path /src
```

---

## 🛠️ Build Locally

### Build the Image

```bash
docker build -t ai-slop-gate .
```

### Run Local Image

```bash
docker run --rm \
  -v $(pwd):/data \
  ai-slop-gate \
  run --provider static --policy /data/policy.yml --path /data
```

---

## 🔧 Docker Arguments Explained

```bash
docker run --rm \
  -v $(pwd):/src \              # Mount current directory to /src
  -e GEMINI_API_KEY=$API_KEY \  # Pass environment variables
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider gemini --policy /src/policy.yml --path /src
```

**Key arguments:**
- `--rm` — Automatically remove container after run
- `-v $(pwd):/src` — Mount your code directory
- `-e VAR=value` — Set environment variables
- `--policy /src/policy.yml` — Path to policy inside container
- `--path /src` — Directory to analyze inside container

---

## 💾 Persistent Cache with Docker

To persist LLM cache between runs:

```bash
docker run --rm \
  -v $(pwd):/src \
  -v $HOME/.ai-slop-cache:/app/.ai-slop-cache \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider gemini --llm-local --path /src
```

**Cache benefits:**
- First run: ~15s, calls API
- Cached runs: ~0.5s, no API calls
- Saves ~67% of tokens!

### Clear Docker Cache

```bash
docker run --rm \
  -v $HOME/.ai-slop-cache:/app/.ai-slop-cache \
  ghcr.io/sergudo/ai-slop-gate:latest \
  clear-cache
```

Or manually:

```bash
rm -rf $HOME/.ai-slop-cache/
```

---

## 🏠 Local LLM with Docker & Ollama

### Using Docker Compose

The easiest way to run with local LLMs:

```bash
# Start the stack (ai-slop-gate + Ollama)
docker-compose up -d

# Run analysis
docker-compose run --rm gate \
  python -m ai_slop_gate.cli run \
  --provider ollama \
  --llm-local \
  --path /workspace
```

### Manual Ollama Setup

If you have Ollama running separately:

```bash
docker run --rm \
  -v $(pwd):/src \
  --network host \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider ollama --llm-local --path /src
```

**Benefits of Local LLM:**
- ✅ 100% data privacy (code never leaves your infrastructure)
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
      - uses: actions/checkout@v3
      
      - name: Cache AI Slop responses
        uses: actions/cache@v3
        with:
          path: .ai-slop-cache
          key: ai-slop-cache-${{ hashFiles('**/*.py') }}
      
      - name: Run AI Slop Gate
        run: |
          docker run --rm \
            -v $(pwd):/src \
            -v $(pwd)/.ai-slop-cache:/app/.ai-slop-cache \
            -e GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }} \
            ghcr.io/sergudo/ai-slop-gate:latest \
            run --provider gemini --llm-local --path /src
```

### GitLab CI

```yaml
analyze:
  image: ghcr.io/sergudo/ai-slop-gate:latest
  script:
    - ai-slop-gate run --provider static --path .
  cache:
    paths:
      - .ai-slop-cache/
```

See [INTEGRATIONS.md](INTEGRATIONS.md) for complete CI/CD examples.

---

## 🔐 Security Best Practices

### 1. Use Signed Images

Always verify image signatures:

```bash
# Images are signed with Cosign
cosign verify ghcr.io/sergudo/ai-slop-gate:latest
```

### 2. Pin Specific Versions

```bash
# Instead of :latest, use specific version
docker pull ghcr.io/sergudo/ai-slop-gate:v1.2.3
```

### 3. Scan Images

```bash
# Scan for vulnerabilities before use
docker scan ghcr.io/sergudo/ai-slop-gate:latest
```

### 4. Use Read-Only Mounts

```bash
docker run --rm \
  -v $(pwd):/src:ro \  # Read-only mount
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --path /src
```

---

## 🧪 Docker Testing

### Test Static Analysis

```bash
docker run --rm \
  -v $(pwd):/src \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --path /src --verbose
```

### Test with Demo Repository

```bash
git clone https://github.com/SergUdo/slop_test
docker run --rm \
  -v $(pwd)/slop_test:/src \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider static --path /src
```

---

## 🐛 Troubleshooting

### Issue: "Permission denied"

**Solution:** Ensure correct volume permissions:

```bash
# Linux/macOS
docker run --rm -v $(pwd):/src:rw ...

# Windows (PowerShell)
docker run --rm -v ${PWD}:/src ...
```

### Issue: "Cache not persisting"

**Solution:** Mount cache directory:

```bash
docker run --rm \
  -v $HOME/.ai-slop-cache:/app/.ai-slop-cache \
  ...
```

### Issue: "Cannot connect to Ollama"

**Solution:** Use host network:

```bash
docker run --rm --network host ...
```

Or use Docker Compose with proper networking.

### Issue: "API key not found"

**Solution:** Pass environment variables explicitly:

```bash
docker run --rm \
  -e GEMINI_API_KEY="your-key-here" \
  ...
```

---

## 📊 Docker Image Details

- **Base Image:** Python 3.11-slim
- **Size:** ~300MB (compressed)
- **Platforms:** linux/amd64, linux/arm64
- **Registry:** GitHub Container Registry (GHCR)
- **Verification:** Signed with Cosign

### Image Tags

- `latest` — Latest stable release
- `v1.2.3` — Specific version
- `develop` — Development branch (unstable)

---

## 🔗 Related Documentation

- [Cache Guide](CACHE.md) — Detailed cache configuration
- [CLI Reference](CLI_REFERENCE.md) — Complete CLI documentation
- [Integrations](INTEGRATIONS.md) — CI/CD setup guides
- [Security Policy](../docs/source/SECURITY.md) — Security best practices

---

## 💬 Support

If you encounter issues with Docker:

1. Check [GitHub Issues](https://github.com/SergUdo/ai-slop-gate/issues)
2. Review [Discussions](https://github.com/SergUdo/ai-slop-gate/discussions)
3. Open a new issue with Docker logs and your command