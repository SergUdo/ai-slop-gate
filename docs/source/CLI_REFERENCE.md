# 🔧 CLI Reference

Complete command-line reference for ai-slop-gate.

---

## Basic Usage

```bash
python -m ai_slop_gate.cli <command> [options]
```

---

## Commands

### `init`

Initialize configuration file.

```bash
python -m ai_slop_gate.cli init [--force]
```

**Options:**
- `--force` — Overwrite existing `.ai-slop-gate.yml`

**Example:**
```bash
python -m ai_slop_gate.cli init
python -m ai_slop_gate.cli init --force  # Overwrite existing config
```

---

### `run`

Run code analysis.

```bash
python -m ai_slop_gate.cli run [options]
```

---

## Core Options

### `--provider <name> [<name> ...]`

Specify which provider(s) to use.

**Available providers:**
- `static` — Fast static analysis (no API key required)
- `gemini` — Google Gemini LLM
- `groq` — Groq LLM (Llama 3.3)
- `ollama` — Local Ollama LLM
- `compliance` — Compliance checks (GDPR, licenses, etc.)

**Examples:**
```bash
# Single provider
python -m ai_slop_gate.cli run --provider static

# Multiple providers
python -m ai_slop_gate.cli run --provider static gemini

# All providers
python -m ai_slop_gate.cli run --provider static gemini groq ollama
```

---

### `--policy <path>`

Path to policy configuration file.

**Default:** `policy.yml`

**Examples:**
```bash
# Use default policy
python -m ai_slop_gate.cli run --provider static

# Custom policy
python -m ai_slop_gate.cli run --provider static --policy custom-policy.yml

# Strict production policy
python -m ai_slop_gate.cli run --provider static --policy policies/prod-strict.yml
```

---

### `--path <path>`

Project directory to analyze.

**Default:** Current directory (`.`)

**Examples:**
```bash
# Analyze current directory
python -m ai_slop_gate.cli run --provider static

# Analyze specific project
python -m ai_slop_gate.cli run --provider static --path /path/to/project

# Analyze subdirectory
python -m ai_slop_gate.cli run --provider static --path ./src
```

---

## LLM Options

### `--llm-local`

Run LLM analysis on local files (full repository).

**Usage:**
```bash
python -m ai_slop_gate.cli run --provider gemini --llm-local
```

**Notes:**
- Analyzes entire repository
- Requires API key for cloud providers (Gemini, Groq)
- No API key needed for Ollama (local)
- Automatically uses cache to save tokens

---

### `--cache-dir <path>`

Specify cache directory for LLM responses.

**Default:** `.ai-slop-cache`

**Examples:**
```bash
# Default cache location
python -m ai_slop_gate.cli run --provider gemini --llm-local

# Custom cache directory
python -m ai_slop_gate.cli run --provider gemini --llm-local --cache-dir /tmp/cache

# User-specific cache
python -m ai_slop_gate.cli run --provider gemini --llm-local --cache-dir $HOME/.ai-cache
```

---

### `--no-cache`

Disable LLM response caching (always call API).

**Usage:**
```bash
python -m ai_slop_gate.cli run --provider gemini --llm-local --no-cache
```

**Use when:**
- Testing prompt changes
- Debugging LLM responses
- Forcing fresh analysis

**Warning:** Disabling cache increases API costs!

---

## GitHub Integration

### `--github-repo <owner/repo>`

Enable GitHub integration.

**Format:** `owner/repository`

**Example:**
```bash
python -m ai_slop_gate.cli run \
  --provider gemini \
  --github-repo SergUdo/ai-slop-gate \
  --pr-id 123
```

---

### `--pr-id <number>`

Analyze specific GitHub Pull Request (diff-only mode).

**Required:** `--github-repo`

**Example:**
```bash
python -m ai_slop_gate.cli run \
  --provider gemini \
  --github-repo SergUdo/ai-slop-gate \
  --pr-id 123 \
  --github-token "$GITHUB_TOKEN"
```

**Notes:**
- Only analyzes PR diff (changed files)
- Posts comments directly to PR
- Requires GitHub token with PR permissions

---

### `--github-sha <sha>`

Report results as GitHub Checks for specific commit.

**Example:**
```bash
python -m ai_slop_gate.cli run \
  --provider static \
  --github-repo SergUdo/ai-slop-gate \
  --github-sha abc123def456
```

---

### `--github-token <token>`

GitHub API token for authentication.

**Alternative:** Set `GITHUB_TOKEN` environment variable

**Examples:**
```bash
# Via CLI argument
python -m ai_slop_gate.cli run \
  --github-repo SergUdo/ai-slop-gate \
  --pr-id 123 \
  --github-token "ghp_xxxxxxxxxxxx"

# Via environment variable (recommended)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
python -m ai_slop_gate.cli run \
  --github-repo SergUdo/ai-slop-gate \
  --pr-id 123
```

---

## GitLab Integration

### `--gitlab-project <path>`

GitLab project identifier.

**Format:** `username/project` or `group/subgroup/project`

**Example:**
```bash
python -m ai_slop_gate.cli run \
  --provider static \
  --gitlab-project sergudo/ai-slop-gate \
  --mr-iid 42
```

---

### `--mr-iid <number>`

Merge Request internal ID (not the MR number).

**Required:** `--gitlab-project`

**Example:**
```bash
python -m ai_slop_gate.cli run \
  --provider gemini \
  --gitlab-project sergudo/ai-slop-gate \
  --mr-iid 42 \
  --gitlab-token "$GITLAB_TOKEN"
```

---

### `--gitlab-url <url>`

GitLab instance URL.

**Default:** `https://gitlab.com`

**Examples:**
```bash
# GitLab.com (default)
python -m ai_slop_gate.cli run --gitlab-project user/repo --mr-iid 1

# Self-hosted GitLab
python -m ai_slop_gate.cli run \
  --gitlab-project user/repo \
  --mr-iid 1 \
  --gitlab-url https://gitlab.company.com
```

---

### `--gitlab-token <token>`

GitLab API token.

**Alternative:** Set `GITLAB_TOKEN` environment variable

**Examples:**
```bash
# Via CLI argument
python -m ai_slop_gate.cli run \
  --gitlab-project user/repo \
  --mr-iid 1 \
  --gitlab-token "glpat-xxxxxxxxxxxx"

# Via environment variable (recommended)
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
python -m ai_slop_gate.cli run \
  --gitlab-project user/repo \
  --mr-iid 1
```

---

## Compliance Options

### `--compliance`

Run compliance checks in addition to code analysis.

**Example:**
```bash
python -m ai_slop_gate.cli run --provider static --compliance
```

**Checks:**
- GDPR/DSGVO data residency
- License compliance (GPL, AGPL detection)
- Supply chain security
- AI hallucination detection

---

### `--compliance-only`

Run ONLY compliance checks (skip code analysis).

**Example:**
```bash
python -m ai_slop_gate.cli run --compliance-only
```

**Use when:**
- Only legal/compliance review needed
- Fast compliance gate in CI/CD
- Auditing dependencies

---

## Output & Debugging

### `--verbose`

Show detailed diagnostic output.

**Example:**
```bash
python -m ai_slop_gate.cli run --provider gemini --llm-local --verbose
```

**Output includes:**
- Cache hits/misses
- API call details
- File analysis progress
- Provider execution logs

---

### `--enforcement <mode>`

Override enforcement mode from policy.

**Modes:**
- `never` — No enforcement (advisory only)
- `advisory` — Show warnings, don't block
- `blocking` — Fail build on violations

**Example:**
```bash
# Advisory mode for development
python -m ai_slop_gate.cli run --provider static --enforcement advisory

# Blocking mode for production
python -m ai_slop_gate.cli run --provider static --enforcement blocking
```

---

## Environment Variables

### LLM API Keys

```bash
export GEMINI_API_KEY="your-gemini-key"
export GROQ_API_KEY="your-groq-key"
```

### GitHub/GitLab Tokens

```bash
export GITHUB_TOKEN="ghp-xxxxxxxxxxxx"
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
```

### Custom Configuration

```bash
export AI_SLOP_GATE_CONFIG="/path/to/custom-config.yml"
export AI_SLOP_GATE_CACHE_DIR="/tmp/cache"
```

---

## Complete Examples

### Basic Static Analysis

```bash
python -m ai_slop_gate.cli run --provider static
```

---

### LLM Analysis with Cache

```bash
python -m ai_slop_gate.cli run \
  --provider gemini \
  --llm-local \
  --policy policy.yml
```

---

### Multiple Providers

```bash
python -m ai_slop_gate.cli run \
  --provider static gemini groq \
  --llm-local \
  --path /path/to/project
```

---

### Compliance Check

```bash
python -m ai_slop_gate.cli run \
  --compliance \
  --policy policy.yml
```

---

### GitHub PR Analysis

```bash
export GITHUB_TOKEN="ghp-xxxxxxxxxxxx"
export GEMINI_API_KEY="your-key"

python -m ai_slop_gate.cli run \
  --provider gemini \
  --github-repo owner/repo \
  --pr-id 123
```

---

### GitLab MR Analysis

```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
export GROQ_API_KEY="your-key"

python -m ai_slop_gate.cli run \
  --provider groq \
  --gitlab-project user/repo \
  --mr-iid 42 \
  --gitlab-url https://gitlab.company.com
```

---

### Local Ollama Analysis

```bash
python -m ai_slop_gate.cli run \
  --provider ollama \
  --llm-local \
  --path /path/to/project
```

**Note:** Requires Ollama running locally (`ollama serve`)

---

### Custom Cache Directory

```bash
python -m ai_slop_gate.cli run \
  --provider gemini \
  --llm-local \
  --cache-dir /tmp/my-cache
```

---

### Verbose Output with No Cache

```bash
python -m ai_slop_gate.cli run \
  --provider gemini \
  --llm-local \
  --no-cache \
  --verbose
```

---

### Production Mode (Strict)

```bash
python -m ai_slop_gate.cli run \
  --provider static gemini \
  --llm-local \
  --policy policies/production.yml \
  --enforcement blocking
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0`  | Success (no violations or advisory mode) |
| `1`  | Analysis failed (critical violations in blocking mode) |
| `2`  | Configuration error |
| `3`  | API error (invalid key, rate limit, etc.) |

---

## Alias & Shortcuts

### Bash Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Quick static analysis
alias asg-static='python -m ai_slop_gate.cli run --provider static'

# LLM analysis with cache
alias asg-llm='python -m ai_slop_gate.cli run --provider gemini --llm-local'

# Full analysis
alias asg-full='python -m ai_slop_gate.cli run --provider static gemini --llm-local'

# Compliance check
alias asg-comply='python -m ai_slop_gate.cli run --compliance'
```

---

## Tips & Best Practices

### 1. Always Use Cache for LLM

```bash
# ✅ GOOD: Uses cache (default)
python -m ai_slop_gate.cli run --provider gemini --llm-local

# ❌ BAD: Wastes tokens
python -m ai_slop_gate.cli run --provider gemini --llm-local --no-cache
```

---

### 2. Combine Static + LLM

```bash
# Fast static check + smart LLM analysis
python -m ai_slop_gate.cli run --provider static gemini --llm-local
```

---

### 3. Use Environment Variables for Tokens

```bash
# ✅ GOOD: Secure, no token in command history
export GITHUB_TOKEN="ghp-xxxxxxxxxxxx"
python -m ai_slop_gate.cli run --github-repo owner/repo --pr-id 123

# ❌ BAD: Token visible in shell history
python -m ai_slop_gate.cli run --github-token "ghp-xxxxxxxxxxxx"
```

---

### 4. Start with Advisory Mode

```bash
# First time: Advisory mode
python -m ai_slop_gate.cli run --provider static --enforcement advisory

# After tuning: Blocking mode
python -m ai_slop_gate.cli run --provider static --enforcement blocking
```

---

## Troubleshooting

### "Provider skipped: insufficient context"

**Cause:** Missing API key or invalid configuration

**Solution:**
```bash
# Set API key
export GEMINI_API_KEY="your-key"

# Or use local Ollama
python -m ai_slop_gate.cli run --provider ollama --llm-local
```

---

### "Cache not working"

**Cause:** Cache disabled or wrong directory

**Solution:**
```bash
# Check verbose output
python -m ai_slop_gate.cli run --provider gemini --llm-local --verbose

# Verify cache directory
ls -la .ai-slop-cache/
```

---

### "Permission denied"

**Cause:** No write access to project directory or cache

**Solution:**
```bash
# Fix permissions
chmod -R u+rw .ai-slop-cache/

# Or use custom cache directory
python -m ai_slop_gate.cli run --cache-dir /tmp/cache
```

---

## Related Documentation

- [Cache Guide](CACHE.md) — Cache management
- [Docker Guide](DOCKER.md) — Docker usage
- [Integrations](INTEGRATIONS.md) — CI/CD setup
- [Policy Configuration](../docs/source/policy-configuration.md) — Policy settings

---

## Support

For CLI issues:
1. Check [GitHub Issues](https://github.com/SergUdo/ai-slop-gate/issues)
2. Review [Discussions](https://github.com/SergUdo/ai-slop-gate/discussions)
3. Read [Full Documentation](https://ai-slop-gate.readthedocs.io/)