# Cache Integration Guide

## Overview

AI Slop Gate includes an intelligent caching system that saves LLM API responses to disk, dramatically reducing costs and improving performance for repeated analyses.

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

↓ SHA256 hash ↓

Key: "a3f2e1d4c5b6..." (64 characters)
```

**Important:** Changing ANY parameter creates a new cache key:
- Different code → new key
- Different policy → new key
- Different model → new key
- Different provider → new key

---

## Configuration

### Default Settings

Cache is **enabled by default** for all LLM providers:

```bash
# Cache enabled automatically
python -m ai_slop_gate.cli.main run --provider gemini --llm-local
```

### Custom Cache Directory

Specify a custom location:

```bash
python -m ai_slop_gate.cli.main run \
  --provider gemini \
  --llm-local \
  --cache-dir /tmp/my-cache
```

### Disable Cache

Force fresh API calls every time:

```bash
python -m ai_slop_gate.cli.main run \
  --provider gemini \
  --llm-local \
  --no-cache
```

### Cache Location

Default: `.ai-slop-cache/` in current directory

```bash
$ ls -lh .ai-slop-cache/
-rw-r--r-- 1 user user 2.3K Feb 16 10:30 a3f2e1d4c5b6...json
-rw-r--r-- 1 user user 1.8K Feb 16 10:32 b7e8f9a1c2d3...json
```

---

## Usage Examples

### Example 1: First-time Analysis (Cache Miss)

```bash
$ time python -m ai_slop_gate.cli.main run \
    --provider gemini \
    --llm-local \
    --path ./my-project

# Output:
Cache enabled: True (dir=.ai-slop-cache)
🗄️  Wrapping 'gemini' with cache (dir=.ai-slop-cache)
→ Running provider: gemini (llm)
✓ gemini: collected 5 observations

real    0m15.234s  # Calls API
```

Cache file created:
```bash
$ ls .ai-slop-cache/
a3f2e1d4c5b6a7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2.json
```

### Example 2: Repeated Analysis (Cache Hit)

```bash
$ time python -m ai_slop_gate.cli.main run \
    --provider gemini \
    --llm-local \
    --path ./my-project

# Output:
Cache enabled: True (dir=.ai-slop-cache)
🗄️  Wrapping 'gemini' with cache (dir=.ai-slop-cache)
→ Running provider: gemini (llm)
✓ gemini: collected 5 observations

real    0m0.543s  # From cache! 🚀
```

**Result:** 96% faster, 0 API calls, 0 tokens spent!

### Example 3: Modified Code (Cache Miss)

```bash
# Edit a file
echo "# new code" >> my-project/main.py

$ python -m ai_slop_gate.cli.main run \
    --provider gemini \
    --llm-local \
    --path ./my-project

# Output:
→ Running provider: gemini (llm)
✓ gemini: collected 6 observations  # New result

# New cache file created (different content hash)
$ ls .ai-slop-cache/
a3f2e1d4c5b6...json  # Old cache
d7e8f9a0b1c2...json  # New cache (modified code)
```

---

## CI/CD Integration

### GitHub Actions

Cache `.ai-slop-cache/` between workflow runs:

```yaml
name: AI Slop Gate

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Cache LLM responses
      - name: Cache AI Slop Gate
        uses: actions/cache@v3
        with:
          path: .ai-slop-cache
          key: ai-slop-cache-${{ hashFiles('**/*.py', 'policy.yml') }}
          restore-keys: |
            ai-slop-cache-
      
      - name: Run Analysis
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python -m ai_slop_gate.cli.main run \
            --provider gemini \
            --llm-local \
            --path .
```

**Benefits:**
- First PR run: calls API (15s, uses tokens)
- Subsequent runs with same code: uses cache (0.5s, no tokens)
- Cache invalidates automatically when code changes

### GitLab CI

```yaml
ai-slop-gate:
  cache:
    key: ai-slop-cache-${CI_COMMIT_REF_SLUG}
    paths:
      - .ai-slop-cache/
  
  script:
    - python -m ai_slop_gate.cli.main run
        --provider gemini
        --llm-local
        --path .
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

Check cache effectiveness:

```bash
# Count cache files
echo "Total cache entries: $(find .ai-slop-cache/ -name '*.json' | wc -l)"

# Cache size
echo "Cache size: $(du -sh .ai-slop-cache/ | cut -f1)"

# Last modified
ls -lt .ai-slop-cache/ | head -5
```

---

## Performance Metrics

### Typical Performance

| Scenario | Time | Tokens | Cost* |
|----------|------|--------|-------|
| First run (cache miss) | 15s | 50,000 | $0.025 |
| Repeated run (cache hit) | 0.5s | 0 | $0.00 |
| Modified code (cache miss) | 15s | 50,000 | $0.025 |

*Based on Gemini Flash pricing ($0.50/1M tokens)

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

**Savings: 87% time, 90% cost** 🚀

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

class RedisCacheBackend(CacheBackend):
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get(self, key: str):
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    def set(self, key: str, value: Any):
        self.redis.set(key, json.dumps(value))

# Use it
from ai_slop_gate.providers.cached_provider import CachedProvider
import redis

redis_client = redis.Redis(host='localhost', port=6379)
cache = RedisCacheBackend(redis_client)
cached_provider = CachedProvider(provider=provider, cache=cache)
```

---

## Troubleshooting

### Cache Not Created

**Problem:** No `.ai-slop-cache/` directory after running

**Possible causes:**
1. Using static provider (doesn't use cache)
   ```bash
   # Static providers don't cache
   --provider static  # ❌ No cache
   ```

2. Missing `--llm-local` flag
   ```bash
   # LLM needs context
   --provider gemini              # ❌ Skipped
   --provider gemini --llm-local  # ✅ Works
   ```

3. Empty directory (no files to analyze)

**Solution:**
```bash
# Verify LLM provider runs
python -m ai_slop_gate.cli.main run \
  --provider gemini \
  --llm-local \
  --verbose \
  --path . 2>&1 | grep "Wrapping"

# Should see: 🗄️ Wrapping 'gemini' with cache
```

### Cache Not Used

**Problem:** Every run calls API despite cache existing

**Possible causes:**
1. `--no-cache` flag set
2. Code changed (creates new cache key)
3. Policy changed (creates new cache key)
4. Different provider/model

**Diagnosis:**
```bash
# Check cache files exist
ls .ai-slop-cache/

# Verify same code produces same key
python3 -c "
from ai_slop_gate.cache.key_builder import CacheKeyBuilder
builder = CacheKeyBuilder()

key1 = builder.build(
    provider_name='gemini',
    model='gemini-1.5-flash',
    content='test',
    policy={'rule': 'value'}
)
key2 = builder.build(
    provider_name='gemini',
    model='gemini-1.5-flash',
    content='test',
    policy={'rule': 'value'}
)

print(f'Same key: {key1 == key2}')  # Should be True
print(f'Key: {key1}')
"
```

### Cache Poisoning

**Problem:** Bad results cached, need to invalidate

**Solution:**
```bash
# Clear specific cache entry
# (requires finding the right file by timestamp)
ls -lt .ai-slop-cache/ | head -5
rm .ai-slop-cache/abc123...json

# Or clear all cache
rm -rf .ai-slop-cache/
```

---

## Best Practices

### For Open Source Projects

1. **Commit `.gitignore` entry:**
   ```gitignore
   # AI Slop Gate cache
   .ai-slop-cache/
   ```

2. **Use cache in CI/CD** (see CI/CD Integration)

3. **Document cache location** in README

4. **Use free LLM tiers** with cache:
   - Ollama (100% free, local)
   - Groq (generous free tier)
   - Gemini Flash (free quota)

### For Teams

1. **Shared cache location** (optional):
   ```bash
   # Team shared cache (e.g., NFS mount)
   --cache-dir /shared/ai-slop-cache
   ```

2. **Cache rotation policy:**
   ```bash
   # Cron job: clear cache older than 30 days
   0 2 * * * find /shared/ai-slop-cache -mtime +30 -delete
   ```

3. **Monitor cache effectiveness:**
   ```bash
   # Log cache hit rate
   grep "Cache" ci-logs.txt | grep -c "hit"
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

## Next Steps

- [Policy Configuration Guide](policy-configuration.md)
- [Contributing Guidelines](../CONTRIBUTING.md)