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

Initialize a default `policy.yml` in the current directory.

```bash
python -m ai_slop_gate.cli init [--force]
```

**Options:**
- `--force` — Overwrite existing `policy.yml`

**Examples:**
```bash
python -m ai_slop_gate.cli init
python -m ai_slop_gate.cli init --force
```

---

### `run`

Run code analysis.

```bash
python -m ai_slop_gate.cli run [options]
```

---

## Core Options

### `--policy <path>` ⚠️ Required

Path to `policy.yml`.

**Why it matters:** `policy.yml` defines `include_paths` — without it, every file in the repository
is sent to the LLM provider, which hits token limits and generates noise from docs, lock files,
and other non-code content. Always provide a policy.

**Discovery order** (when `--policy` is omitted — not recommended):

1. `<--path>/policy.yml` — policy inside the repository being analysed
2. `./policy.yml` — current working directory
3. Bundled package default (very permissive, no `include_paths`)

**Best practice:** every repository you scan should have its own minimal `policy.yml`
(see [Minimal policy for a target repository](#minimal-policy-for-a-target-repository)).

**Examples:**
```bash
# Explicit policy (recommended)
python -m ai_slop_gate.cli run --provider static --policy policy.yml

# Policy from the target repo (auto-discovery, requires policy.yml in --path)
python -m ai_slop_gate.cli run --provider static --path /path/to/project

# Strict production policy
python -m ai_slop_gate.cli run --provider static --policy policies/prod-strict.yml
```

---

### `--provider <name> [<name> ...]`

Specify which provider(s) to run.

**Available providers:**

| Provider | Requires API key | Description |
|---|---|---|
| `static` / `static_pipeline` | No | Fast deterministic static analysis |
| `gemini` | `GEMINI_API_KEY` | Google Gemini LLM |
| `groq` | `SLOPE_GATE_GROQ` | Groq LLM (Llama 3.3) |
| `ollama` | No (local) | Local Ollama LLM |

**Examples:**
```bash
# Single provider
python -m ai_slop_gate.cli run --provider static --policy policy.yml

# Multiple providers
python -m ai_slop_gate.cli run --provider static gemini --policy policy.yml

# LLM + local files
python -m ai_slop_gate.cli run --provider groq --llm-local --policy policy.yml
```

---

### `--path <path>`

Project directory to analyse.

**Default:** `.` (current directory)

**Note:** `include_paths` in `policy.yml` are resolved relative to `--path`.
Scoping `--path` to your source directory alone is not sufficient — always use
`include_paths` in `policy.yml` to restrict what providers see.

**Examples:**
```bash
python -m ai_slop_gate.cli run --provider static --policy policy.yml
python -m ai_slop_gate.cli run --provider static --path /path/to/project --policy policy.yml
```

---

### `--enforcement <mode>`

Override the enforcement level set in `policy.yml`.

| Mode | Behaviour |
|---|---|
| `blocking` | CI fails on violations (default from policy) |
| `advisory` | Findings are reported, CI never blocked |
| `never` | Report only — exit code always 0 |

**Use `advisory` or `never` when:**
- Introducing the gate to an existing project (clearing baseline noise first)
- Running analysis steps that should never break the build independently

**Examples:**
```bash
# Warn but don't block CI
python -m ai_slop_gate.cli run --provider static --enforcement advisory --policy policy.yml

# Full blocking mode
python -m ai_slop_gate.cli run --provider static --enforcement blocking --policy policy.yml
```

---

## LLM Options

### `--llm-local`

Scan local files with the LLM provider instead of a PR diff.

**Requires:** `--policy` with `include_paths` configured — otherwise the LLM receives the entire
repository and will exceed token limits.

**Excluded automatically by `llm_provider.py`** (regardless of policy):
- `.env`, `.env.*`, `.env.example`
- `policy.yml`
- `docs/`, `scripts/`, `.ai-slop-cache/`
- Lock files (`package-lock.json`, `poetry.lock`, etc.)
- Minified bundles (`*.min.js`)

**Examples:**
```bash
python -m ai_slop_gate.cli run --provider groq --llm-local --policy policy.yml
python -m ai_slop_gate.cli run --provider ollama --llm-local --path ./src --policy policy.yml
```

---

### `--cache-dir <path>`

Cache directory for LLM responses.

**Default:** `.ai-slop-cache`

```bash
python -m ai_slop_gate.cli run --provider gemini --llm-local --cache-dir /tmp/cache --policy policy.yml
```

---

### `--no-cache`

Disable LLM response caching (always call API).

**Warning:** Increases API costs significantly.

```bash
python -m ai_slop_gate.cli run --provider gemini --llm-local --no-cache --policy policy.yml
```

---

## Compliance Options

### `--compliance`

Run compliance checks in addition to provider analysis.

**Checks:** GDPR/DSGVO, license violations (GPL, AGPL), secret detection, PII detection.

```bash
python -m ai_slop_gate.cli run --provider static --compliance --policy policy.yml
```

---

### `--compliance-only`

Run ONLY compliance checks, skip all LLM and static providers.

```bash
python -m ai_slop_gate.cli run --compliance-only --policy policy.yml
```

---

## Output

### `--verbose`

Show detailed diagnostic output: cache hits/misses, per-file progress, triggered rules.

```bash
python -m ai_slop_gate.cli run --provider gemini --llm-local --verbose --policy policy.yml
```

---

## GitHub Integration

All three flags are required together to post PR comments or create GitHub Checks.

### `--github-repo <owner/repo>` + `--pr-id <number>` + `--github-token <token>`

Post analysis results as a PR comment.

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

python -m ai_slop_gate.cli run \
  --provider groq \
  --github-repo owner/repo \
  --pr-id 123 \
  --policy policy.yml
```

---

### `--github-sha <sha>`

Publish results as a GitHub Checks annotation (for push events).
Used together with `--github-repo` and `--github-token`.

```bash
python -m ai_slop_gate.cli run \
  --provider static \
  --github-repo owner/repo \
  --github-sha abc123def456 \
  --policy policy.yml
```

---

### `--github-token <token>`

GitHub API token. Prefer `GITHUB_TOKEN` environment variable over passing via CLI flag
(CLI flags appear in shell history).

```bash
# Recommended
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
python -m ai_slop_gate.cli run --github-repo owner/repo --pr-id 123 --policy policy.yml
```

---

## GitLab Integration

### `--gitlab-project <path>` + `--mr-iid <number>` + `--gitlab-token <token>`

Post analysis results as a Merge Request comment.

```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"

python -m ai_slop_gate.cli run \
  --provider groq \
  --gitlab-project user/repo \
  --mr-iid 42 \
  --policy policy.yml
```

---

### `--gitlab-url <url>`

GitLab instance URL.

**Default:** `https://gitlab.com`

```bash
python -m ai_slop_gate.cli run \
  --provider static \
  --gitlab-project user/repo \
  --mr-iid 1 \
  --gitlab-url https://gitlab.company.com \
  --policy policy.yml
```

---

## Minimal Policy for a Target Repository

Place this `policy.yml` in the root of the repository you want to scan.
The gate will automatically use it (discovery order: target repo → cwd → bundled default).

```yaml
# policy.yml — minimal override for target repository
version: "v1.4"
project_name: "my-project"

enforcement: advisory   # start with advisory, switch to blocking after tuning

# REQUIRED: limits what providers see. Without this, LLMs hit token limits.
include_paths:
  - src    # adjust to your source directory

ai_provider:
  name: groq
  models:
    groq: llama-3.3-70b-versatile

compliance:
  enabled: false

rules:
  - id: block-hardcoded-secrets
    when:
      signal: "hardcoded_.*"
    then:
      action: blocking
      message: "Hardcoded secret detected."

  - id: advisory-quality
    when:
      category: quality
      severity: medium
    then:
      action: advisory
      message: "Code quality issue detected."
```

---

## Environment Variables

### LLM API Keys

```bash
export GEMINI_API_KEY="your-gemini-key"
export SLOPE_GATE_GROQ="your-groq-key"
```

### GitHub / GitLab Tokens

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
```

---

## Complete Examples

### Static Analysis (local project)

```bash
python -m ai_slop_gate.cli run \
  --provider static \
  --policy policy.yml
```

---

### LLM Analysis on Local Files

```bash
export SLOPE_GATE_GROQ="your-key"

python -m ai_slop_gate.cli run \
  --provider groq \
  --llm-local \
  --policy policy.yml
```

---

### Static + LLM Combined

```bash
python -m ai_slop_gate.cli run \
  --provider static groq \
  --llm-local \
  --policy policy.yml
```

---

### Compliance Only

```bash
python -m ai_slop_gate.cli run \
  --compliance-only \
  --policy policy.yml
```

---

### GitHub PR Analysis

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export SLOPE_GATE_GROQ="your-key"

python -m ai_slop_gate.cli run \
  --provider groq \
  --github-repo owner/repo \
  --pr-id 123 \
  --policy policy.yml
```

---

### GitLab MR Analysis

```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
export SLOPE_GATE_GROQ="your-key"

python -m ai_slop_gate.cli run \
  --provider groq \
  --gitlab-project user/repo \
  --mr-iid 42 \
  --policy policy.yml
```

---

### Local Ollama (no API key)

```bash
# Start Ollama first: ollama serve
python -m ai_slop_gate.cli run \
  --provider ollama \
  --llm-local \
  --policy policy.yml
```

---

### Advisory Mode (safe for new projects)

```bash
python -m ai_slop_gate.cli run \
  --provider static \
  --enforcement advisory \
  --policy policy.yml
```

---

### Production Strict Mode

```bash
python -m ai_slop_gate.cli run \
  --provider static groq \
  --llm-local \
  --enforcement blocking \
  --policy policies/production.yml
```

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success — no blocking violations, or `--enforcement advisory/never` |
| `1` | Blocking violations detected (`--enforcement blocking`) |

---

## Tips & Best Practices

### 1. Always provide `--policy`

Without `policy.yml` and `include_paths`, LLM providers receive the entire repository
and will exceed token limits on any non-trivial project.

```bash
# ✅ GOOD
python -m ai_slop_gate.cli run --provider groq --llm-local --policy policy.yml

# ❌ BAD — sends everything to the LLM
python -m ai_slop_gate.cli run --provider groq --llm-local
```

### 2. Start with `advisory`, then tighten

```bash
# Step 1: understand findings
python -m ai_slop_gate.cli run --provider static --enforcement advisory --policy policy.yml

# Step 2: block on violations once baseline is clear
python -m ai_slop_gate.cli run --provider static --enforcement blocking --policy policy.yml
```

### 3. Use environment variables for tokens

```bash
# ✅ GOOD — token not in shell history
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
python -m ai_slop_gate.cli run --github-repo owner/repo --pr-id 123 --policy policy.yml

# ❌ BAD — visible in shell history
python -m ai_slop_gate.cli run --github-token "ghp_xxxxxxxxxxxx" ...
```

### 4. Use cache for LLM in CI

LLM calls are expensive. Cache is enabled by default and reduces costs on repeat runs
(e.g. when only one file changed).

```bash
# ✅ Cache enabled (default)
python -m ai_slop_gate.cli run --provider groq --llm-local --policy policy.yml

# Use --no-cache only when debugging prompt changes
python -m ai_slop_gate.cli run --provider groq --llm-local --no-cache --verbose --policy policy.yml
```

---

## Troubleshooting

### "LLM provider skipped: no PR context and --llm-local not set"

Add `--llm-local` to analyse files on disk, or pass `--github-repo` + `--pr-id` for PR diff mode.

### "Token limit exceeded"

Add or tighten `include_paths` in `policy.yml` to limit which directories are sent to the LLM.

### "No policy.yml found"

Run `python -m ai_slop_gate.cli init` to create a default policy, or pass `--policy <path>` explicitly.

### "Trivy / Syft binary not found"

Install the required tools before running static analysis in CI:

```bash
# Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
  | sh -s -- -b /usr/local/bin v0.50.4

# Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh \
  | sh -s -- -b /usr/local/bin
```

---

## Related Documentation

- [Cache Guide](CACHE.md)
- [Policy Configuration](../docs/source/policy-configuration.md)
- [Integrations](INTEGRATIONS.md)
