# Cache Integration Guide

## Overview

AI Slop Gate includes an intelligent caching system that saves LLM API responses to disk, dramatically reducing costs and improving performance for repeated analyses.

**Performance Benefits:**
- First run: ~15s (calls LLM API)
- Cached run: ~0.5s (no API call)
- Token savings: ~67% reduction

**Cost Savings:**
For a typical project analyzed 10 times:
- Without cache: 10 × $0.05 = $0.50
- With cache: 1 × $0.05 = $0.05
- **Savings: 90%**

---

## How It Works

### Cache Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User runs: python -m ai_slop_gate.cli.main run             │
│            --provider gemini --llm-local                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Generate Cache Key    │
              │ SHA256(provider +     │
              │   model + content +   │
              │   policy)             │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Check Cache           │
              │ .ai-slop-cache/       │
              │   abc123...json       │
              └───────────┬───────────┘
                          │
                 ┌────────┴────────┐
                 │                 │
            CACHE HIT         CACHE MISS
                 │                 │
                 ▼                 ▼
        ┌────────────────┐  ┌──────────────┐
        │ Return cached  │  │ Call LLM API │
        │ result (0.5s)  │  │ (15s)        │
        └────────────────┘  └──────┬───────┘
                                   │
                                   ▼
                            ┌──────────────┐
                            │ Save to cache│
                            └──────────────┘
```

### Cache Key Generation

Cache keys are deterministic SHA256 hashes based on:
- **Provider name** (gemini, groq, ollama)
- **Model** (gemini-1.5-flash, llama3, etc.)
- **Content** (code being analyzed)
- **Policy** (rules and configuration)

**Example:**
```python
# Same input always generates same key
provider: "gemini"
model: "gemini-1.5-flash"
content: "def foo(): pass"
policy: {"rule": "security"}

# SHA256 hash
Key: "a3f2e1d4c5b6..." (64 characters)
```

**Important:** Changing ANY parameter creates a new cache key:
- Different code → new key
- Different policy → new key
- Different model → new key
- Different provider → new key

---

## Quick Start

### Enable Cache (Default)

Cache is enabled by default:

```bash
python -m ai_slop_gate.cli run --provider gemini --llm-local
```

### Disable Cache

```bash
python -m ai_slop_gate.cli run --provider gemini --llm-local --no-cache
```

### Custom Cache Directory

```bash
python -m ai_slop_gate.cli run \
  --provider gemini \
  --llm-local \
  --cache-dir /tmp/my-cache
```

---

## Cache Location

### Local Development

- **Default:** `.ai-slop-cache/` in current directory
- **Custom:** `--cache-dir /path/to/cache`

```bash
$ ls -lh .ai-slop-cache/
-rw-r--r-- 1 user user 2.3K Feb 16 10:30 a3f2e1d4c5b6...json
-rw-r--r-- 1 user user 1.8K Feb 16 10:32 b7e8f9a1c2d3...json
```

### Docker

- **Internal:** `/app/.ai-slop-cache/` (deleted after container stops)
- **Persistent:** Mount with `-v $HOME/.ai-slop-cache:/app/.ai-slop-cache`

Example:

```bash
docker run --rm \
  -v $(pwd):/src \
  -v $HOME/.ai-slop-cache:/app/.ai-slop-cache \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider gemini --llm-local --path /src
```

### CI/CD

#### GitHub Actions

```yaml
- name: Cache AI Slop responses
  uses: actions/cache@v3
  with:
    path: .ai-slop-cache
    key: ai-slop-cache-${{ hashFiles('**/*.py') }}
    restore-keys: |
      ai-slop-cache-

- name: Run AI Slop Gate
  run: |
    python -m ai_slop_gate.cli run --provider gemini --llm-local
```

#### GitLab CI

```yaml
analyze:
  cache:
    key: ai-slop-cache
    paths:
      - .ai-slop-cache/
  script:
    - ai-slop-gate run --provider gemini --llm-local
```

---

## Usage Examples

### Example 1: First-time Analysis (Cache Miss)

```bash
$ time python -m ai_slop_gate.cli run \
    --provider gemini \
    --llm-local \
    --path ./my-project

# Output:
Cache enabled: True (dir=.ai-slop-cache)
Wrapping 'gemini' with cache (dir=.ai-slop-cache)
Running provider: gemini (llm)
gemini: collected 5 observations

real    0m15.234s  # Calls API
```

Cache file created:
```bash
$ ls .ai-slop-cache/
a3f2e1d4c5b6a7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2.json
```

### Example 2: Repeated Analysis (Cache Hit)

```bash
$ time python -m ai_slop_gate.cli run \
    --provider gemini \
    --llm-local \
    --path ./my-project

# Output:
Cache enabled: True (dir=.ai-slop-cache)
Wrapping 'gemini' with cache (dir=.ai-slop-cache)
Running provider: gemini (llm)
gemini: collected 5 observations

real    0m0.543s  # From cache!
```

**Result:** 96% faster, 0 API calls, 0 tokens spent!

### Example 3: Modified Code (Cache Miss)

```bash
# Edit a file
echo "# new code" >> my-project/main.py

$ python -m ai_slop_gate.cli run \
    --provider gemini \
    --llm-local \
    --path ./my-project

# Output:
Running provider: gemini (llm)
gemini: collected 6 observations  # New result

# New cache file created (different content hash)
$ ls .ai-slop-cache/
a3f2e1d4c5b6...json  # Old cache
d7e8f9a0b1c2...json  # New cache (modified code)
```

---

## Cache Management

### View Cache

```bash
# List cache files
ls -lh .ai-slop-cache/

# View cache content
cat .ai-slop-cache/a3f2e1d4c5b6...json | jq

# Check cache size
du -sh .ai-slop-cache/
```

### Clear Cache

```bash
# Clear all cache
rm -rf .ai-slop-cache/

# Clear old cache (older than 30 days)
find .ai-slop-cache/ -name "*.json" -mtime +30 -delete

# Clear specific provider cache
# (requires manual filtering by inspecting files)
```

### Cache Statistics

```bash
# Count cache files
echo "Total cache entries: $(find .ai-slop-cache/ -name '*.json' | wc -l)"

# Cache size
echo "Cache size: $(du -sh .ai-slop-cache/ | cut -f1)"

# Last modified
ls -lt .ai-slop-cache/ | head -5
```

---

## Supported Providers

| Provider | Cache Support |
|----------|---------------|
| `static` | No (already fast) |
| `gemini` | Yes |
| `groq`   | Yes |
| `ollama` | Yes |
| `compliance` | No (policy-based) |

**Note:** Static providers don't use cache because they're already fast. Only LLM providers benefit from caching.

---

## Performance Metrics

### Real-World Example

Project: 50 Python files, 5,000 lines of code

**Without cache (10 CI runs):**
- Time: 10 × 15s = 150s
- Tokens: 10 × 50,000 = 500,000
- Cost: ~$0.25

**With cache (10 CI runs, code unchanged):**
- Time: 1 × 15s + 9 × 0.5s = ~20s
- Tokens: 1 × 50,000 = 50,000
- Cost: ~$0.025

**Savings: 87% time, 90% cost**

---

## Security Notes

### DO NOT Commit Cache

Cache files may contain:
- Sensitive code snippets
- Internal logic patterns
- Security-related findings

**Always add to `.gitignore`:**

```gitignore
# AI Slop Gate cache (DO NOT COMMIT)
.ai-slop-cache/
*.ai-slop-cache/
```

### User-Specific Cache

Cache is user-specific and should **NOT** be shared:
- Different developers may have different analysis contexts
- Cache keys depend on local file paths
- Security findings should not be shared via cache

### Clean Cache Regularly

For long-running projects:

```bash
# Remove cache older than 30 days
find .ai-slop-cache -type f -mtime +30 -delete

# Or clean manually
rm -rf .ai-slop-cache/
```

---

## Troubleshooting

### Cache Not Working

**Symptoms:** Every run calls API

**Solutions:**

1. Check if cache is enabled:
```bash
python -m ai_slop_gate.cli run --provider gemini --llm-local --verbose
# Should show: "Cache enabled: True"
```

2. Verify cache directory exists:
```bash
ls -la .ai-slop-cache/
```

3. Check permissions:
```bash
chmod -R u+rw .ai-slop-cache/
```

### Cache Hits Not Detected

**Symptoms:** Cache exists but not used

**Solutions:**

1. Ensure file content hasn't changed:
```bash
# Cache key depends on file hash
git status  # Check for modifications
```

2. Verify provider matches:
```bash
# Cache is provider-specific
# gemini cache won't work for groq
```

3. Clear and rebuild cache:
```bash
rm -rf .ai-slop-cache/
python -m ai_slop_gate.cli run --provider gemini --llm-local
```

### Docker Cache Not Persisting

**Symptoms:** Cache lost between Docker runs

**Solution:** Mount cache volume:

```bash
docker run --rm \
  -v $HOME/.ai-slop-cache:/app/.ai-slop-cache \
  ghcr.io/sergudo/ai-slop-gate:latest \
  run --provider gemini --llm-local
```

### Cache Directory Too Large

**Symptoms:** `.ai-slop-cache/` exceeds 100MB

**Solutions:**

1. Clean old entries:
```bash
find .ai-slop-cache -type f -mtime +7 -delete
```

2. Use cache limits (if implemented):
```bash
ai-slop-gate run --cache-max-size 50MB
```

3. Exclude from backups:
```bash
# Add to .backupignore or exclude in backup software
.ai-slop-cache/
```

---

## Best Practices

### For Open Source Projects

**DO:**
- Enable cache for local development
- Use cache in CI/CD to save tokens
- Clear cache periodically
- Document cache usage in README

**DON'T:**
- Commit cache to git
- Share cache between users
- Use cache for sensitive projects without encryption

### For Enterprise Projects

**DO:**
- Use separate cache per environment (dev, staging, prod)
- Implement cache retention policies
- Monitor cache size and hit rates
- Encrypt cache for sensitive code

**DON'T:**
- Mix caches between projects
- Store cache on shared drives
- Disable cache without understanding impact

### For CI/CD Pipelines

**DO:**
- Persist cache between runs
- Use cache keys based on file hashes
- Monitor cache savings in metrics
- Set cache expiration (e.g., 30 days)

**DON'T:**
- Disable cache to "be safe" (wastes tokens)
- Use same cache for all branches
- Ignore cache misses in monitoring

---

## Advanced Configuration

### Python API

Use cache programmatically:

```python
from ai_slop_gate.providers.llm import GeminiProvider
from ai_slop_gate.providers.cached_provider import CachedProvider
from ai_slop_gate.cache.file_backend import FileCacheBackend

# Create provider
provider = GeminiProvider(model="gemini-1.5-flash")

# Wrap with cache
cache_backend = FileCacheBackend(root=".my-cache")
cached_provider = CachedProvider(
    provider=provider,
    cache=cache_backend
)

# Use normally - cache is transparent
result = cached_provider.collect(content="code", policy={})
```

### Custom Cache Backend

Implement your own cache (e.g., Redis):

```python
from ai_slop_gate.cache.base import CacheBackend
import json
import redis

class RedisCacheBackend(CacheBackend):
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get(self, key: str):
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    def set(self, key: str, value: Any):
        self.redis.set(key, json.dumps(value))

# Use it
redis_client = redis.Redis(host='localhost', port=6379)
cache = RedisCacheBackend(redis_client)
cached_provider = CachedProvider(provider=provider, cache=cache)
```

---

## FAQ

**Q: Does cache work with GitHub PR analysis?**  
A: Yes! PR content is hashed just like local files.

**Q: Is cache shared between different branches?**  
A: Yes, if the code is identical. Cache key doesn't include branch name.

**Q: What happens if I change policy.yml?**  
A: New cache key is generated. Old cache remains but won't be used.

**Q: Can I use cache with multiple projects?**  
A: Yes! Each project can have its own cache dir, or share one.

**Q: Does cache expire?**  
A: No automatic expiration. Clear manually or set up cron job.

**Q: Is cache thread-safe?**  
A: File-based cache uses atomic writes. Redis backend would be fully thread-safe.

**Q: What's stored in cache?**  
A: LLM responses (observations) in JSON format. No API keys or sensitive data.

---

## Related Documentation

- [CLI Reference](CLI_REFERENCE.md)
- [Docker Guide](DOCKER.md)
- [Policy Configuration](policy-configuration.md)
- [Contributing Guidelines](CONTRIBUTING.md)